## 1. Did the fixes hold?

**Health overclaim — held.** Abstract: "the fused scores reveal when the two lists did not overlap" and "The test measures overlap, not health: two nonempty lists that share nothing produce the same ceiling as an empty list, and per-retriever row counts tell the two cases apart." Intro: "The fused scores can show something narrower, and useful." Correct scope everywhere I checked.

**Rounding rule — held.** "0.001 to 0.011" is now differences of printed values (ArguAna 0.484−0.473=0.011, SciDocs 0.153−0.152=0.001); FiQA's "0.009 nDCG@10 and 0.013 Recall@100" is 0.233−0.224 and 0.521−0.508.

**Runs-not-lists — held.** Abstract: "In 174 further query runs the keyword list was nonempty but shared nothing with the dense list." Body: "In 174 of the 176" where the antecedent is "176 such query runs."

**Nonempty counterpart — held, with one leak.** §2: "as long as the other retriever returned something, the test has no false negatives for an empty list." Contributions: "while the other list is nonempty." Limitations: "two retrievers and a nonempty counterpart." But the abstract still says "as the derivation requires with two retrievers" — the one place the condition the paper now insists on is dropped. Add "and a nonempty counterpart" or cut the clause to "as the derivation requires here."

No fix introduced a new error.

## 2. What the edits broke

- **Results intro overclaims.** "Every condition for every collection--encoder pair is in Appendix~\ref{app:full}" is no longer true: the appendix now holds only the three BM25 conditions and the shared-doc counts; dense/h-and/h-or effectiveness is in Tables `tab:ndcg`–`tab:recall`. The appendix's own lead-in gets it right ("complete Tables…"). Fix the sentence: "Tables~\ref{tab:legs}–\ref{tab:recall} and Appendix~\ref{app:full} between them cover every condition and pair."
- **Wrong venue for a new citation.** "the BEIR hybrids of \citet{chen2022hybrid} and \citet{wang2021interpolation}" and "measure what BM25 adds to dense retrievers on BEIR" — Wang, Zhuang & Zuccon (ICTIR 2021) evaluates interpolation on MS MARCO and TREC DL, not BEIR, to my knowledge; the BEIR claim fits Chen et al. only. Reattribute before posting — this is falsifiable from memory by a reviewer.
- **"The buggy builder's empty rate runs from 50.8% on NFCorpus to 98.0% on SciFact"** reads as the six-collection range while ArguAna's 0.0% sits in the same table, and "the five rates" two sentences later never says which five. Name the exclusion: "Outside ArguAna — Section~\ref{sec:arguana} explains why it is never empty — the buggy builder's empty rate runs from 50.8% to 98.0%."
- **Orphaned bib entries.** `nogueira2019doc2query` and `anthropic2024contextual` were cited only in the cut Appendix A. BibTeX won't print them; delete anyway.
- Otherwise clean: `\ref{sec:found}` does cover the stopword-drop text (the fix paragraph lives there now); `tab:excess` "right" matches the new two-panel layout; no `\ref{app:negative}` remains. Spot-checked new numbers against the JSONs: 124 of 378 pooled; 39 ceilings over ≥4-doc lists (29 FiQA + 7 TREC + 3 SciDocs); h-or shared range 19.0–43.7; FiQA losses 0.037–0.058; the 5/13, 2/5, 9/9, 1/3, 12/6 tallies all reproduce from `significance.json`. Abstract, contribution list, "What to log," and conclusion all claim exactly what the body shows.

## 3. Remaining readability stops

- "Two in 22\,362 is why a system that runs at $K > k$ should count shared documents directly." The edit deleted the qualifier the sentence needs. → "Two such runs in 22\,362 — rare, but not zero — are why a system at $K > k$ should count shared documents directly."
- "the tables in this section hold what the text discusses" — delete it into the corrected pointer sentence above.
- Abstract: "mostly a short list on a large corpus" → "mostly short lists on the larger corpora."
- "Two details made the constraint stricter than ``every token present''." The swallowed-syntax-error detail isn't strictness, it's a second path to empty; the numbered frame misleads. → "Two details made things worse than ``every token present'' suggests."
- "the ceiling is a degenerate case of that idea, read at the point where agreement is zero" — the ceiling doesn't rank systems. → "the ceiling is the same agreement signal read at zero."

## 4. Title

"The $1/k$ Ceiling: A Zero-Overlap Test for Hybrid Retrieval" promises exactly what the paper delivers; the only omitted condition — exactness at $K \le k$ — is abstract-level, not title-level.

## 5. Post it?

Yes, after one last pass. A cs.IR reader finishes this version: the thesis is scoped correctly everywhere it matters, the collapsed tables carry what the prose dropped, and the ArguAna blind spot is stated honestly. The single highest-value remaining change is fixing the two falsifiable surface claims — the `app:full` pointer (wrong as written) and the `wang2021interpolation` venue attribution — since those are the only things left a reviewer can refute without running anything. Everything above that is copy-editing; nothing below it blocks posting.
