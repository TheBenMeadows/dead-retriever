# Round 4 consensus — IRRJ journal draft (2026-10-14)

Brief: `review/brief-round4.md` (inline form built by `make-round4-brief.sh`, 86 KB: paper, bibliography, keyword facts, natural lengths, 18 summary files). Every seat was told to use no tool. Probes: `review/probe-round4.py`.

## Lanes

| Seat | Route | Bytes | Note |
|---|---|---|---|
| Gemini 4 Argon (medium) | Devin | 8,756 | first launch failed "Unknown model" in the runner; same id answered directly and on relaunch |
| Gemini (agyx) | agyx | 8,723 | two refuted claims (X1, X2) |
| GPT-6 Astra (xhigh) | Devin | 7,383 | found the evaluation-protocol defect (P2) |
| GPT-6.1 Sol (xhigh) | Devin | 7,320 | also found P2 |
| Fable 5.1 | fresh Claude subagent, read only the brief | 6,562 | |
| SWE-2 (max) | Devin | 6,427 | free; noted ArguAna dense scores depressed by the self document |
| Grok 4.7 (medium) | Cursor | 5,887 | found P5 and P6 |
| DeepSeek V4.1 Flash | ccx | 5,868 | |
| GPT-6 Luna | Kagi | 5,634 | fallback for Codex |
| Codex GPT-5.6 Terra | ccx | 181 | ChatGPT free-plan cap (429 `usage_limit_reached`); replaced by Luna |
| GPT-6 Sol (xhigh) | Devin | 5,454 | one misread (X3) |

## Verified defects (all REPRODUCED by `probe-round4.py`)

| # | Defect | Seats | Fix |
|---|---|---|---|
| P2 | `evaluate()` scores a document whose id equals the query id; BEIR's evaluator drops it (`ignore_identical_ids`). ArguAna: 1,298/1,406 query ids are corpus ids, FiQA 55/648, others 0. Every ArguAna effectiveness figure counts the query's own (non-relevant) document. | Astra, 6.1 Sol, SWE-2 (consequence) | Runner fix `031d657` (exclusion at scoring only; fusion and diagnostics unchanged), rerun ArguAna + FiQA × 3 encoders on Kaggle, regenerate tables. Needs a push APPROVE. |
| P1 | "never useful" (§6.2 title, abstract): the AND leg hit a relevant document on 1 query. | Luna, Argon, Astra, 6.1 Sol, Grok | "almost never relevant" / "did not change aggregate effectiveness" |
| P10 | The §6.5 mechanism sentence: in 8 of the 12 pairs where the buggy hybrid beats the repaired one it does so by abstaining (empty leg leaves dense untouched); it beats dense in only 4 (SciFact bge by 0.001, NFCorpus ×3). | Argon, agyx | Rewrite the mechanism around abstention; keep NFCorpus as the exact-match case. |
| P3 | Prose bounds computed before rounding disagree with the 3-decimal tables: SciFact "at most 0.002" (e5 0.0022, table 0.003); Recall@100 "9 of 18" with one 0.0006 gain printed as a tie; "within 0.008" (ArguAna 0.0084); "2.6 to 18" (e5 NFCorpus 2.49); "0.1%" for 4/6,636 (0.06%); "at most 4.0" (4.006). | all ten | One rule: prose quotes differences of the printed values, or says "before rounding"; print the tie row to 4 decimals. |
| P4 | SciFact (0/18 at 5.2k docs) left out of the corpus-size list of short-list rates. | Argon, agyx, Astra, 6.1 Sol, Grok, SWE-2 | Include it; describe the pattern, no size rule. |
| P5 | "corpus size, document length and vocabulary differ along the same ordering" is false for corpus size (5,183; 25,657; 57,638; 171,332; 3,633 in content-token order). | Grok, SWE-2 | "the collections also differ in…" |
| P6 | "where the buggy leg was live on more queries the hybrid did move" is illustrated by TREC-COVID (13 live) while SciDocs (58 live) barely moves. | Grok | Reword. |
| P7 | The natural-length buckets pool both builders (1–3 bucket: 612 buggy, 114 fixed; fired 132 vs 5). | Luna, SWE-2 | State the pooling; give the split. |
| P8 | TREC-COVID's 16/18 short-list runs are 6 queries × 3 encoders. | Fable, Grok, Astra | Say six queries. |
| P9 | Abstract "restores overlap on every collection": ArguAna already overlapped (1.003 shared per query). | DeepSeek, Astra | "raises overlap in every pair". |
| P11 | "rank one" vs Section 2's 0-based ranks; "1,400-character chunk or one abstract" applied to BEIR; doc2query cited for "cheapest form of document expansion"; CombSUM credited with CombMNZ's multi-system reward. | Argon, Grok, DeepSeek, Astra, 6.1 Sol, agyx | Wording. |

Also from reading, not probed (true by inspection): the §6.6 sweep ranges pool bge and nomic while Table 5 prints bge only (Argon, Fable, DeepSeek, SWE-2, agyx) — state the pooling or print nomic; the abstract's "two working retrievers… four of ten queries did" — the incident's four were the buggy builder's 1–3 chunks (Fable, agyx); "top 100 fused results" at K = k = 60 is a cap, not a count (Fable, agyx); §6 defines bm25-or as "non-stopword tokens" without the under-three-characters rule (SWE-2).

## Exonerations (do not re-raise)

- X1 (agyx): "two live lists that agreed on every document would show the same step at twice the scale" is correct — the relative step is scale-invariant, the absolute step doubles, which is what "same step at twice the scale" says.
- X2 (agyx): the abstract's "therefore" carries the "with per-retriever depth K ≤ k" of the preceding sentence.
- X3 (GPT-6 Sol): "13 of 330 on NFCorpus (3.6k documents) implies 3.9%, not the printed 3.6%" — 3.6k is the corpus size, not a rate.
- agyx: "six-token conversational query" next to a seven-token example — the sentence is general, not about the example. "four original… pairs" in Appendix B means the earlier version's four pairs; make that explicit.

## Interpretation (converging judgements)

- Content-token ordering (a): supported as an observation; DeepSeek's point is the strongest — the quoted AND makes every token a conjunct, so the ordering is close to arithmetic. Say so instead of presenting it as a finding. "The content words are what run out" → "consistent with". (DeepSeek, Astra, 6.1 Sol, SWE-2)
- Corpus size (b): four-point description, SciFact breaks monotonicity; drop "Expect more such queries on a large corpus" from §9. (9 of 10)
- ArguAna generalisation (c): "routinely receives" → "can receive"; the blind spot needs the self-match to be unwanted (finding the source email may be the task). (9 of 10)
- Different instruments (d): supported by all; call the signals overlap and activity monitors, not a health verdict (Astra, 6.1 Sol).

## Tensions for Ben

- **Title.** DeepSeek, Astra, 6.1 Sol and Grok want "Found a Dead Retriever" changed or qualified (row counts found the bug; the ceiling was retrospective) and "Detects Zero Overlap" conditioned on K ≤ k. SWE-2, Argon and Fable accept it as a label for the incident. The title is shared with the arXiv and Zenodo versions.
- **Historical claim in the abstract** ("returned no results for most natural-language queries from the first version until 2026-08-18"): Astra and 6.1 Sol say it needs a traffic denominator or should be framed as an inference from the unchanged builder plus the replay.

## Journal fit (ranked by convergence)

1. Paired significance on the effectiveness comparisons (per-query rows exist; Wilcoxon or bootstrap, multiplicity handled) — required by 10 of 10. Needs per-query effectiveness scores, which the runner does not write today: the perquery JSONL holds diagnostics only. Either add per-query nDCG/Recall output to the runner (covered by the same Kaggle rerun if done before it) or recompute rankings.
2. Conventional structure: an Introduction with contributions, Related Work before the experiments, a methods/protocol subsection (tokenizer, stoplist, ID policy), a Conclusion — required by 7.
3. One figure (incident staircase, ceiling rate vs row count, or the r1·r2 = k² boundary) — 7, mostly optional.
4. Excess-run table naming the two FiQA overlap-present queries with their ranks (Grok, Astra).
5. State what the ceiling adds over logging row counts and counting overlap directly (GPT-6 Sol; Grok's contribution paragraph) — required by Sol.
6. Place FTS5 BM25 against published BEIR BM25 baselines (Fable); a second keyword engine (DeepSeek, optional).
7. Move §5 to an appendix (Grok, Astra, optional).
