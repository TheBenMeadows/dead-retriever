# dead-retriever

Code for the paper on diagnosing a silently inert retriever in hybrid search from the fused scores alone.

Reciprocal-rank fusion gives each document 1/(k + r) from every retriever that ranks it at position r. A document found by one retriever alone scores at most 1/k. When the maximum fused score across a result list is exactly 1/k, every document in it came from one retriever. Across a set of queries, that ceiling is the signature of a retriever that returns nothing, and it is visible in the scores alone.

The bug that motivated this is an FTS5 keyword query built by quoting every token and joining with spaces, which FTS5 reads as an implicit AND. On conversational queries it matched no chunk, the keyword half of a keyword+vector system was inert for months, and every result came from the vector leg. The fused scores had said so the whole time.

## Layout

- `dead_retriever/hybrid.py`: FTS5 keyword index, exact dense index, RRF, the two query builders (`and_quoted` reproduces the bug, `or_bm25` is the fix), and `ceiling_report`.
- `scripts/beir_run.py`: runs five conditions (bm25_and, bm25_or, dense, hybrid_and, hybrid_or) on a BEIR test split and writes nDCG@10, Recall@100 and per-query fusion diagnostics.
- `tests/test_hybrid.py`: a synthetic corpus where the quoted-AND builder returns nothing and the ceiling flags it.

## Run

```
python3 tests/test_hybrid.py
./scripts/beir_run.py --dataset beir/scifact/test --out results/
./scripts/beir_run.py --dataset beir/nfcorpus/test --out results/
```

The script downloads the BEIR split through `ir_datasets` and the encoder through `sentence-transformers`. Embeddings are cached under `cache/`.

## Provenance

`hybrid.py` is extracted from a private retrieval module (`rag_core.py`, sha256 `fc7153438f2f5a332bb38eec3476b4635196ad40ebd84a1d72659910bcf19ef4`, 2026-10-07). The private corpus, its queries and its documents are not part of this repository. The paper reports only aggregate numbers from it.
