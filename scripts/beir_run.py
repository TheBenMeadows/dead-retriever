#!/opt/homebrew/bin/uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["ir_datasets", "sentence-transformers", "pytrec_eval", "numpy", "einops"]
# ///
"""Run the dead-retriever conditions on one BEIR test split and write metrics.

    beir_run.py --dataset beir/scifact/test --model nomic-ai/nomic-embed-text-v1.5 --out results/

Conditions: bm25_and (quoted-AND builder), bm25_or, dense, hybrid_and, hybrid_or.
Metrics: nDCG@10 and Recall@100 (pytrec_eval), plus per-query fusion diagnostics
for the hybrid conditions (keyword leg empty, max fused score at the 1/k ceiling,
documents credited by both legs).
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dead_retriever import (RRF_K, DenseIndex, HybridRetriever, KeywordIndex,  # noqa: E402
                            ceiling_report, fts_query)

DOC_PREFIX = {"nomic-ai/nomic-embed-text-v1.5": "search_document: ", "nomic-ai/nomic-embed-text-v1": "search_document: "}
QRY_PREFIX = {"nomic-ai/nomic-embed-text-v1.5": "search_query: ", "nomic-ai/nomic-embed-text-v1": "search_query: "}
CONDITIONS = ("bm25_and", "bm25_or", "dense", "hybrid_and", "hybrid_or")


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


def embed_all(model_name, texts, prefix, cache, batch):
    if cache.exists():
        return np.load(cache)
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name, trust_remote_code=True)
    vecs = model.encode([prefix + t for t in texts], batch_size=batch,
                        show_progress_bar=True, normalize_embeddings=True, convert_to_numpy=True)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.save(cache, vecs.astype(np.float32))
    return vecs


def build_keyword(docs, path):
    fresh = not path.exists()
    kw = KeywordIndex(str(path))
    if fresh:
        kw.add(docs)
    return kw


def run_query(cond, q, qv, kw, dense, depth):
    """Ranked {doc_id: score} for one condition, plus a diagnostics dict."""
    if cond == "bm25_and":
        ranked = kw.search(fts_query(q, "and_quoted"), depth)
        return {d: 1.0 / (RRF_K + r) for r, d in enumerate(ranked)}, {"empty": not ranked}
    if cond == "bm25_or":
        ranked = kw.search(fts_query(q, "or_bm25"), depth)
        return {d: 1.0 / (RRF_K + r) for r, d in enumerate(ranked)}, {"empty": not ranked}
    if cond == "dense":
        ranked = dense.search(qv, depth)
        return {d: 1.0 / (RRF_K + r) for r, d in enumerate(ranked)}, {}
    mode = "and_quoted" if cond == "hybrid_and" else "or_bm25"
    scores, ranks = HybridRetriever(kw, dense, fts_mode=mode, depth=depth).retrieve(q, qv)
    rep = ceiling_report(scores, ranks)
    return scores, {"keyword_empty": "keyword" in rep.empty_legs, "at_ceiling": rep.at_ceiling,
                    "multi_leg_docs": rep.multi_leg_docs, "max_score": rep.max_score}


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
    for cond in CONDITIONS:
        run, diags = {}, []
        for (qid, q), qv in zip(queries, qvec):
            scores, diag = run_query(cond, q, qv, kw, dense, a.depth)
            run[qid] = {str(d): float(s) for d, s in scores.items()}
            diags.append(diag)
        results["conditions"][cond] = {**evaluate(run, qrels), **summarize_diag(diags)}
        print(cond, json.dumps(results["conditions"][cond]), file=sys.stderr)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{tag}.json").write_text(json.dumps(results, indent=1) + "\n")
    print(out / f"{tag}.json")


if __name__ == "__main__":
    main()
