# Round 5 consensus — IRRJ confirmation (2026-10-14)

Brief: `review/brief-round5.md` (inline form by `make-round5-brief.sh`, 122 KB: paper, bibliography, significance.json, keyword facts, natural lengths, 18 summary files). Four seats, the ones that found the most in round 4.

## Lanes

| Seat | Route | Bytes | Verdict |
|---|---|---|---|
| Gemini 4 Argon (medium) | Devin | 7,066 | every star and count matches; 2 required fixes |
| GPT-6 Astra (xhigh) | Devin | 5,787 | every star and count matches; 6 text corrections |
| GPT-6.1 Sol (xhigh) | Devin | 5,937 | every star and count matches; same corrections as Astra |
| Claude Fable 5.1 | fresh subagent | ~8 KB | every star and count matches; Holm arithmetic spot-checked; 5 points the others missed |

## Verified and applied (commits `ab02398`, `88feada`)

| Defect | Seats | Fix |
|---|---|---|
| `\citealp{smucker2007comparison}` had no bibliography entry; the citation rendered undefined and the compile log check missed it | Argon, Astra, Sol | Entry added from Crossref (CIKM 2007, pp. 623--632); audit now checks every cited key against refs.bib and the built .bbl |
| Appendix B still said timings were omitted "because the collections were timed on two different machines" | Argon, Astra, Sol | Sentence replaced |
| "by 0.001, nomic (0.483)" on ArguAna is a 0.00016 difference | Astra, Sol | "above e5 (0.447) and level with nomic (0.483)" |
| "usually a different handful of documents" exceeds the rates (12.8 / 41.1 / 88.9%, 124 of 378 pooled) | Astra, Sol | Rates stated |
| "on ArguAna with bge it returned only the self-match" (four queries returned two; one relevant hit) and "the fused list was the dense list" asserted from aggregate equality | Astra, Sol | Reworded to what was measured |
| Conclusion "present on every query for as long as the builder had existed" and intro "from the start" restate the historical claim the abstract had already made an inference | Astra, Sol | "held on all ten replayed queries, and the unchanged builder implies…" |
| FiQA id-rule effect stated as an inference | Astra | Stated as the observed before/after comparison (every figure identical) |
| "none of whose tokens occur in the corpus at all" | Astra | "no quoted token matches any document" |
| Families not named | Astra, Sol | "six families: two metrics by three comparisons; no correction across families" |
| Figure caption "every cell" | Astra | "every populated cell" |

## Also verified and applied from Fable's seat (commit after `88feada`)

| Point | Fix |
|---|---|
| "The losses are largest on FiQA" is false as a set statement: TREC-COVID with nomic loses 0.054 (printed), more than FiQA's e5 and nomic | FiQA named as the largest single loss and the only collection where every encoder loses significantly; TREC-COVID nomic's 0.054 stated as not significant |
| NFCorpus's live AND lists are not "short": 86 of 159 have four or more documents | "exact-match lists of four or more documents on 86 of those 159" |
| The abstract never says the reproduction runs at K > k | "at $K = 100 > k = 60$" added |
| "the ceiling missed none of those empty legs" is the two-retriever theorem presented as a finding | "as the derivation requires with two retrievers" (abstract, conclusion) |
| Holm over all 108 tests: computed here, 23 of 31 family-level results survive, 8 lost, none of the seven h-or vs dense nDCG@10 stars (Fable's own count was 5 lost; the audit carries the computed 8) | One sentence in Limitations; audit check |
| TREC-COVID bge buggy-hybrid star rests on 13 live queries at p = 0.043 | Stated in 7.3 |
| SciFact's 0 of 18 is uninformative, not a counterexample (0 of 18 at NFCorpus's rate happens about half the time, 0.49) | Reworded; audit check |
| `thakur2021beir` cited for the evaluator default, which is in the BEIR code | "the evaluation code released with BEIR … its `ignore_identical_ids` option" |
| "11 of the two encoders' 20 cells" inside a sentence scoped to K = 60 | "20 cells at n >= 20 over both depths and both encoders" |
| SciDocs "at most 0.001" beside an unrounded SciFact figure | "(0.0017 before rounding)" added |

Not taken (optional): per-collection length trend as an extra clause; confidence intervals on the paired differences.

## Refuted

- Argon: `\usepackage{graphicx}` missing. `irrj2e.sty` loads graphicx (`\RequirePackage{graphicx}`); the figure compiles.

## Tension, resolved by stating the rule

Astra and Sol want prose differences computed before rounding (0.033, 0.034, 0.004, 0.059, 0.013); Argon accepted either if stated. Round 4 had the opposite complaint (prose differences that could not be reproduced from the printed tables). The protocol now states: "Differences quoted in the text are differences of the printed three-decimal values unless a fourth decimal is given." The audit enforces it.

## Judgements all seats share

- The paired sign-flip test and Holm's correction within six families are appropriate for the design; the three encoders rerun the same queries, which Holm tolerates; no paper-wide control is claimed (stated in Limitations).
- The 12-wins paragraph's partition (8 not above dense: 7 empty-leg pairs + ArguAna bge; 4 above: NFCorpus ×3, SciFact bge) follows from the tables.
- Section 7.4's counts match the JSON once SciFact is included and the builder pooling is stated.
- Title, abstract and conclusion claim no more than the body.
- No new retrieval experiment is needed. Optional: confidence intervals on the paired differences if the journal asks.
