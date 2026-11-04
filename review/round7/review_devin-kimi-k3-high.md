## 1. Did the fixes hold?

**Health overclaim — held.** Abstract now reads "the fused scores reveal when the two lists did not overlap," and keeps the explicit sentence: "The test measures overlap, not health: two nonempty lists that share nothing produce the same ceiling as an empty list, and per-retriever row counts tell the two cases apart." Section 2's heading paragraph is now "It is a statement about overlap, not about either retriever," and the new conclusion distributes responsibility correctly: "The scores can say whether two retrievers agreed on anything, the row counts can say what that means."

**Rounding rule — held.** The two changed differences now match printed-three-decimal arithmetic: "worse at nDCG@10 by 0.001 to 0.011" (printed 0.484−0.473=0.011 on ArguAna, 0.153−0.152=0.001 on SciDocs) and "better by 0.009 nDCG@10 and 0.013 Recall@100" (0.233−0.224, 0.521−0.508). The old 0.010/0.012 violations are gone.

**Runs-not-lists — held, and the counts close.** Abstract: "In 174 further query runs the keyword list was nonempty but shared nothing with the dense list"; body: "There were 176 such query runs, 164 under the buggy builder and 12 under the fixed one." 174 zero-overlap + 2 deep-overlap = 176, and the two deep-overlap runs are correctly assigned to hybrid_or (FiQA bge and e5 both show at_ceiling_rate 0.0030864 ≈ 2/648). The abstract's "In two runs under the repaired builder, the lists shared one document at deep ranks" matches.

**Nonempty counterpart — held in three of four places it matters.** Section 2: "as long as the other retriever returned something, the test has no false negatives." Limitations: "needs two retrievers and a nonempty counterpart." Contribution list: "can never be missed while the other list is nonempty." But the abstract still says "the ceiling missed none of those empty lists, as the derivation requires with two retrievers" — the one place the condition was dropped after having been added everywhere else.

**New error introduced by a fix:** yes, one, in the mathematics paragraph. "A maximum of $1/k$ therefore rules out a shared document at rank 0 of either list at any depth, and at $K \le k$ it rules out every shared document, because $r_1 r_2 \le (K-1)^2 < k^2$" — correct. "Ranks 60 and 60 score exactly $1/60$" (2/120) and "ranks 90 and 90 score $2/150$" — correct. The rewritten derivation is clean; the error is elsewhere (§2 below).

## 2. What the edits broke

**The Wang et al. citation is misattributed in two places (highest impact).** Related work: "\citet{wang2021interpolation} and \citet{chen2022hybrid} measure what BM25 adds to dense retrievers on BEIR"; Section 5.5: "the BEIR hybrids of \citet{chen2022hybrid} and \citet{wang2021interpolation} gain from BM25 under different fusion choices than this one." Chen et al. (ECIR 2022) did evaluate zero-shot on BEIR. Wang, Zhuang & Zuccon (ICTIR 2021) evaluated BM25 interpolation on MS MARCO passage ranking and TREC Deep Learning — not BEIR. Two sentences credit BEIR results to a paper that has none. Fix: "…\citet{chen2022hybrid} measure it on BEIR, and \citet{wang2021interpolation} on MS MARCO/TREC DL, under different fusion choices…" and drop "BEIR hybrids of" in 5.5. The other five new citations (Kumaran & Allan, Bendersky & Croft, Nuray & Can, Aslam & Montague, the RRF/fusion context) are accurately described.

**References and anchors — otherwise clean.** No dangling `Table~N` or `Section~N`: `sec:fix` was deleted with it (the fix paragraph now lives at the end of `sec:found`, which is exactly where Related work's "the stopword drop in Section~\ref{sec:found}" now points — correct). `app:negative` is gone from intro and Limitations; its pointer sentence landed in `app:run`. `tab:prod`, `tab:legs`, `tab:excess` (left/right), `tab:bm25`, `tab:shared`, `tab:sweep` all resolve and their quoted figures reconcile with the JSONs (Table 7 timings match the bge-side `mean_query_ms` values; the 12/6 win-loss split, six significant wins, 0.035/0.085/0.034 ArguAna deltas, and "0.027 to 0.039" TREC-COVID all check out).

**Terms before definition — clean.** "content tokens" is defined in Setup before use in §4.1 and Table 2's caption; "row counts" defined in the introduction before the body uses it; "singleton," "at the ceiling," "self-match" all defined before or at first use.

**Abstract/contributions/What-to-log/conclusion alignment** — consistent, except the abstract omission flagged in §1 (the abstract is now the only guarantee statement without the nonempty-counterpart clause; the conclusion has the same omission: "as it must with two retrievers").

## 3. Remaining readability stops

Two, both in or beside the diff:

- Abstract: "In 174 further query runs the keyword list was nonempty but shared nothing with the dense list, mostly a short list on a large corpus." 174 lists reduced to "a short list," and "further" points at a unit that just changed. Rewrite: "In 174 further runs the keyword list was nonempty yet disjoint from the dense list — usually a one-to-three-document list on one of the larger corpora."
- Table 3 header: "buggy builder, per encoder" sits over a first column whose caption says the count "does not depend on the encoder." Header to "buggy builder (encoder ranges)" or split the rule so "per encoder" spans only columns 3–4.

## 4. The title against the content

It promises what the paper delivers, with one implicit convention a clicking reader should know: the ceiling is $1/k$ only under zero-based ranks — under Cormack et al.'s original one-based formula it is $1/(k+1)$ — and the exact zero-overlap reading needs $K \le k$ (the one-sided form is all you get at the common $K=100>k=60$), both of which the title compresses away legitimately for a title.

## 5. Post it?

Yes — after one change. A cs.IR reader will finish this: the ceiling derivation is now stated tightly, the incident/production/sweep/ArguAna arc reads in order, the new two-table appendix plus per-encoder shared-counts table carry what the text discusses, and the prose no longer recites tables. Every audited number I re-derived from the attached JSONs reconciles, and the six-reference additions are right for five of six. The single remaining change with the highest value is the Wang et al. misattribution in §2 above: two sentences currently claim BEIR evidence from a paper that contains none, which is exactly the kind of slip a reader who knows that literature will catch and generalize from. One-line rewording in each place; then post it.
