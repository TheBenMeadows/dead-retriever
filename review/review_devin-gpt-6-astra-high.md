## 1. The central diagnostic claim exceeds the theorem

Section 2’s implication is correct under its definitions: positive \(k\), zero-based ranks, depth \(K\le k\), and one contribution per document per retriever. There is no counterexample under those assumptions. But **no overlap does not imply an empty retriever**, even across many queries. Two working retrievers can systematically retrieve disjoint documents. “Almost always share” requires evidence, not just a shared corpus.

The \(K>k\) weak-form claim is **false**. Set \(k=60,K=100\). Let two lists be disjoint except for a document at rank 60 in both. It scores
\[
2/(60+60)=1/60.
\]
Both lists’ rank-zero documents also score \(1/60\). Thus a maximum-scoring document can be shared, contradicting “the top fused document was found by one retriever at its rank 0.” A shared document at rank 99 instead scores \(2/159<1/60\), leaving the maximum unchanged.

What survives: with nonempty lists, a maximum of \(1/k\) requires every retriever’s rank-zero document to be exclusive; it does not exclude deeper overlap.

Move these restrictions into the abstract and replace the title/checklist’s diagnosis of emptiness with a warning requiring component-level confirmation. Also state that conventional one-based RRF has a singleton ceiling of \(1/(k+1)\); weighted or normalized variants need different thresholds. [main.tex](file:///Users/bemeadows/Projects/dead-retriever/paper/main.tex)

## 2. The false-positive counts are valid; their explanation and denominator are not

Let \(E\) mean keyword-empty and \(C\) mean ceiling-positive. Here dense always returns a nonempty list, so \(E\subseteq C\): empty keyword guarantees maximum \(1/60\). Consequently the sets cannot differ in both directions.

The unrounded results give, for either encoder:

- AND: \(|E|=164,\ |C|=167\), hence three false positives.
- OR: \(|E|=25,\ |C|=27\), hence two false positives.

But those extra queries need not “share nothing with the dense top 100”: the counterexamples above permit overlap. Aggregate mean overlap cannot establish their individual overlap counts. Save the per-query diagnostics and inspect these queries.

Three out of 323 is 0.929% of **all queries**, not the conventional false-positive rate. Among keyword-nonempty queries, that rate is \(3/159=1.887\%\); after fixing, \(2/298=0.671\%\). Label the denominator.

## 3. Flatness does not establish the proposed causal explanation

The absolute adjacent gap is
\[
\Delta_r=\frac{1}{(k+r)(k+r+1)}
       =k^{-2}+O(k^{-3})
\]
for fixed \(r\). That approximation is correct near the top. But “1.4% flatness” is a **relative** gap:
\[
\Delta_r/s_r=1/(k+r+1),
\]
approximately \(1/k\), not \(1/k^2\). At rank zero with \(k=60\), it is 1.639%.

Moreover, two identical live lists produce \(2/(k+r)\), with exactly the same relative flatness. The dead leg explains the observed singleton score scale, not uniquely the sensitivity to multiplicative recency penalties. Delete “that flatness was the dead leg” as a causal conclusion.

The prefix experiment was intentionally vector-only, with the keyword index unchanged. Calling it “confounded” contradicts its own description.

## 4. Code findings and reproducibility risks

- **FTS5 reproduction:** whitespace-separated quoted phrases implement implicit AND. Quoting is not itself the problem; the conjunction is. Regex tokens containing punctuation, such as `foo-bar`, can become multi-token FTS phrases, so “every quoted token” needs that qualification.
- **Error masking:** `KeywordIndex.search` catches every `sqlite3.OperationalError`, not just syntax errors. Operational failures become indistinguishable from genuine zero matches. Report these separately. [hybrid.py:37-74](file:///Users/bemeadows/Projects/dead-retriever/dead_retriever/hybrid.py)
- **Fusion:** duplicates contribute only at their first occurrence; later ranks retain their original indices. `rrf_fuse` itself enforces no depth; `HybridRetriever` supplies truncated lists. This satisfies the bound provided callers respect the depth contract.
- **Diagnostic:** `at_ceiling` tests `<= ceiling + eps`, not equality, and reports true when both configured lists are empty and `max_score=0`. Distinguish an empty union from equality. Dense being nonempty prevents this discrepancy in these BEIR runs. [hybrid.py:99-133](file:///Users/bemeadows/Projects/dead-retriever/dead_retriever/hybrid.py)
- **Runner:** title/text concatenation, Nomic prefixes, qrels filtering, and component depths show no evident condition-specific defect. BGE receives no recommended retrieval-query instruction; disclose this and test sensitivity before generalizing encoder comparisons.
- Cache reuse checks existence only, without validating text/order, preprocessing, model revision, or dimensions. Stale query caches can silently truncate evaluation through `zip`. Record fingerprints and assert lengths. [beir_run.py](file:///Users/bemeadows/Projects/dead-retriever/scripts/beir_run.py)

## 5. Numerical transcription is consistent; coverage and inference are not

Every displayed value in Tables 2 and 3 matches the supplied JSON at the shown precision. The BEIR collection sizes, quoted metric differences, percentages, and three-point SciFact recall gain also agree.

**Table 1 is not auditable from these files.** Neither are production counts, timings, corpus sizes, recency outcomes, prefix outcomes, or Appendix B’s runtime/hardware claims. Supply non-sensitive measurement records; otherwise identify these as incident-report measurements without released supporting data.

“Within noise” and “indistinguishable” lack paired uncertainty/equivalence analysis. Use measured differences instead.

The collection comparison does not isolate query length from vocabulary, corpus, and relevance differences. Likewise, AND→OR changes both conjunction and token filtering.

An omitted conclusion: hybrid-AND exceeds hybrid-OR in nDCG@10 on both BGE collections and Nomic NFCorpus. Restoring keyword coverage is not equivalent to improving retrieval. This does not invalidate component-health monitoring; it invalidates using these results to imply effectiveness gains.

## 6. References: attribution problems outweigh identifiable metadata errors

From existing knowledge, I identify no definite author/title/venue/year error among the twelve entries; this is not external bibliographic verification. Bruch’s 2023 TOIS citation is not inherently erroneous.

The Nomic and C-Pack papers do not document every version-specific inference setting; add release/model-card references. Cormack supports the experimental choice of 60, not “most hybrid-search implementations unchanged.” BEIR supports BM25’s competitiveness, not the asserted loss from dropping it in this system.

Add Lee, *Analyses of Multiple Evidence Combination*, for overlap in fusion; Gao et al., *Complementing Lexical Retrieval with Semantic Residual Embeddings*, for lexical/dense complementarity; and Cronen-Townsend et al., *Predicting Query Performance*, as adjacent query-level diagnostics, explicitly distinguished from component-health monitoring. [refs.bib](file:///Users/bemeadows/Projects/dead-retriever/paper/refs.bib)

## 7. Delete unsupported rhetoric

Cut “respectable retriever,” “the test costs nothing,” the copied-bug “second lesson,” and repeated claims that scores “had been saying so.”

Replace “a six-word query is broken, not selective”: legitimate restrictive queries can return nothing. Move the private-evidence limitation and absence of demonstrated effectiveness improvement earlier. Remove the repository placeholder before submission.
