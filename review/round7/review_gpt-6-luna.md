## 1. Did the fixes hold?

- **Health overclaim:** The abstract now says, “The test measures overlap, not health: two nonempty lists that share nothing produce the same ceiling as an empty list, and per-retriever row counts tell the two cases apart.” That is the right distinction. The incident account also no longer says the scores diagnosed a broken retriever.
- **Rounding:** The revised comparison says, “It is worse at nDCG@10 by 0.001 to 0.011 on five collections. The exception is FiQA, where OR over every token is better by 0.009 nDCG@10 and 0.013 Recall@100.” Those are differences of the printed table values. The other corrected figure is also handled: “one of the nine gains, NFCorpus with bge, is 0.0006, inside the table’s rounding.” That appropriately identifies the unrounded difference behind the printed tie.
- **Runs, not lists:** The abstract now says, “In 174 further query runs the keyword list was nonempty but shared nothing with the dense list.” Correct unit and claim.
- **Nonempty counterpart:** The derivation now says, “So with two retrievers, as long as the other retriever returned something, the test has no false negatives for an empty list.” Correct. But the condition is still omitted in the abstract and conclusion; see below.

## 2. What did the edits break?

The `Table~N` and `Section~N` references point to the corresponding sections and tables. The moved definitions are in place before use: in particular, “content tokens” is defined in the keyword-retriever setup before the results use it. The reported counts and effectiveness comparisons have supporting tables, captions, or stated result-file sources.

Two claims still outrun their stated conditions:

- Abstract: “the ceiling missed none of those empty lists, as the derivation requires with two retrievers.” Conclusion: “the ceiling missed no empty keyword list in 22\,362 runs, as it must with two retrievers.” The guarantee requires the *other* list to be nonempty; if both lists are empty, the fused maximum is undefined. The experiments satisfy the condition, but both general explanations should say so.
- Conclusion: “The scores can say whether two retrievers agreed on anything.” That is exact only for $K \le k$; at $K>k$, the paper’s own two FiQA cases show that overlap can be hidden. Rewrite: “At $K \le k$, the scores certify zero overlap at the ceiling; at greater depth, count shared documents directly.”

The new Related work paragraph has two attribution problems. “The BEIR hybrids of \citet{chen2022hybrid} and \citet{wang2021interpolation} measure what BM25 adds to dense retrievers on BEIR” incorrectly groups Wang et al. (2021) as a BEIR study; cite it for BM25 interpolation in passage retrieval, not as a BEIR result. Also, Kumaran and Allan and Bendersky and Croft support the motivation to shorten or analyze verbose queries, but not the stronger claim that failure of a *conjunctive keyword query* on verbose input is an old observation. Narrow that sentence to query shortening and verbose-query analysis.

## 3. Remaining readability stops

- “With two retrievers it must.” Rewrite: “With two retrievers, an empty list forces the fused maximum to $1/k$ if the other list is nonempty.”
- “These are read from the lists as fused.” Rewrite: “The runner computes these diagnostics from the retriever outputs and the fused list.”
- “The scores can say whether two retrievers agreed on anything.” Use the condition-qualified rewrite above.

## 4. Title

“The $1/k$ Ceiling: A Zero-Overlap Test for Hybrid Retrieval” omits the essential $K \le k$ condition for a zero-overlap conclusion; at $K>k$, a ceiling does not rule out deep overlap.

## 5. Post it?

A cs.IR reader can follow the derivation and the experiments, and the fixes largely held. I would not post this version until the abstract and conclusion state the nonempty-counterpart condition and the conclusion’s final claim is restricted to $K \le k$; that is the single highest-value change because it aligns the paper’s most visible claims with its theorem.
