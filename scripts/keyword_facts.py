#!/opt/homebrew/bin/uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["ir_datasets", "numpy"]
# ///
"""Keyword-side facts per BEIR collection that need no encoder: query length
in the builder's own tokens, and what the quoted-AND leg returns. Writes
results/keyword_facts.json.

For each collection and each query with qrels: the token count, the count
after the fixed builder's stopword and short-token drop, the AND leg's row
count (depth 100), whether the AND leg returned the query's own id, whether it
returned a document whose text equals the query's after whitespace and case
normalisation (ArguAna's queries are themselves corpus documents), whether
any AND hit is relevant, and how many query ids are also corpus document ids
(the ids the evaluator drops before scoring).

    scripts/keyword_facts.py
"""
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import ir_datasets  # noqa: E402

from dead_retriever import KeywordIndex, fts_query  # noqa: E402
from dead_retriever.hybrid import FTS_STOP, tokens  # noqa: E402

DATASETS = ("beir/scifact/test", "beir/nfcorpus/test", "beir/arguana", "beir/scidocs",
            "beir/fiqa/test", "beir/trec-covid")
DEPTH = 100


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def facts(name):
    ds = ir_datasets.load(name)
    docs = {d.doc_id: d.text for d in ds.docs_iter()}
    kw = KeywordIndex(":memory:")
    kw.add([(d.doc_id, getattr(d, "title", "") or "", d.text) for d in ds.docs_iter()])
    qrels = {}
    for r in ds.qrels_iter():
        qrels.setdefault(r.query_id, {})[r.doc_id] = int(r.relevance)
    n_tok, n_kept, n_and = [], [], []
    self_hit = self_top = rel_hit = same_text = id_in_corpus = 0
    for q in ds.queries_iter():
        if q.query_id not in qrels:
            continue
        id_in_corpus += q.query_id in docs
        toks = tokens(q.text)
        n_tok.append(len(toks))
        n_kept.append(len([t for t in toks if len(t) > 2 and t not in FTS_STOP]))
        hits = kw.search(fts_query(q.text, "and_quoted"), DEPTH)
        n_and.append(len(hits))
        self_hit += q.query_id in hits
        self_top += bool(hits) and hits[0] == q.query_id
        rel_hit += any(qrels[q.query_id].get(h, 0) > 0 for h in hits)
        same_text += any(norm(docs[h]) == norm(q.text) for h in hits)
    n = len(n_tok)
    return {"dataset": name, "n_queries": n,
            "tokens_mean": statistics.fmean(n_tok), "tokens_median": statistics.median(n_tok),
            "kept_tokens_mean": statistics.fmean(n_kept),
            "and_empty": sum(1 for x in n_and if x == 0),
            "and_rows_1_3": sum(1 for x in n_and if 1 <= x <= 3),
            "and_rows_4_plus": sum(1 for x in n_and if x >= 4),
            "and_returns_query_itself": self_hit, "and_query_itself_at_rank_1": self_top,
            "and_returns_query_text": same_text, "and_any_relevant_hit": rel_hit,
            "query_id_is_doc_id": id_in_corpus}


def main():
    out = [facts(name) for name in DATASETS]
    for f in out:
        print(json.dumps(f))
    (ROOT / "results" / "keyword_facts.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
