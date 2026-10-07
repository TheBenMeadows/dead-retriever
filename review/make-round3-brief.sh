#!/bin/sh
# Round-3 brief with the paper, bibliography, main results and sweep results inline.
set -eu
R=/Users/bemeadows/Projects/dead-retriever
OUT=$R/review/brief-round3-inline.md
{
  cat "$R/review/brief-round3.md"
  for f in paper/main.tex paper/refs.bib \
           results/beir_scifact_test__BAAI_bge-base-en-v1.5.json \
           results/beir_nfcorpus_test__BAAI_bge-base-en-v1.5.json \
           results/beir_scifact_test__nomic-ai_nomic-embed-text-v1.5.json \
           results/beir_nfcorpus_test__nomic-ai_nomic-embed-text-v1.5.json \
           results/beir_scifact_test__BAAI_bge-base-en-v1.5.sweep.json \
           results/beir_nfcorpus_test__BAAI_bge-base-en-v1.5.sweep.json \
           results/beir_scifact_test__nomic-ai_nomic-embed-text-v1.5.sweep.json \
           results/beir_nfcorpus_test__nomic-ai_nomic-embed-text-v1.5.sweep.json; do
    printf '\n\n=== %s ===\n\n' "$f"
    cat "$R/$f"
  done
} > "$OUT"
wc -c "$OUT"
