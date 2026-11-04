### Ranked Findings by Expected Impact

1. **Abstract drops "at the ceiling" on the 174 + 2 nonempty runs (broken by the Question 1c edit).** Replacing `"It also appeared over 174 nonempty keyword lists..."` with `"In 174 further query runs the keyword list was nonempty..."` deleted the verb phrase stating that the ceiling fired on those runs, and left "174 further query runs" attached to the previous sentence's "buggy builder" scope when 10 of the 174 are under the fixed builder.
2. **Incorrect dataset attribution for \citet{wang2021interpolation} in Sections 5.5 and 7.** Both sections say \citet{wang2021interpolation} evaluate on BEIR; their ICTIR 2021 paper evaluates on MS MARCO Passage and TREC DL 2019/2020, not BEIR (only \citealp{chen2022hybrid} uses BEIR).
3. **Conjunctive-query attribution for \citet{kumaran2007shorter} and \citet{bendersky2008verbose} in Section 7.** Both papers study verbose queries under Indri language-model scoring, not boolean conjunctive (`AND`) queries.
4. **Orphaned definite reference `"the 294 SciFact queries"` in Section 5.2.** Cutting the raw query counts from Section 5.1 removed the prior mention of 294 (`Table 2` prints `300` and `98.0%`).

---

### 1. Did the fixes hold?

- **(a) Health overclaim — held.**
  - *Abstract:* `"This paper shows that the fused scores reveal when the two lists did not overlap."`
  - *Section 1 (Introduction):* `"The fused scores can show something narrower, and useful. ... So, at $K \le k$, a fused list whose maximum score is $1/k$ contains no document that both retrievers returned. It does not say that either list is empty."`
  - *Section 5.5:* `"Overlap and effectiveness are different questions, and only relevance judgements answer the second."`
  - *Section 9 (Conclusion):* `"The scores can say whether two retrievers agreed on anything, the row counts can say what that means, and whether fusing a retriever helps is a question for relevance judgements."`
  - All four passages now restrict the score test to overlap and assign empty-vs-short-vs-full to the row counts.

- **(b) Rounding rule — held.**
  - *Section 5.1:* `"It is worse at nDCG@10 by 0.001 to 0.011 on five collections. The exception is FiQA, where OR over every token is better by 0.009 nDCG@10 and 0.013 Recall@100, at 5.6 times the cost."`
  - Both changed bounds (`0.011` on ArguAna: $0.484 - 0.473$; `0.013` on FiQA: $0.521 - 0.508$) now equal the differences of the three-decimal values printed in `Table 7` (`\ref{tab:bm25}`).

- **(c) Runs, not lists — introduced a new error in the Abstract.**
  - *Abstract:* `"In 174 further query runs the keyword list was nonempty but shared nothing with the dense list, mostly a short list on a large corpus. In two runs under the repaired builder, the lists shared one document at deep ranks, the case $K > k$ leaves open."`
  - The unit is now query runs, but neither sentence states that the fused list was *at the ceiling* on those $174 + 2$ runs (nor that these 176 runs exhaust the nonempty at-ceiling cases), and `"174 further query runs"` follows a sentence about the buggy builder even though the 174 span both builders (164 buggy, 10 repaired).

- **(d) Nonempty counterpart on the no-false-negative guarantee — held.**
  - *Section 1 (list item 1):* `"with two retrievers an empty list can never be missed while the other list is nonempty;"`
  - *Section 2:* `"So with two retrievers, as long as the other retriever returned something, the test has no false negatives for an empty list; everything it gets wrong is in the other direction, a ceiling over a nonempty list."`
  - *Section 8 (Limitations):* `"The exact ceiling statement needs $K \le k$, and the guarantee that an empty list is never missed needs two retrievers and a nonempty counterpart;"`
  - All three statements are exact.

---

### 2. What did the edits break?

- **Cross-references:** Every `Table~N`, `Section~N`, `Figure~1` and `Appendix` reference resolves to the intended target. In Section 3, removing `\subsection{The fix}` left the stopword drop inside `\subsection{How it was found, and what the scores had already said}` (`\label{sec:found}`), so `Section~\ref{sec:found}` in Section 7 still resolves to Section 3.2. In Section 5.5, `(Appendix~\ref{app:full})` for the shared-document means (`4.0`, `19.0`, `43.7`) still resolves to Appendix A, though `Table~\ref{tab:shared}` is now more specific.
- **Orphaned numbers:** Cutting `"294 of SciFact's 300 claim-length queries"` from Section 5.1 orphaned `"On the 294 SciFact queries with an empty keyword list"` in Section 5.2. In Section 5.1, `"905 against 52\,ms"` now sits beside `Table~\ref{tab:bm25}`, which prints `905.4` and `51.5`.
- **Definition order:** Moving `\emph{row counts}` to Section 1 and `\emph{at the ceiling}` into the Abstract fixed the prior use-before-definition issues; `\emph{content tokens}` is defined in Section 4 before `Table 2` and Section 5.1 use it.
- **Claims across sections:** Aligned except for the dropped "at the ceiling" predicate in the Abstract (finding 1).
- **Six new references:** `aslam2001metasearch` and `nuray2006ranking` match their descriptions. `wang2021interpolation` is misdescribed in Sections 5.5 and 7 as a BEIR study (it uses MS MARCO and TREC DL 2019/2020; finding 2). `kumaran2007shorter` and `bendersky2008verbose` study verbose queries under Indri language models rather than conjunctive boolean queries (finding 3).

---

### 3. Remaining readability stops

1. **Abstract:**
   - *Quote:* `"In 174 further query runs the keyword list was nonempty but shared nothing with the dense list, mostly a short list on a large corpus. In two runs under the repaired builder, the lists shared one document at deep ranks, the case $K > k$ leaves open."`
   - *Rewrite:* `"Across both builders, the ceiling also appeared in 174 query runs where the keyword list was nonempty but shared nothing with the dense list, mostly short lists on the larger corpora, and in two runs under the repaired builder where the lists shared one document at deep ranks, the case $K > k$ leaves open."`

2. **Section 5.5, paragraph 4, and Section 7, paragraph 1:**
   - *Quote (Section 5.5):* `"Unweighted RRF treats a weak keyword list and a strong dense list alike, which is one reason \citet{bruch2023fusion} find a tuned convex combination competitive, and the BEIR hybrids of \citet{chen2022hybrid} and \citet{wang2021interpolation} gain from BM25 under different fusion choices than this one."`
   - *Rewrite (Section 5.5):* `"Unweighted RRF treats a weak keyword list and a strong dense list alike, which is one reason \citet{bruch2023fusion} find a tuned convex combination competitive, and why \citet{wang2021interpolation} and \citet{chen2022hybrid} find that BM25 helps dense retrievers on MS~MARCO and BEIR under weighted interpolation."`
   - *Quote (Section 7):* `"\citet{wang2021interpolation} and \citet{chen2022hybrid} measure what BM25 adds to dense retrievers on BEIR,"`
   - *Rewrite (Section 7):* `"\citet{wang2021interpolation} and \citet{chen2022hybrid} measure what BM25 adds to dense retrievers on MS~MARCO and BEIR,"`

3. **Section 7, paragraph 2:**
   - *Quote:* `"That a conjunctive keyword query fails on verbose, natural-language input is an old observation: \citet{kumaran2007shorter} and \citet{bendersky2008verbose} both start from search engines doing badly on long queries and look for the few terms worth keeping, which is what the stopword drop in Section~\ref{sec:found} does crudely."`
   - *Rewrite:* `"That keyword retrieval degrades on verbose, natural-language input is an old observation: \citet{kumaran2007shorter} and \citet{bendersky2008verbose} both start from search engines doing badly on long queries and look for the few terms worth keeping, which is what the stopword drop in Section~\ref{sec:found} does crudely."`

4. **Section 5.2, paragraph 1:**
   - *Quote:* `"On the 294 SciFact queries with an empty keyword list, the per-query rows show that the \textsc{hybrid-and} list is the \textsc{dense} list: the same document count and a maximum score of exactly $1/60$."`
   - *Rewrite:* `"On the 294 of SciFact's 300 queries with an empty keyword list, the per-query rows show that the \textsc{hybrid-and} list is the \textsc{dense} list: the same document count and a maximum score of exactly $1/60$."`

---

### 4. The title against the content

`"The $1/k$ Ceiling: A Zero-Overlap Test for Hybrid Retrieval"` accurately promises what the paper delivers and leaves out only that $1/k$ is the Reciprocal Rank Fusion constant, which an IR reader recognises from the notation.

---

### 5. Post it?

A cs.IR reader will finish this version: the derivation, incident, and BEIR tables now move without repetition. Do not post before fixing the two-sentence gap in the Abstract where the 174 + 2 nonempty query runs lost the clause saying the ceiling appeared on them (finding 1), and correcting the citation of \citet{wang2021interpolation} from BEIR to MS MARCO (finding 2); with those two edits, post it.
