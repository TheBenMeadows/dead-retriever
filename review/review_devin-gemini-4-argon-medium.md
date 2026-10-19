### 1. Whole-paper referee pass: defects to fix before submission

1. **Missing bibliography entry (`\citealp{smucker2007comparison}`).** Section~\ref{sec:protocol} ("Effectiveness") cites `\citealp{smucker2007comparison}`, but `smucker2007comparison` is absent from `paper/refs.bib`. BibTeX will fail on this key and render `(?)` in the compiled PDF. Add the `@inproceedings{smucker2007comparison, ...}` entry (Smucker, Allan, and Carterette, CIKM 2007, pp. 623--632) to `paper/refs.bib`.
2. **Stale contradiction on timing hardware between Section~\ref{sec:protocol}, Appendix~\ref{app:full}, and Appendix~\ref{app:run}.** Section~\ref{sec:protocol} ("Hardware") states that *"Every run reported here was made in one Kaggle kernel on an NVIDIA T4 (Appendix~\ref{app:run})"* and Appendix~\ref{app:run} confirms *"every result file in the repository is from the Kaggle runs."* However, Appendix~\ref{app:full} still says: *"Query times are in `results/*.json` and are omitted here because the collections were timed on two different machines (Appendix~\ref{app:run})."* That sentence is a leftover from before all 18 pairs were rerun on the T4 and contradicts both Section~\ref{sec:protocol} and Appendix~\ref{app:run}. Replace the reason in Appendix~\ref{app:full} (e.g., omit for space or because shared-host CPU variance is already summarised in Section~\ref{sec:leg}).
3. **Verify `\usepackage{graphicx}` for Figure~\ref{fig:length}.** `paper/main.tex` now calls `\includegraphics[width=\textwidth]{fig-ceiling-length.pdf}` in Section~\ref{sec:rowcount}, but the preamble does not explicitly load `\usepackage{graphicx}`. Unless `irrj2e.sty` loads `graphicx` internally, compilation will fail on `\includegraphics`.

---

### 2. Significance tests (Section 6 and Section 7.5)

- **Verification against `results/significance.json`.** Every star in Tables~\ref{tab:ndcg} and~\ref{tab:recall} and every significance count in the Abstract, Section~\ref{sec:effect}, Section~\ref{sec:discussion}, and Section~\ref{sec:conclusion} matches `p_holm < 0.05` across all 108 rows of `results/significance.json`:
  - `hybrid_or` vs. `dense` on `ndcg_cut_10`: 5 positive (`p_holm < 0.05` in 2: ArguAna `nomic` and `e5`), 13 negative (`p_holm < 0.05` in 5: ArguAna `bge`, SciDocs `bge`, FiQA all 3).
  - `hybrid_and` vs. `dense` on `ndcg_cut_10`: `p_holm < 0.05` in 6 (NFCorpus `nomic` and `e5` positive; FiQA all 3 and TREC-COVID `bge` negative; TREC-COVID `nomic` is `p_holm = 0.0578`, rightly unstarred).
  - `hybrid_or` vs. `dense` on `recall_100`: 9 positive (`p_holm < 0.05` in 1: ArguAna `e5`; NFCorpus `bge` has `mean_diff = +0.000588`, rightly explained as a rounded tie in Table~\ref{tab:recall}), 9 negative (`p_holm < 0.05` in 3: SciDocs `bge`, FiQA `bge`, TREC-COVID `nomic`).
  - `hybrid_and` vs. `dense` on `recall_100`: `p_holm < 0.05` in 3 (NFCorpus all 3).
  - `hybrid_and` vs. `hybrid_or` on `ndcg_cut_10`: 12 positive (`p_holm < 0.05` in 6: ArguAna `bge`, FiQA `bge` and `nomic`, NFCorpus `bge` and `e5`, SciDocs `bge`; FiQA `e5` and NFCorpus `nomic` sit at `p_holm = 0.0655`), 6 negative (`p_holm < 0.05` in 2: ArguAna `nomic` and `e5`).
- **Appropriateness of the test and correction.** A two-sided paired sign-flip randomization test with $10^5$ trials is the standard non-parametric test for per-query IR metrics, including when most per-query differences are identically zero (as in `hybrid_and` vs. `dense`). Defining Holm step-down families of size 18 per `(metric, comparison)` is appropriate and well-disclosed: Section~\ref{sec:protocol} and Section~\ref{sec:limits} explicitly note that the three encoders rerun the same queries (so the 18 tests within a family are positively dependent—under which Holm's procedure remains valid, since Holm holds under arbitrary dependence) and that no correction is applied across the six families.

---

### 3. Rewritten mechanism and ArguAna paragraphs (Section 7.5)

- **ArguAna paragraph.** Follows from the tables: `bm25-or` nDCG@10 is `0.484` (Appendix~\ref{app:full}, raw `0.4836`), which exceeds `e5` `dense` (`0.447`) and `nomic` `dense` (`0.483`, raw `0.4834`) by `0.001` as printed (`0.0002` unrounded), while trailing `bge` `dense` (`0.641`). Consequently `hybrid-or` significantly improves `e5` (`+0.085`) and `nomic` (`+0.034` from printed table values, `+0.0331` unrounded) and significantly degrades `bge` (`-0.035` printed, `-0.0343` unrounded).
- **"The buggy hybrid's 12 wins" paragraph.** Every count and partition holds:
  - Of the 12 pairs where `h-and > h-or` at nDCG@10, 8 have `h-and <= dense`: seven on SciDocs (3), FiQA (3), and TREC-COVID (`nomic`) where `kw empty` is 74.0% to 94.2%, plus ArguAna with `bge` where `h-and` equals `dense` (`0.641`) because `bm25-and` returns only the self-match.
  - The remaining 4 of 12 are NFCorpus (all 3 encoders, `+0.008` to `+0.014` printed over `dense`, significant for `nomic` and `e5`) and SciFact with `bge` (`+0.001`), where `h-and > dense`.

---

### 4. Section 7.4 and Figure 1

- All pooled and per-collection counts match `results/natural_lengths.json` and `results/keyword_facts.json`:
  - Pooled excluding ArguAna across both builders and 3 encoders: `1-3` has `137 / 726` (`18.9%`), split into `612` buggy-builder runs (`73 + 46 + 73 + 6 = 198` queries $\times 3 = 594$ plus SciFact's $6 \times 3 = 18$, firing on `132`) and `114` fixed-builder runs (firing on `5`); `4-49` has `35 / 588` (`6.0%`); `50-100` has `4 / 6,636` (`0.06%`).
  - Per-collection `1-3` counts (`0/18` SciFact, `13/330` NFCorpus, `18/141` SciDocs, `90/219` FiQA, `16/18` TREC-COVID) sum to `137 / 726`.
  - The prose explicitly notes that SciFact (`0/18` at `5.2k` docs vs. NFCorpus `13/330` at `3.6k`) breaks a strict corpus-size ordering and that both builders are pooled.

---

### 5. Abstract, title, and conclusion

- The title (`... Detects Zero Overlap at Depth K <= k: an Incident and Six BEIR Collections`), abstract, and conclusion state the exact theorem, the $K > k$ caveat (including the 2 FiQA runs), the 174 disjoint-live runs, the ArguAna self-match blindness, and the exact effectiveness and significance counts (`5 of 18`, `2` significant; `13 of 18`, `5` significant). No claim exceeds the body.

---

### 6. Remaining items before acceptance

- **Required:** Add `smucker2007comparison` to `paper/refs.bib` so the citation in Section~\ref{sec:protocol} resolves.
- **Required:** Fix the stale sentence in Appendix~\ref{app:full} claiming query times were omitted *"because the collections were timed on two different machines"*, which contradicts Section~\ref{sec:protocol} and Appendix~\ref{app:run}.
- **Optional:** In Section~\ref{sec:effect}, three reported differences (`0.034` on ArguAna `nomic`, `0.005` on SciFact `nomic`, `0.014` on NFCorpus `nomic`) are differences of the 3-decimal rounded entries in Table~\ref{tab:ndcg} whereas `mean_diff` in `results/significance.json` rounds to `0.033`, `0.004`, and `0.013`; either use the unrounded differences or note that differences in the text are between printed table entries.
