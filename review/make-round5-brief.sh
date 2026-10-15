#!/bin/sh
# Round-5 brief (IRRJ confirmation) with the paper, bibliography, significance tests, keyword facts,
# natural lengths and the 18 summary result files inline.
set -eu
R=$(cd "$(dirname "$0")/.." && pwd)
OUT=$R/review/brief-round5-inline.md
{
  cat "$R/review/brief-round5.md"
  for f in paper/main.tex paper/refs.bib results/significance.json results/keyword_facts.json results/natural_lengths.json; do
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
