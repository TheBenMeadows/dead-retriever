### 1. Verification of Round 2 Fixes

All 30 hunks in [diff-since-round7.patch](file:///Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/review/round8/diff-since-round7.patch) held; none introduced an error. Specifically:

- **Abstract and §\ref{sec:conclusion}**: The qualification *"with two retrievers and a dense list that was never empty"* accurately reflects why singleton scores sum to at least $1/k$ without false negatives. The sentence covering the 174 disjoint runs and the 2 runs with deep overlap ($r_1 r_2 \ge 60^2$) correctly accounts for all 176 nonempty keyword runs at the ceiling across both builders in [keyword_facts.json](file:///Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/keyword_facts.json) and [natural_lengths.json](file:///Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/natural_lengths.json).
- **§\ref{sec:ceiling}**: The statement *"so a nonempty list at the ceiling has maximum exactly $1/k$"* is correct because a nonempty input list guarantees at least one rank-0 document scoring $s(d) \ge 1/k$. Splitting the rank-product explanation (*"because that document's rank product is 0"*) cleanly separates the rank-0 case ($r_1 r_2 = 0 < k^2$) from the general bound at $K \le k$ ($(K-1)^2 < k^2$).
- **§\ref{sec:results} and Appendix**: The Results opener points correctly to Tables 5 and 6 and Appendix A. The text updates in §\ref{sec:leg} (*"Outside ArguAna..."*), §\ref{sec:rowcount} (*"On the 294 of SciFact's 300 queries..."*), and §\ref{sec:effect} (pointing to Table 8, folding the TREC-COVID contrast with $p = 0.043$, and wrapping the ArguAna block in `\sloppy`) agree exactly with Table 3, [significance.json](file:///Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/significance.json), and the underlying result files.
- **§\ref{sec:related} and Appendix B**: Wang et al. (2021) on MS MARCO and Chen et al. (2022) on BEIR are accurately distinguished. The summaries of Nuray & Can (2006) and Kumaran & Allan (2007) / Bendersky & Croft (2008) match their source contents. The CPU reproduction note in Appendix B is strictly restricted to the four bge and nomic pairs.

### 2. The Title

Yes: it specifies the exact mathematical condition ($1/k$ ceiling in RRF) and its precise operational meaning (a test for zero overlap between retrieved lists, rather than an empty-retriever or system-health diagnostic).

### 3. Page One Rejections

None.

### 4. Recommendation and Retrospective

Yes, post it plainly to arXiv (cs.IR) and Zenodo. The formal conditions ($K \le k$ equivalence versus $K > k$ one-sided detection) are rigorously bounded, the incident narrative and FTS5 failure mechanism are concrete, the empirical validation across 22\,362 runs over six BEIR collections and three encoders is fully audited, and the literature boundaries are properly drawn.

A different approach—framing this as an algorithmic benchmark exploring parameter grids ($k$, $K$, score-weight sweeps) or adaptive fusion baselines—would have gained conventional placement within standard evaluation tracks (such as SIGIR short or resource papers). However, it would have cost the paper its crisp operational identity, burying an immediately actionable, zero-cost operational diagnostic beneath routine tuning tables.
