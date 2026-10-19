#!/bin/sh
# Round-4 brief (IRRJ journal draft) with the paper, bibliography, keyword facts,
# natural lengths and the 18 summary result files inline.
set -eu
R=$(cd "$(dirname "$0")/.." && pwd)
OUT=$R/review/brief-round4-inline.md
{
  cat "$R/review/brief-round4.md"
  for f in paper/main.tex paper/refs.bib results/keyword_facts.json results/natural_lengths.json; do
    printf '\n\n=== %s ===\n\n' "$f"
    cat "$R/$f"
  done
  for f in "$R"/results/beir_*.json; do
    case "$f" in *.sweep.json) continue ;; esac
    printf '\n\n=== results/%s ===\n\n' "$(basename "$f")"
    cat "$f"
  done
} > "$OUT"
wc -c "$OUT"
