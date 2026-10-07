# Review: dead-retriever paper, draft 3 — round 3 (final full read)

You are reviewing the submission candidate of a short arXiv paper (cs.IR). Two earlier rounds (eight reviews in all) corrected the thesis to "the 1/k ceiling in reciprocal rank fusion detects zero overlap, not an empty retriever", rewrote Sections 2 and 6, re-ran the experiments with the bge query instruction, persisted per-query diagnostics, and added the experiment reviewers asked for: the ceiling's firing rate against the length of a live keyword list (Section 6, "How short is too short", Table 4). That section has not been reviewed by anyone yet. Answer as the one careful reviewer whose job is to stop the author from posting something wrong. Formulas and line references over adjectives; no compliments; do not restate the paper. Under 1000 words.

## What to do

1. **Read the whole paper once as a reader would** and name anything that would embarrass the author after posting: a false sentence, a number that does not follow from the tables, a claim wider than the evidence, a citation that does not say what it is cited for, an inconsistency between sections.
2. **Section 2 arithmetic, once more.** Is every sentence true as stated, including the one-sided direction (max > 1/k implies overlap for any K), the r1 r2 < k^2 condition, the L > 2 remark, and the one-based shift (ceiling 1/(k+1), strict separation for K <= k+1)?
3. **Table 4 and its paragraph (new).** Do the prose ranges follow from the table and from the four `*.sweep.json` files reproduced below (which also hold the nomic encoder and the disjoint and fired-with-overlap rates)? Is "the K > k leak never occurred" stated with the right scope? Is the operator advice in that paragraph supported?
4. **Abstract and title.** Do they now claim exactly what the body shows, no more?
5. **Anything missing** that a reader would expect in a paper this size and no more: one sentence per item, no new experiments unless one is essential.

## Attached (inline below; do not use any tool: do not read files, run commands, or fetch URLs; answer in your final message)

- `paper/main.tex` — the paper.
- `paper/refs.bib` — the bibliography (every entry was checked against a primary listing in round 1; flag only if you know one to be wrong).
- `results/*.json` — the four main result files (bge and nomic × SciFact and NFCorpus).
- `results/*.sweep.json` — the four live-list-length sweep files behind Table 4.
