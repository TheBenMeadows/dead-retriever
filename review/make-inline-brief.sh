#!/bin/sh
# Build a self-contained brief with every reviewed file reproduced inline, for
# lanes whose file tool is confirm-gated in print mode (Devin, 2026-10-07).
set -eu
R=/Users/bemeadows/Projects/dead-retriever
OUT=$R/review/brief-inline.md
{
  sed -e 's/^Read the attached files; do not answer from this description alone\. Run nothing\. Write nothing\. Do not edit any files\. Answer in your final message\.$/Every file named above is reproduced in full below. Do not use any tool: do not read files, run commands, or fetch URLs. Answer in your final message./' "$R/review/brief.md"
  for f in paper/main.tex paper/refs.bib dead_retriever/hybrid.py scripts/beir_run.py \
           results/beir_scifact_test__BAAI_bge-base-en-v1.5.json \
           results/beir_nfcorpus_test__BAAI_bge-base-en-v1.5.json \
           results/beir_scifact_test__nomic-ai_nomic-embed-text-v1.5.json \
           results/beir_nfcorpus_test__nomic-ai_nomic-embed-text-v1.5.json; do
    printf '\n\n=== %s ===\n\n' "$f"
    cat "$R/$f"
  done
} > "$OUT"
wc -c "$OUT"
grep -c "Do not use any tool" "$OUT"
