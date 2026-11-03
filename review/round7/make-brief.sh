#!/bin/sh
# Round-7 briefs (rewrite, round 2 of 3): inline variant (diff + full paper + results), Gemini variant
# with absolute paths, Kagi/Cursor/ccx variant naming attachments, and the short GLM brief.
set -eu
R=$(cd "$(dirname "$0")/../.." && pwd)
D=$R/review/round7
{
  cat "$D/brief.md"
  for f in review/round7/diff-since-round6.patch review/round7/diff-refs.patch paper/main.tex paper/refs.bib results/significance.json results/keyword_facts.json results/natural_lengths.json; do
    printf '\n\n=== %s ===\n\n' "$f"
    cat "$R/$f"
  done
  for f in "$R"/results/beir_*.json; do
    case "$f" in *.sweep.json) continue ;; esac
    printf '\n\n=== results/%s ===\n\n' "$(basename "$f")"
    cat "$f"
  done
} > "$D/brief-inline.md"
{
  sed 's/^Do not use any tool.*$//' "$D/brief.md"
  printf '\n\nRead these files by absolute path before answering. Do not edit any files. Answer in your final message.\n\n'
  for f in review/round7/diff-since-round6.patch review/round7/diff-refs.patch paper/main.tex paper/refs.bib results/significance.json results/keyword_facts.json results/natural_lengths.json; do printf -- '- %s/%s\n' "$R" "$f"; done
  for f in "$R"/results/beir_*.json; do case "$f" in *.sweep.json) continue ;; esac; printf -- '- %s\n' "$f"; done
} > "$D/brief-gemini.md"
sed 's/^Do not use any tool.*$/The diff, the paper, its bibliography and the result summaries are attached. Answer in your final message./' "$D/brief.md" > "$D/brief-kagi.md"
{
  cat "$D/brief-glm-short.md"
  printf '=== abstract ===\n\n'; sed -n '/\\begin{abstract}/,/\\end{abstract}/p' "$R/paper/main.tex"
  printf '\n=== introduction ===\n\n'; sed -n '/\\section{Introduction}/,/\\section{The ceiling}/p' "$R/paper/main.tex" | sed '$d'
  printf '\n=== conclusion ===\n\n'; sed -n '/\\section{Conclusion}/,/\\section\*{Use of AI tools}/p' "$R/paper/main.tex" | sed '$d'
} > "$D/brief-glm.md"
wc -c "$D"/brief-inline.md "$D"/brief-gemini.md "$D"/brief-kagi.md "$D"/brief-glm.md
