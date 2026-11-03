### 1. Did the fixes hold?

The four correctness fixes held and introduced no new errors.

- **Health overclaim (three sentences):**
  1. *Abstract:* \
     `"This paper shows that the fused scores reveal when the two lists did not overlap."` \
     Right. Replaces the claim that scores reveal retriever failure with the exact claim of zero overlap.
  2. *Section 1 (Introduction):* \
     `"The fused scores can show something narrower, and useful."` and `"It does not say that either list is empty. The per-retriever \emph{row counts}, the number of documents each retriever returned for the query, separate an empty list from a short one and from two full lists that happen to share nothing."` \
     Right. Explicitly bounds the fused scores to overlap and assigns diagnosis of emptiness to row counts.
  3. *Section 9 (Conclusion):* \
     `"The scores can say whether two retrievers agreed on anything, the row counts can say what that means, and whether fusing a retriever helps is a question for relevance judgements."` \
     Right. Replaces the claim that scores determine whether a retriever is "alive" with the three-way division of labor: scores measure agreement, row counts measure retriever activity, relevance judgments measure effectiveness.

- **Rounding rule:** \
  *Section 5.1:* \
  `"It is worse at nDCG@10 by 0.001 to 0.011 on five collections. The exception is FiQA, where OR over every token is better by 0.009 nDCG@10 and 0.013 Recall@100, at 5.6 times the cost."` \
  Right. In [Table 7](file:///Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/paper/main.tex#L341-L372) (`tab:bm25`), ArguAna nDCG@10 differences are $0.484 - 0.473 = 0.011$ (formerly printed as 0.010), and FiQA Recall@100 differences are $0.521 - 0.508 = 0.013$ (formerly printed as 0.012). Both now match the stated rule (differences of printed 3-decimal values).

- **Runs-not-lists:** \
  *Abstract:* \
  `"In 174 further query runs the keyword list was nonempty but shared nothing with the dense list, mostly a short list on a large corpus."` \
  Right. Specifies query runs rather than keyword lists.

- **Nonempty counterpart condition:** \
  *Contributions (item 1):* `"with two retrievers an empty list can never be missed while the other list is nonempty;"` \
  *Section 2:* `"So with two retrievers, as long as the other retriever returned something, the test has no false negatives for an empty list; everything it gets wrong is in the other direction, a ceiling over a nonempty list."` \
  *Section 8 (Limitations):* `"and the guarantee that an empty list is never missed needs two retrievers and a nonempty counterpart;"` \
  Right. All three instances state the necessary condition that the counterpart list must return documents.

---

### 2. What did the edits break?

- **Table and Section references:** All `\ref` targets resolve to existing labels. [Table 1](file:///Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/paper/main.tex#L98-L113) through [Table 6](file:///Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/paper/main.tex#L268-L287) in the body and [Table 7](file:///Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/paper/main.tex#L338-L372) (`tab:bm25`) and [Table 8](file:///Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/paper/main.tex#L374-L393) (`tab:shared`) in Appendix A point to the intended tables. References to sections correctly reflect the relocation of Related Work to Section 7.
- **Numbers in prose:** Every edited number ($0.011$, $0.013$, $12.8\%$, $41.1\%$, $88.9\%$, $124\text{ of }378$, $39\text{ runs}$) is directly supported by [Table 3](file:///Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/paper/main.tex#L176-L195), [Table 7](file:///Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/paper/main.tex#L338-L372), or [natural_lengths.json](file:///Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/natural_lengths.json).
- **Term definitions:** No term is used before its definition. *Row counts* is defined in Section 1; *at the ceiling* and *singleton* in Section 2; *content tokens* in Section 4; *self-match* in Section 5.3.
- **Scope of claims:** Abstract, contributions, Section 6 ("What to log"), Section 8, and Section 9 claim only zero overlap from scores, requiring row counts to identify empty or short lists, exactly matching the body.
- **New Related Work citations:** All six references are cited accurately: \citet{kumaran2007shorter} and \citet{bendersky2008verbose} for reducing verbose queries; \citet{nuray2006ranking} for ranking systems by consensus without relevance judgments; \citet{aslam2001metasearch} for metasearch models; and \citet{chen2022hybrid} and \citet{wang2021interpolation} for BM25 dense combinations on BEIR.

---

### 3. Remaining readability stops (ranked by expected impact)

1. **Orphaned TREC-COVID sentence at the end of Section 5.5.** \
   *Quote:* `"On TREC-COVID the buggy hybrid is 0.027 to 0.039 below \textsc{dense}, significant for bge ($p = 0.043$), on a difference carried by the 13 queries with a nonempty list."` \
   *Problem:* The paragraph's topic sentence is `"The buggy hybrid's 12 wins over the repaired one are mostly abstention."` All 12 wins are accounted for (8 not above dense, 4 above dense). This closing sentence was left behind when the earlier NFCorpus vs. TREC-COVID contrast was trimmed. For bge and e5 on TREC-COVID, the buggy hybrid lost to the repaired hybrid, so asserting that buggy was below dense across all three encoders does not belong under this topic sentence. \
   *Rewrite:* Delete the sentence, or fold it into the NFCorpus contrast: \
   `"Only on NFCorpus (all three encoders) and SciFact with bge is the buggy hybrid above \textsc{dense} as well (by 0.008 to 0.014 on NFCorpus, where 86 of the 159 nonempty lists held four or more documents), whereas on TREC-COVID its 13 nonempty lists pulled it 0.027 to 0.039 below \textsc{dense} (significant for bge, $p = 0.043$)." `

2. **Inconsistent terminology between "content tokens" and "content words" in Section 5.1.** \
   *Quote:* `"Every quoted token is one more condition a single document must meet; stopwords are met almost everywhere; the content words are the conditions that fail."` \
   *Problem:* Section 4 defines *content tokens*, and the adjacent sentences use `"Content tokens per query"` and `"by content tokens"`. \
   *Rewrite:* `"Every quoted token is one more condition a single document must meet; stopwords are met almost everywhere; the content tokens are the conditions that fail."`

3. **Indefinite singular vs. plural list mismatch in Section 5.2.** \
   *Quote:* `"On the three largest collections a list of one to three documents was disjoint from the dense top 100 on 12.8, 41.1 and 88.9\% of runs (124 of 378 pooled)."` \
   *Problem:* Attaches a singular indefinite subject (`"a list"`) to three separate percentages. \
   *Rewrite:* `"On the three largest collections, keyword lists of one to three documents were disjoint from the dense top 100 on 12.8, 41.1 and 88.9\% of runs (124 of 378 pooled)."`

4. **Imprecise appendix pointer in Section 5.5.** \
   *Quote:* `"the mean number of documents both retrievers returned rose from at most 4.0 per query (Appendix~\ref{app:full}) to between 19.0 and 43.7 in every collection--encoder pair."` \
   *Problem:* Points generically to Appendix A, whereas Section 5.1 points specifically to `(Table~\ref{tab:bm25})`. [Table 8](file:///Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/paper/main.tex#L374-L393) (`tab:shared`) is the dedicated table for shared counts. \
   *Rewrite:* `"the mean number of documents both retrievers returned rose from at most 4.0 per query (Table~\ref{tab:shared}) to between 19.0 and 43.7 in every collection--encoder pair."`

5. **Disorienting section pointer for the stopword drop in Section 7.** \
   *Quote:* `"which is what the stopword drop in Section~\ref{sec:found} does crudely."` \
   *Problem:* Resolves to Section 3.2 ("How it was found, and what the scores had already said"), where the fix paragraph was appended after `\subsection{The fix}` was removed. \
   *Rewrite:* Point to Section 4 where content tokens are specified: \
   `"which is what the content-token drop in Section~\ref{sec:setup} does crudely."`

---

### 4. The title against the content

The title promises a zero-overlap test for hybrid retrieval, which the paper fully delivers; while the if-and-only-if equivalence requires $K \le k$ and unweighted RRF, an arXiv title does not need to state parameter bounds that the abstract defines in its third sentence.

---

### 5. Post it?

A cs.IR reader will finish this version: the mathematical scope of the $1/k$ bound is exact, the distinction between zero overlap and retriever failure is rigorously kept throughout, and the experimental results across all 18 pairs are completely accounted for. The single remaining change with the highest value is fixing the orphaned TREC-COVID sentence at the end of Section 5.5 (Item 1 above) so the paragraph on the buggy hybrid's 12 abstention wins ends coherently. Once that sentence is resolved, post it.
