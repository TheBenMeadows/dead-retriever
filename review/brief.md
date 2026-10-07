# Review: dead-retriever paper, draft 1 — round 1

You are reviewing a short arXiv paper (cs.IR) and the code behind it. The paper claims that in reciprocal rank fusion a maximum fused score of exactly 1/k identifies a retriever that returned nothing, documents a production bug that caused exactly that (an SQLite FTS5 query built by quoting every token, which FTS5 reads as implicit AND), and reproduces the effect on two BEIR collections. Answer as a demanding IR reviewer who also reads code. Be specific and concrete; formulas and line references over adjectives; no compliments; do not restate the paper back to me. Rank findings by expected impact. Under 1200 words.

## The target

An arXiv preprint that a careful reader in information retrieval would accept as correct and honest: the derivation holds, every number in the text is in the result files, the claims are no wider than the evidence, the citations are real and say what the paper attributes to them, and the prose has no filler.

## Earlier rounds

None. This is the first outside review of the draft.

## What it does now

The paper (main.tex) has: the incident; the derivation of the ceiling (Section 2); the bug and its fix (Section 3); before/after aggregates from a private corpus (Section 4, Table 1); two negative results the dead leg confounded (Section 5); a BEIR reproduction with two encoders and five conditions (Section 6, Table 2 and Appendix A); related work; limitations; a short practical checklist. The private corpus itself is not available and will not be; only aggregates appear. The code (hybrid.py) is the FTS5 + exact-dense + RRF implementation with the two query builders and the ceiling report; beir_run.py produced the four result files in results/.

Settled and not under review: the choice of SciFact and NFCorpus; the two encoders; that the private corpus stays private; the venue (arXiv, no workshop).

## The standing verdict

Author's own words: "The derivation is simple enough that I may have missed a case where it fails. The BEIR tables show the hybrid with the fixed keyword leg does NOT beat dense alone at nDCG@10 for bge; I wrote that in plainly, but a reviewer may say the paper undercuts its own motivation. The related-work section is thin and I want to know which citations are wrong or missing. The ceiling false-positive rate (three queries on NFCorpus) is read off the table; is that reasoning right?"

## Attached from our side

- `/Users/bemeadows/Projects/dead-retriever/paper/main.tex` — the paper, LaTeX source. The unit under review.
- `/Users/bemeadows/Projects/dead-retriever/paper/refs.bib` — the bibliography. Check each entry against what you know.
- `/Users/bemeadows/Projects/dead-retriever/dead_retriever/hybrid.py` — the retriever, fusion and ceiling diagnostic. The `and_quoted` mode reproduces the bug.
- `/Users/bemeadows/Projects/dead-retriever/scripts/beir_run.py` — the experiment runner (conditions, metrics, diagnostics).
- `/Users/bemeadows/Projects/dead-retriever/results/beir_scifact_test__BAAI_bge-base-en-v1.5.json`
- `/Users/bemeadows/Projects/dead-retriever/results/beir_nfcorpus_test__BAAI_bge-base-en-v1.5.json`
- `/Users/bemeadows/Projects/dead-retriever/results/beir_scifact_test__nomic-ai_nomic-embed-text-v1.5.json`
- `/Users/bemeadows/Projects/dead-retriever/results/beir_nfcorpus_test__nomic-ai_nomic-embed-text-v1.5.json` — the four result files Tables 2 and 3 were filled from.

## Questions

1. **Derivation** — Is Section 2 correct? State any case where "max fused score <= 1/k implies no document was found by more than one retriever" fails under K <= k, and whether the weak-form statement for K > k is right. Is the "flatness is 1/k^2" remark right to first order?
2. **Numbers** — Does every figure in Tables 1 to 3 and in the prose match the result files (to the rounding shown)? List any that do not. Is the false-positive reading (ceiling rate minus empty rate = three queries on NFCorpus, two after the fix) a valid inference from per-query rates, or could the two sets differ in both directions?
3. **Claims vs evidence** — Where does the text claim more than the tables show? Where is a conclusion missing that the tables do support?
4. **Code** — In hybrid.py, does `and_quoted` faithfully reproduce FTS5 implicit AND as documented? Does `ceiling_report` compute what Section 2 defines? Does `rrf_fuse` handle duplicates and depth as the paper says? Any defect in beir_run.py that would bias a condition (document text construction, prefixes, depth, qrels filtering)?
5. **Citations** — Which references are wrong (venue, year, authors, title) or do not support the sentence that cites them? Which obvious related work is missing (hybrid retrieval failure analysis, RRF analysis, retrieval system monitoring)?
6. **Prose** — Which sentences are filler, repetition, or stakes inflation? Which of the limitations should be stated earlier?

Read the attached files; do not answer from this description alone. Run nothing. Write nothing. Do not edit any files. Answer in your final message.
