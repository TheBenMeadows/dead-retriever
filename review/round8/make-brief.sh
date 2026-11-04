#!/bin/sh
# Round-8 briefs (rewrite, round 3 of 3, confirmation): inline (diff + paper + results), Gemini (paths), Kagi (attachments).
set -eu
R=$(cd "$(dirname "$0")/../.." && pwd)
D=$R/review/round8
{
  cat "$D/brief.md"
  for f in review/round8/diff-since-round7.patch paper/main.tex paper/refs.bib results/significance.json results/keyword_facts.json results/natural_lengths.json; do
    printf '\n\n=== %s ===\n\n' "$f"; cat "$R/$f"
  done
  for f in "$R"/results/beir_*.json; do case "$f" in *.sweep.json) continue ;; esac; printf '\n\n=== results/%s ===\n\n' "$(basename "$f")"; cat "$f"; done
} > "$D/brief-inline.md"
{
  sed 's/^Do not use any tool.*$//' "$D/brief.md"
  printf '\n\nRead these files by absolute path before answering. Do not edit any files. Answer in your final message.\n\n'
  for f in review/round8/diff-since-round7.patch paper/main.tex paper/refs.bib results/significance.json results/keyword_facts.json results/natural_lengths.json; do printf -- '- %s/%s\n' "$R" "$f"; done
  for f in "$R"/results/beir_*.json; do case "$f" in *.sweep.json) continue ;; esac; printf -- '- %s\n' "$f"; done
} > "$D/brief-gemini.md"
sed 's/^Do not use any tool.*$/The diff, the paper, its bibliography and the result summaries are attached. Answer in your final message./' "$D/brief.md" > "$D/brief-kagi.md"
wc -c "$D"/brief-inline.md "$D"/brief-gemini.md "$D"/brief-kagi.md
