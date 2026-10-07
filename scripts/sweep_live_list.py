#!/opt/homebrew/bin/uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["ir_datasets", "numpy"]
# ///
"""Operating characteristic of the ceiling test against live-list length.

For every query, the fixed keyword list (OR over non-stopword tokens) is cut to
its first n documents and fused with the dense top K. The ceiling test fires
when the maximum fused score is <= 1/k. For each n this reports how often it
fired, how often the two lists in fact shared nothing (the quantity the test
is meant to detect), and how often they shared something at ranks whose
combined credit stayed at or below 1/k (the K > k leak). Depth K is swept over
{60, 100} so the exact case K = k = 60 sits beside the paper's K = 100 setting.
Uses the embedding caches written by beir_run.py; no model is loaded.

    sweep_live_list.py --dataset beir/scifact/test --model BAAI/bge-base-en-v1.5 --out results/
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dead_retriever import RRF_K, DenseIndex, KeywordIndex, fts_query, rrf_fuse  # noqa: E402

LENGTHS = (1, 2, 3, 5, 10, 20, 50, 100)
DEPTHS = (60, 100)


def load_queries(dataset):
    import ir_datasets
    ds = ir_datasets.load(dataset)
    qrels = {r.query_id for r in ds.qrels_iter()}
    docs = [d.doc_id for d in ds.docs_iter()]
    return [(q.query_id, q.text) for q in ds.queries_iter() if q.query_id in qrels], docs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="beir/scifact/test")
    ap.add_argument("--model", default="BAAI/bge-base-en-v1.5")
    ap.add_argument("--cache", default="cache")
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    tag = a.dataset.replace("/", "_") + "__" + a.model.replace("/", "_")
    cache = Path(a.cache)
    queries, doc_ids = load_queries(a.dataset)
    dvec = np.load(cache / f"{tag}.docs.npy")
    qvec = np.load(cache / f"{tag}.queries.npy")
    if len(doc_ids) != dvec.shape[0] or len(queries) != qvec.shape[0]:
        sys.exit(f"cache shape mismatch: {len(doc_ids)} docs vs {dvec.shape}, {len(queries)} queries vs {qvec.shape}")
    dense = DenseIndex(doc_ids, dvec)
    kw = KeywordIndex(str(cache / f"{a.dataset.replace('/', '_')}.fts.sqlite"))

    k = RRF_K
    out = {"dataset": a.dataset, "model": a.model, "rrf_k": k, "n_queries": len(queries), "cells": []}
    for K in DEPTHS:
        dense_lists = [dense.search(qv, K) for qv in qvec]
        kw_lists = [kw.search(fts_query(q, "or_bm25"), K) for _, q in queries]
        for n in LENGTHS:
            if n > K:
                continue
            fired = disjoint = leak = live = 0
            for dl, kl in zip(dense_lists, kw_lists):
                cut = kl[:n]
                if not cut:
                    continue  # an empty leg is the case the test cannot miss; this sweep is about live legs
                live += 1
                scores, ranks = rrf_fuse({"dense": dl, "keyword": cut}, k)
                mx = max(scores.values())
                shared = sum(1 for d in scores if d in ranks["dense"] and d in ranks["keyword"])
                at_ceiling = mx <= 1.0 / k + 1e-12
                fired += at_ceiling
                disjoint += (shared == 0)
                leak += (at_ceiling and shared > 0)
            out["cells"].append({"K": K, "n": n, "live_queries": live,
                                 "fired_rate": fired / live if live else None,
                                 "disjoint_rate": disjoint / live if live else None,
                                 "fired_with_overlap_rate": leak / live if live else None})
            print(json.dumps(out["cells"][-1]), file=sys.stderr)
    Path(a.out).mkdir(parents=True, exist_ok=True)
    p = Path(a.out) / f"{tag}.sweep.json"
    p.write_text(json.dumps(out, indent=1) + "\n")
    print(p)


if __name__ == "__main__":
    main()
