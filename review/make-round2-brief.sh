#!/bin/sh
# Round-2 brief with the paper source and result JSONs inline (no file tool needed).
set -eu
R=/Users/bemeadows/Projects/dead-retriever
OUT=$R/review/brief-round2-inline.md
{
  cat "$R/review/brief-round2.md"
  for f in paper/main.tex \
           results/beir_scifact_test__BAAI_bge-base-en-v1.5.json \
           results/beir_nfcorpus_test__BAAI_bge-base-en-v1.5.json \
           results/beir_scifact_test__nomic-ai_nomic-embed-text-v1.5.json \
           results/beir_nfcorpus_test__nomic-ai_nomic-embed-text-v1.5.json; do
    printf '\n\n=== %s ===\n\n' "$f"
    cat "$R/$f"
  done
} > "$OUT"
wc -c "$OUT"
