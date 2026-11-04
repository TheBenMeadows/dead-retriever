## Findings, ranked

1. **The new related-work sentence misattributes BEIR evidence to Wang et al.** It says: “\citet{wang2021interpolation} and \citet{chen2022hybrid} measure what BM25 adds to dense retrievers on BEIR.” Chen et al. is the BEIR-era zero-shot-hybrid evidence; Wang et al. studies interpolation with BM25 for BERT dense *passage retrieval*, not BEIR. Revise to separate the claims, e.g.: “\citet{chen2022hybrid} evaluates zero-shot hybrid retrieval on BEIR, while \citet{wang2021interpolation} finds that interpolating BM25 can improve BERT dense passage retrieval.” The other five additions are used within their scope: Kumaran–Allan and Bendersky–Croft motivate verbose-query term selection; Nuray–Can ranks systems through fusion without relevance judgements; Aslam–Montague models metasearch combination; and Chen supports hybrid zero-shot retrieval.

2. **The Appendix A deletion left one false locator claim.** Results opens: “Every condition for every collection--encoder pair is in Appendix~\ref{app:full}.” That was true before the three full per-encoder tables were removed. The appendix now contains BM25-only results and shared-document means; dense and hybrid effectiveness remains in Tables~\ref{tab:ndcg} and \ref{tab:recall} in the body. Replace it with: “Tables~\ref{tab:ndcg} and \ref{tab:recall} give dense and hybrid effectiveness; Appendix~\ref{app:full} supplies the BM25-only results and shared-document counts.”

All explicit `Table~` and `Section~` references otherwise point to the intended material. The moved Related work section, contribution list, abstract, “What to log,” and conclusion preserve the theorem’s scope: exact zero-overlap diagnosis at \(K\leq k\), a one-sided implication plus direct overlap counting at \(K>k\), and row counts rather than fused scores for activity/health.

## 1. The four requested fixes

- **Health overclaim — fixed.** The abstract now says, “**This paper shows that the fused scores reveal when the two lists did not overlap**,” and immediately bounds that statement with “**With per-retriever depth \(K \le k\)**.” The introduction makes the non-health reading explicit: “**It does not say that either list is empty.**” This is now right.

- **Rounding — fixed.** The protocol says, “**Differences quoted in the text are differences of the printed three-decimal values unless a fourth decimal is given.**” The altered prose follows it: “**It is worse at nDCG@10 by 0.001 to 0.011**” and FiQA is “**better by 0.009 nDCG@10 and 0.013 Recall@100**,” matching the printed Appendix values.

- **Runs, not lists — fixed.** The abstract now says, “**In 174 further query runs the keyword list was nonempty but shared nothing with the dense list**.” That correctly uses the encoder-specific hybrid-run unit; the body distinguishes these 174 zero-overlap runs from the two \(K>k\) runs with hidden overlap.

- **Nonempty counterpart — fixed.** The qualification now says, “**If one of two lists is empty and the other is not**,” followed by “**as long as the other retriever returned something**.” That supplies the condition required for a fused maximum and the no-false-negative statement. I found no new error in these four repairs.

## 3. Remaining readability stops

- “**Among those short lists, the at-ceiling share is highest on the three largest collections (Table~\ref{tab:excess}, right); SciFact's 0 of 18 is consistent with NFCorpus's rate, and the collections differ in more than size, so this is an ordering, not a demonstrated size effect.**”  
  Rewrite: “Among one-to-three-document lists, the at-ceiling rate is highest on SciDocs, FiQA, and TREC-COVID (Table~\ref{tab:excess}, right). This is an ordering, not a size effect: SciFact’s 0 of 18 is compatible with NFCorpus’s rate, and the collections differ in more than corpus size.”

- “**That a conjunctive keyword query fails on verbose, natural-language input is an old observation: \citet{kumaran2007shorter} and \citet{bendersky2008verbose} both start from search engines doing badly on long queries and look for the few terms worth keeping, which is what the stopword drop in Section~\ref{sec:found} does crudely.**”  
  Rewrite: “Kumaran and Allan and Bendersky and Croft address verbose queries by identifying a smaller set of useful terms. The stopword drop in Section~\ref{sec:found} is a crude fixed-rule version of that reduction.”

## 4. Title

“The \(1/k\) Ceiling: A Zero-Overlap Test for Hybrid Retrieval” is accurate only with the \(K\leq k\) condition supplied by the paper, so the title omits the condition under which a ceiling proves zero overlap rather than merely failing to rule out deep overlap.

## 5. Post it?

A cs.IR reader can finish this version: the theorem, operational prescription, counterexamples, and effectiveness separation now remain aligned rather than competing for the same claim. Post after the highest-value remaining change: correct the Wang–Chen/BEIR sentence, because it is a concrete literature misattribution rather than a stylistic preference; also repair the stale Appendix locator before submission.
