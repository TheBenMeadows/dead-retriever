### Findings Ranked by Expected Impact

1. **Defensive micro-accounting in Section~\ref{sec:effect} re-invites the desk-reject verdict.** Section~\ref{sec:effect} (lines 311–312) spends 40 lines across two massive paragraphs litigating every pairwise loss where the buggy hybrid beat the repaired hybrid. It reads like a courtroom defense rather than an empirical analysis.
2. **Appendix~\ref{app:negative} directly sustains the journal editor's critique.** The notes on recency decay (7 queries) and title prepending (15 queries) are private-engine debugging notes that admit they "say nothing about the techniques in general." They add zero empirical weight and confirm the impression of "personal experiences."
3. **Pooling contradiction in Section~\ref{sec:rowcount}.** Line 224 asserts that "a short exact-match list was disjoint... on 12.8, 41.1 and 88.9% of runs (124 of 378 pooled)." However, line 222 defined this pool as combining both builders (612 buggy AND + 114 fixed OR). The fixed builder is an OR builder, not an exact-match list.
4. **Premature empirical leak in Section~\ref{sec:ceiling}.** Line 65 cites `Table~\ref{tab:prod}` and discusses 10 private replayed queries inside the derivation of the theoretical property, two sections before Section~\ref{sec:incident} introduces the production setup.

---

### 1. Readability, with Evidence

#### Paragraphs Requiring Multiple Reads
* **Section~\ref{sec:effect}, line 309:**
  > *Quote:* "The two significant gains over \textsc{dense} are on ArguAna, the one collection where BM25 alone (0.484) is above an encoder at nDCG@10, e5 (0.447), and level with another, nomic (0.483): the repaired hybrid gains 0.085 for e5 and 0.034 for nomic, and loses 0.035 for bge, the encoder BM25 does not match, also significantly."
  > *Rewrite:* "On ArguAna, BM25 alone achieves 0.484 nDCG@10, matching nomic (0.483) and exceeding e5 (0.447). Consequently, fusing the repaired keyword retriever significantly improves both encoders (+0.085 for e5, +0.034 for nomic), while significantly degrading bge (−0.035), whose dense baseline (0.641) far exceeds BM25."
* **Section~\ref{sec:effect}, line 311:**
  > *Quote:* "Over the whole of SciFact, \textsc{hybrid-and} and \textsc{dense} differ by at most 0.003 nDCG@10 and 0.000 Recall@100 as printed (0.0022 and 0.0000 before rounding), all of it from the six queries with a nonempty keyword list, and on SciDocs, with 942 empty lists, by at most 0.001 in each (0.0017 before rounding)."
  > *Rewrite:* "On SciFact and SciDocs, where the buggy builder returned nothing for 98.0% and 94.2% of queries, \textsc{hybrid-and} is functionally identical to \textsc{dense}: printed metrics differ by at most 0.003 on SciFact and 0.001 on SciDocs, driven entirely by the rare queries that returned keyword results."

#### Sentences Carrying Multiple Numbers Per Clause
* **Section~\ref{sec:leg}, line 183:** Dumps 10 raw numbers across parallel clauses: "8.7 content tokens per query on SciFact, 7.3 on SciDocs... against empty rates of 98.0, 94.2...". 
  * *Rewrite:* "Empty rates track content-token counts monotonically across the five collections, declining from 98.0% (SciFact, 8.7 content tokens) down to 50.8% (NFCorpus, 2.5 content tokens; Table~\ref{tab:legs})."
* **Section~\ref{sec:leg}, line 185:** Nested parenthetical: "(13.6 against 4.1\,ms on SciFact, 2.6 against 1.2 on NFCorpus, 905 against 52 on ArguAna, whose queries average 195 tokens)".
  * *Rewrite:* "Dropping stopwords reduces latency by $2.2\times$ to $18\times$ (e.g., 52\,ms vs. 905\,ms on ArguAna)."
* **Section~\ref{sec:rowcount}, line 224:** "0 of 18 on SciFact (5.2k documents), 13 of 330 on NFCorpus (3.6k), 18 of 141 on SciDocs (26k), 90 of 219 on FiQA (58k) and 16 of 18 on TREC-COVID (171k; six distinct queries, each run under three encoders)."
  * *Rewrite:* Move these per-collection breakdowns into Table~\ref{tab:excess} or Figure~\ref{fig:length} rather than inlining five data points with corpus sizes.

#### Residual Machine-Written Patterns
* **Banned vocabulary leak:** Line 314 contains the forbidden word: *"A monitor for overlap and activity and a verdict on retrieval effectiveness are different instruments."*
* **Nested parentheticals:** Line 307 nests an explanation of rounding inside an exception: `(one significant; the ninth, NFCorpus with bge, by 0.0006, which the table rounds to a tie)`. 
* **Pre-empting phantom objections:** Line 149 explains: *"FiQA was run with and without the rule and every one of its reported figures is identical, so none of the 55 affected a result."* If it has zero effect, state the filtering rule once without defending why it did not change the decimals.

---

### 2. Correctness After the Rewrite

* **Abstract run vs. list confusion (Line 23):** The abstract states: *"It also appeared over 174 nonempty keyword lists that shared nothing with the dense list"*. The keyword list is deterministic and encoder-independent. The number 174 refers to hybrid query *runs* across the 3 encoders, not 174 distinct keyword lists.
* **Section~\ref{sec:rowcount} vs. Setup pooling (Line 224):** Line 224 characterizes the 378 runs on larger corpora as *"a short exact-match list"*, but line 222 explicitly defines that pool as containing both builders.
* **Section reference ordering (Line 42):** Section~\ref{sec:intro} states: *"It says what a system that fuses should log (Section~\ref{sec:log}), within the limits of Section~\ref{sec:limits}."* Section~\ref{sec:log} precedes Section~\ref{sec:limits}; phrasing it as "within the limits of Section~\ref{sec:limits}" creates a disjointed forward dependency.
* **Forward reference in Section~\ref{sec:ceiling} (Line 65):** Line 65 cites `Table~\ref{tab:prod}` before Section~\ref{sec:incident} exists. Remove the parenthetical `(Table~\ref{tab:prod})` and keep Section~\ref{sec:ceiling} strictly theoretical.

---

### 3. Structure

* **Leading with property works:** Demoting the incident to Section~\ref{sec:incident} is successful for an arXiv cs.IR audience. However, purge all specific incident forward-references (e.g., line 65) from Section~\ref{sec:ceiling}.
* **Section~\ref{sec:incident} is fragmented:** Lines 80–129 contain four separate subheadings (\S 4.1 to \S 4.4) across only 50 lines of prose. Merge them into two subsections: *System and Failure Mode* (\S 4.1+\S 4.2) and *Detection and Fix* (\S 4.3+\S 4.4).
* **Section~\ref{sec:log} placement:** Fold Section~\ref{sec:log} directly into Section~\ref{sec:conclusion} as a bulleted subsection (*Practical Recommendations for Production Fusion*). Having Section 7 (*What to log*), Section 8 (*Limitations*), and Section 9 (*Conclusion*) as three consecutive two-paragraph sections creates a staccato exit.
* **Cuts to reach 16 pages:**
  1. Cut Appendix~\ref{app:negative} entirely (~1.2 pages).
  2. Drop Tables~\ref{tab:full-bge}, \ref{tab:full-nomic}, and~\ref{tab:full-e5} (~3 pages). Tables~\ref{tab:ndcg} and~\ref{tab:recall} already provide the complete nDCG and Recall results for all 18 pairs. Host the full BM25 and latency dumps in the repository.
  3. Compress line 311 in Section~\ref{sec:effect} by 50% (~0.5 pages).

---

### 4. Title

Current: *"A Score Ceiling in Reciprocal Rank Fusion Shows When Two Retrievers Agree on Nothing"*
* **Evaluation:** Accurate to the derivation ($K \le k \implies \max s(d) \le 1/k \iff$ zero overlap), but "Agree on Nothing" sounds informal and buries the diagnostic value.
* **Alternative 1 (Plain):** *Detecting Zero Retriever Overlap in Reciprocal Rank Fusion*
* **Alternative 2 (Naming the finding):** *The $1/k$ Ceiling: Detecting Disjoint and Silent Retrievers in Reciprocal Rank Fusion*

---

### 5. Prior Art

* **(a) RRF bounded at $1/k$ on zero overlap:**
  * \citet{cormack2009rrf} defined RRF ($k=60$) empirically.
  * \citet{bruch2023fusion} analyzed RRF score curves, monotonic properties, and convex combinations, but did not formulate the $1/k$ ceiling as a zero-overlap boundary.
  * Elasticsearch (8.8+) and OpenSearch RRF documentation note that a document appearing in only one retriever has maximum score $1/(k+0) = 1/60 \approx 0.0167$. However, no publication or engineering document has framed $\max s(d) \le 1/k$ as a formal zero-overlap test.
* **(b) Fused scores / per-retriever counts in production monitoring:**
  * \citet{cooper1998monitoring} established retrieval transaction logging (zero-hit tracking).
  * Industrial federated search systems (e.g., \citealp{shokouhi2011federated} [Foundations and Trends in IR]) monitor per-vertical result counts. Monitoring fused score ceilings as an automated fault detector appears novel.
* **(c) Silently inert retriever in hybrid search:**
  * \citet{sculley2015hidden} (*Hidden Technical Debt in Machine Learning Systems*, NeurIPS 2015) formalized "silent component failure" and "dead components" in ML pipelines. Citing this connects the SQLite bug to established ML engineering failure classes.

---

### 6. Would You Post It?

**Yes, post it after structural trimming.** The theoretical derivation is clean, the 22,362 runs are rigorously audited, the ArguAna self-match boundary is an insightful counterexample, and the finding that repairing BM25 significantly degrades RRF in 5 of 18 pairs is a valuable cautionary result for hybrid search practitioners. The single change that would most improve readability is cutting Appendix~\ref{app:negative} and condensing the defensive accounting in Section~\ref{sec:effect}: the paper should read as an objective empirical investigation of rank fusion boundaries, not a post-mortem justifying a private software bug.
