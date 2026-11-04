The four correctness fixes hold in the body. Two restatements of the guarantee, one appendix sentence, and the new related-work citations do not.

## 1. The four fixes

**Health.** The abstract now says the scores "reveal when the two lists did not overlap" and that "The test measures overlap, not health: two nonempty lists that share nothing produce the same ceiling as an empty list, and per-retriever row counts tell the two cases apart." The introduction says a maximum of \(1/k\) "does not say that either list is empty" and that row counts "separate an empty list from a short one and from two full lists that happen to share nothing." Those sentences match Section 2. "The fused scores can show something narrower, and useful" still has no object (rewrite below). It does not restore a health claim.

**Rounding.** "It is worse at nDCG@10 by 0.001 to 0.011 on five collections. The exception is FiQA, where OR over every token is better by 0.009 nDCG@10 and 0.013 Recall@100." Those are the differences of the printed values in Table `tab:bm25` (ArguAna \(0.484-0.473\), SciDocs \(0.153-0.152\), FiQA \(0.233-0.224\) and \(0.521-0.508\)).

**Runs.** "In 174 further query runs the keyword list was nonempty but shared nothing with the dense list" and "In 174 of the 176 the two retrievers shared no document" both count query runs. The 176 are introduced as runs.

**Nonempty counterpart.** Section 2: "So with two retrievers, as long as the other retriever returned something, the test has no false negatives for an empty list." The contribution list has "while the other list is nonempty." Limitations: "needs two retrievers and a nonempty counterpart." The product paragraph is right: score \(> 1/k\) iff \(r_1 r_2 < k^2\); ranks 60 and 60 score \(1/60\); ranks 90 and 90 score \(2/150\); at \(K \le k\), \(r_1 r_2 \le (K-1)^2 < k^2\).

The same guarantee is then stated without the counterpart. Abstract: "as the derivation requires with two retrievers." Conclusion: "as it must with two retrievers." Section 4.2's "With two retrievers it must" is repaired by the next clause, "whenever the dense retriever returned anything."

## 2. What the edits broke

Every `Table~\ref` and `Section~\ref` still resolves. `sec:fix`, `app:negative`, and the three per-encoder table labels are gone, and nothing points at them. "Content tokens," "at the ceiling," and "row counts" are defined before the results use them. The abstract, "What to log," and the conclusion match the body on overlap versus row counts, on 5/13 and 2/5 at nDCG@10, and on the two deep FiQA shares. The \(K \le k\) and \(K > k\) logging rules are separate sentences and match Section 2.

Three breaks:

The results opener still says "Every condition for every collection--encoder pair is in Appendix A." Appendix A now has the three BM25 rows and the shared-document means. Dense and hybrid nDCG@10 and Recall@100 are in Tables `tab:ndcg` and `tab:recall` only. The appendix's own first sentence ("complete" those tables) contradicts the opener.

"That a conjunctive keyword query fails on verbose, natural-language input is an old observation: Kumaran and Allan (2007) and Bendersky and Croft (2008) both start from search engines doing badly on long queries and look for the few terms worth keeping, which is what the stopword drop in Section 3.2 does crudely." Both papers shorten or reweight verbose queries. Neither is about an AND of every token matching nothing, and a fixed stoplist is not their selector. Nuray and Can (2006) do rank systems by agreement with a fused ranking and without judgments; "the ceiling is a degenerate case of that idea" is not their result. Aslam and Montague (2001) do propose metasearch models; that clause is thin and accurate. Chen et al. (2022) do measure hybrid lexical–dense retrieval on BEIR. Wang et al. (2021) show that interpolating BM25 with a dense score helps on MS MARCO passage and TREC Deep Learning. "The BEIR hybrids of Chen et al. and Wang et al." and "measure what BM25 adds to dense retrievers on BEIR" put Wang on the wrong benchmark. The same BEIR pairing is in the last paragraph of Section 4.5.

"905 against 52 ms" sits beside Table `tab:bm25`'s 905.4 and 51.5.

## 3. Readability

"A maximum of \(1/k\) therefore rules out a shared document at rank 0 of either list at any depth, and at \(K \le k\) it rules out every shared document, because \(r_1 r_2 \le (K-1)^2 < k^2\)." The because-clause justifies only the second claim. Rewrite: "A maximum of \(1/k\) rules out a shared document at rank 0 of either list at any depth, because that document's rank product is 0. At \(K \le k\) it rules out every shared document, because \(r_1 r_2 \le (K-1)^2 < k^2\)."

"The fused scores can show something narrower, and useful." Rewrite: "The fused scores show whether any returned document came from both retrievers."

"SciFact's 0 of 18 is consistent with NFCorpus's rate, and the collections differ in more than size, so this is an ordering, not a demonstrated size effect." Rewrite: "At NFCorpus's 13/330 rate, SciFact's 0 of 18 is unsurprising, and these collections differ in more than size, so the rise across Table 3 is an ordering over five points."

## 4. Title

"A Zero-Overlap Test" omits the condition the certificate needs: \(\max s(d) \le 1/k\) is zero overlap only for \(K \le k\), and the paper's own runs use \(K = 100 > k = 60\), where two lists share a document under the ceiling.

## 5. Post it?

A cs.IR reader will finish this version: the ceiling argument, the four fixes in Section 2, and the tables agree. The one change worth making before posting is the new related-work wording: cite Kumaran and Allan and Bendersky and Croft for verbose-query reduction, and cite Wang et al. for interpolation on MS MARCO and TREC DL, leaving BEIR on Chen et al. Correcting the Appendix A opener and putting "and a nonempty counterpart" back into the abstract and conclusion can ride along; neither is the sentence a specialist will reject.
