# Review: dead-retriever paper, journal draft — round 5 (confirmation)

You are reviewing the submission candidate for the Information Retrieval Research Journal (single-blind, normal paper, about 20 pages). Round 4 (ten reviewers) found one experimental defect and fifteen text defects; all were applied. The experimental defect: the evaluator did not drop a document whose id equals the query's id (BEIR's default), so every ArguAna effectiveness figure counted the query's own document. All 18 collection--encoder pairs were rerun with that rule; the ArguAna figures changed (bge dense 0.456 to 0.641), nothing else did. Paired sign-flip randomization tests with Holm's correction were added (per-query scores now exist), the paper was restructured (introduction with contributions, related work before the experiments, a protocol section, a conclusion, the two production negative results moved to Appendix A), a figure was added, and the title was qualified. Answer as the one careful reviewer whose job is to stop the author from submitting something wrong. Formulas, section names and quoted phrases over adjectives; no compliments; do not restate the paper. Under 1000 words.

## What to do

1. **Read the whole paper once as a journal referee would** and name anything that would get it rejected or embarrass the author: a false sentence, a number that does not follow from the tables or the JSON below, a claim wider than the evidence, a citation that does not say what it is cited for, an inconsistency between sections. Sections 1 to 5 were edited lightly; Sections 6 to 10 and the abstract were rewritten.
2. **The significance test (Section 6, "Effectiveness", and Section 7.5).** `results/significance.json` is inline: 108 rows, one per (pair, metric, comparison), each with the mean paired difference, the randomization p-value and the Holm-adjusted p-value. Check that the stars in Tables 3 and 4 and every "significant" or "not significant" in the prose follow from it at alpha = 0.05 on `p_holm`. Say whether the test and correction are the right ones for this design (three encoders rerun the same queries; six families of 18).
3. **The rewritten mechanism paragraph (Section 7.5, "The buggy hybrid's 12 wins")** and the ArguAna paragraph that now says BM25 alone (0.484) is above two encoders: do they follow from the tables?
4. **Section 7.4 and Figure 1**: does the prose claim no more than the pooled and per-collection counts support, now that SciFact is included and the pooling of both builders is stated?
5. **Abstract, title and conclusion.** Do they claim exactly what the body shows, no more?
6. Anything a referee would still require before acceptance: one sentence each, required or optional. No new experiments unless one is essential.

## Attached (inline below; do not use any tool: do not read files, run commands, or fetch URLs; answer in your final message)

- `paper/main.tex` — the paper (IRRJ LaTeX style).
- `paper/refs.bib` — the bibliography (every entry was checked against Crossref, arXiv or the publisher listing; flag only if you know one to be wrong).
- `results/significance.json` — the paired tests.
- `results/keyword_facts.json`, `results/natural_lengths.json` — encoder-free keyword facts and the ceiling rate by keyword-leg length.
- `results/beir_<collection>__<encoder>.json` — the 18 summary files.
