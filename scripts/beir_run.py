#!/opt/homebrew/bin/uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["ir_datasets", "sentence-transformers>=3,<4", "transformers>=4.44,<4.50", "pytrec_eval", "numpy", "einops", "torch"]
#
# [[tool.uv.index]]
# name = "pytorch-cpu"
# url = "https://download.pytorch.org/whl/cpu"
# explicit = true
#
# [tool.uv.sources]
# torch = { index = "pytorch-cpu" }
# ///
"""Run the dead-retriever conditions on one BEIR test split and write metrics.

    beir_run.py --dataset beir/scifact/test --model nomic-ai/nomic-embed-text-v1.5 --out results/

Conditions: bm25_and (quoted-AND builder), bm25_or_raw (OR over every token),
bm25_or (OR over non-stopword tokens), dense, hybrid_and, hybrid_or.
Metrics: nDCG@10 and Recall@100 (pytrec_eval), mean query time, plus fusion
diagnostics for the hybrid conditions (keyword leg empty, max fused score at the
1/k ceiling, documents credited by both legs), written per query to
<out>/<tag>.perquery.jsonl and summarised in <out>/<tag>.json.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dead_retriever import (RRF_K, DenseIndex, HybridRetriever, KeywordIndex,  # noqa: E402
                            ceiling_report, fts_query)

# Each encoder's documented retrieval prefixes: nomic prefixes both sides; the
# bge v1.5 model card prescribes an instruction on short queries only.
DOC_PREFIX = {"nomic-ai/nomic-embed-text-v1.5": "search_document: ", "nomic-ai/nomic-embed-text-v1": "search_document: "}
QRY_PREFIX = {"nomic-ai/nomic-embed-text-v1.5": "search_query: ", "nomic-ai/nomic-embed-text-v1": "search_query: ",
              "BAAI/bge-base-en-v1.5": "Represent this sentence for searching relevant passages: "}
CONDITIONS = ("bm25_and", "bm25_or_raw", "bm25_or", "dense", "hybrid_and", "hybrid_or")


def load(dataset):
    import ir_datasets
    ds = ir_datasets.load(dataset)
    docs = [(d.doc_id, getattr(d, "title", "") or "", d.text) for d in ds.docs_iter()]
    queries = [(q.query_id, q.text) for q in ds.queries_iter()]
    qrels = {}
    for r in ds.qrels_iter():
        qrels.setdefault(r.query_id, {})[r.doc_id] = int(r.relevance)
    queries = [q for q in queries if q[0] in qrels]
    return docs, queries, qrels


def signature(model_name, texts, prefix):
    """What a cached embedding matrix was computed from: count, prefix, model,
    and a hash over the texts. A cache whose signature differs is recomputed."""
    import hashlib
    h = hashlib.sha256()
    for t in texts:
        h.update(t.encode("utf-8", "replace"))
        h.update(b"\0")
    return {"model": model_name, "prefix": prefix, "n": len(texts), "sha256": h.hexdigest()}


def embed_all(model_name, texts, prefix, cache, batch):
    sig = signature(model_name, texts, prefix)
    sig_path = cache.with_suffix(".sig.json")
    if cache.exists() and sig_path.exists() and json.loads(sig_path.read_text()) == sig:
        return np.load(cache)
    if cache.exists() and not sig_path.exists() and os.environ.get("DR_ADOPT_UNSIGNED_CACHE") == "1":
        # A cache written before signatures existed: adopt it if the row count
        # matches and record the signature. Opt-in, because adoption cannot see
        # what prefix or text the old file was computed from; the caller must
        # have deleted any cache whose inputs changed.
        vecs = np.load(cache)
        if vecs.shape[0] == len(texts):
            sig_path.write_text(json.dumps(sig))
            print(f"cache {cache.name}: adopted ({vecs.shape[0]} rows), signature recorded", file=sys.stderr)
            return vecs
    if cache.exists():
        print(f"cache {cache.name}: signature missing or stale, recomputing", file=sys.stderr)
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name, trust_remote_code=True)
    vecs = model.encode([prefix + t for t in texts], batch_size=batch,
                        show_progress_bar=True, normalize_embeddings=True, convert_to_numpy=True)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.save(cache, vecs.astype(np.float32))
    sig_path.write_text(json.dumps(sig))
    return vecs


def build_keyword(docs, path):
    """Build into a temporary file and rename, so a run that dies mid-insert
    cannot leave a half-filled index that a later run takes as complete."""
    if path.exists():
        kw = KeywordIndex(str(path))
        n = kw.c.execute("SELECT count(*) FROM fts").fetchone()[0]
        if n == len(docs):
            return kw
        kw.c.close()
        path.unlink()
    tmp = path.with_suffix(".building.sqlite")
    if tmp.exists():
        tmp.unlink()
    kw = KeywordIndex(str(tmp))
    kw.add(docs)
    kw.c.close()
    tmp.rename(path)
    return KeywordIndex(str(path))


KEYWORD_MODE = {"bm25_and": "and_quoted", "bm25_or_raw": "or_raw", "bm25_or": "or_bm25",
                "hybrid_and": "and_quoted", "hybrid_or": "or_bm25"}


def run_query(cond, q, qv, kw, dense, depth):
    """Ranked {doc_id: score} for one condition, plus a diagnostics dict."""
    if cond.startswith("bm25_"):
        ranked = kw.search(fts_query(q, KEYWORD_MODE[cond]), depth)
        return {d: 1.0 / (RRF_K + r) for r, d in enumerate(ranked)}, {"empty": not ranked, "n_keyword": len(ranked)}
    if cond == "dense":
        ranked = dense.search(qv, depth)
        return {d: 1.0 / (RRF_K + r) for r, d in enumerate(ranked)}, {"n_dense": len(ranked)}
    scores, ranks = HybridRetriever(kw, dense, fts_mode=KEYWORD_MODE[cond], depth=depth, k=RRF_K).retrieve(q, qv)
    rep = ceiling_report(scores, ranks, k=RRF_K)
    return scores, {"keyword_empty": "keyword" in rep.empty_legs, "at_ceiling": rep.at_ceiling,
                    "multi_leg_docs": rep.multi_leg_docs, "max_score": rep.max_score,
                    "n_keyword": len(ranks.get("keyword", {})), "n_dense": len(ranks.get("dense", {}))}


def evaluate(run, qrels):
    import pytrec_eval
    ev = pytrec_eval.RelevanceEvaluator(qrels, {"ndcg_cut_10", "recall_100"})
    per_q = ev.evaluate(run)
    n = len(per_q) or 1
    return {m: sum(v[m] for v in per_q.values()) / n for m in ("ndcg_cut_10", "recall_100")}


def summarize_diag(diags):
    out = {}
    for key in ("empty", "keyword_empty", "at_ceiling"):
        vals = [d[key] for d in diags if key in d]
        if vals:
            out[key + "_rate"] = sum(vals) / len(vals)
    ml = [d["multi_leg_docs"] for d in diags if "multi_leg_docs" in d]
    if ml:
        out["multi_leg_docs_mean"] = sum(ml) / len(ml)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="beir/scifact/test")
    ap.add_argument("--model", default="nomic-ai/nomic-embed-text-v1.5")
    ap.add_argument("--depth", type=int, default=100)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--cache", default="cache")
    ap.add_argument("--out", default="results")
    a = ap.parse_args()

    tag = a.dataset.replace("/", "_") + "__" + a.model.replace("/", "_")
    cache = Path(a.cache)
    docs, queries, qrels = load(a.dataset)
    print(f"{a.dataset}: {len(docs)} docs, {len(queries)} queries with qrels", file=sys.stderr)

    t0 = time.time()
    dvec = embed_all(a.model, [f"{t} {x}".strip() for _, t, x in docs], DOC_PREFIX.get(a.model, ""),
                     cache / f"{tag}.docs.npy", a.batch)
    qvec = embed_all(a.model, [q for _, q in queries], QRY_PREFIX.get(a.model, ""),
                     cache / f"{tag}.queries.npy", a.batch)
    dense = DenseIndex([d[0] for d in docs], dvec)
    kw = build_keyword(docs, cache / f"{a.dataset.replace('/', '_')}.fts.sqlite")
    print(f"indexes ready in {time.time() - t0:.0f}s", file=sys.stderr)

    results = {"dataset": a.dataset, "model": a.model, "depth": a.depth, "rrf_k": RRF_K,
               "n_docs": len(docs), "n_queries": len(queries), "conditions": {}}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    perq = (out / f"{tag}.perquery.jsonl").open("w")
    for cond in CONDITIONS:
        run, diags, secs = {}, [], 0.0
        for (qid, q), qv in zip(queries, qvec):
            t1 = time.perf_counter()
            scores, diag = run_query(cond, q, qv, kw, dense, a.depth)
            secs += time.perf_counter() - t1
            run[qid] = {str(d): float(s) for d, s in scores.items()}
            diags.append(diag)
            perq.write(json.dumps({"qid": qid, "condition": cond, **diag}) + "\n")
        results["conditions"][cond] = {**evaluate(run, qrels), **summarize_diag(diags),
                                       "mean_query_ms": 1000.0 * secs / max(1, len(queries))}
        print(cond, json.dumps(results["conditions"][cond]), file=sys.stderr)
    perq.close()

    (out / f"{tag}.json").write_text(json.dumps(results, indent=1) + "\n")
    print(out / f"{tag}.json")


if __name__ == "__main__":
    main()
