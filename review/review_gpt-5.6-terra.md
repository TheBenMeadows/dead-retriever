## Major revision required

1. **The central diagnostic is overstated for \(K>k\), including in the abstract and checklist.** The exact result at `paper/main.tex:39-47` is correct: for duplicate-free lists of depth at most \(K\), \(2/(k+K-1)>1/k\) iff \(K\leq k\). Thus \(\max_d s(d)\leq1/k\) excludes every multi-leg document, provided at least one result exists.

   The weak-form claim at `paper/main.tex:51` is not sufficient for the interpretation given. With \(K>k\), a two-leg document at rank \(k\) in both lists has score \(2/(2k)=1/k\). If each leg’s rank-0 document is otherwise distinct, the maximum remains \(1/k\) **despite a shared document**. Therefore “a maximum of exactly \(1/k\) still means the top fused document was found by one retriever at rank 0” is only partly true: at least one maximizer is singly credited, but it does not exclude another maximizer or lower-ranked document with multi-leg credit.

   More fundamentally, even when \(K\leq k\), the theorem diagnoses **zero top-\(K\) overlap**, not an empty retriever. “Across a set … [it] is the signature of a retriever that returns nothing” (`main.tex:22`, `49`, `142`) is an unsupported probabilistic assertion. Two functioning but systematically disjoint retrievers, incompatible document IDs, filtering, timeouts, or a shallow lexical candidate set yield the same score pattern. Recast the contribution as a score-only *screen for zero overlap*, whose empty-leg diagnosis requires the row-count telemetry that the paper subsequently advocates.

2. **The NFCorpus false-positive explanation is not identified by the released evidence.** The count inference in `main.tex:128` is valid under this runner: an empty keyword leg necessarily produces `at_ceiling`, because dense contributes a rank-0 score of \(1/k\); hence \(E\subseteq C\), and the rate difference is \(|C\setminus E|\). The raw JSON supports the stated three pre-fix and two post-fix queries. The sets cannot differ in both directions here.

   But those extra ceiling cases do **not** establish “returned documents that happened to share nothing with the dense top 100.” Under \(K=100>60\), they may contain deep overlap whose total RRF credit never exceeds \(1/k\); the rank-\(k\)/rank-\(k\) example above is a counterexample. The released aggregate `multi_leg_docs_mean` cannot classify those individual queries. Call the rate difference an *unconditional excess ceiling-event rate*, not a “false-positive rate” without specifying its denominator; remove the claimed mechanism or release per-query diagnostics.

3. **“Flatness” conflates absolute and relative gaps.** At `main.tex:31`, the exact absolute gap is
   \[
   \frac{1}{k+r}-\frac{1}{k+r+1}=\frac{1}{(k+r)(k+r+1)},
   \]
   which is \(1/k^2\) to first order for fixed \(r\). That part is right. But “adjacent ranks differed by about 1.4%” is a relative statement. Relative to the higher score, the gap is \(1/(k+r+1)\), first-order \(1/k\), not \(1/k^2\). State which quantity justified the recency argument.

4. **The public numbers are correctly transcribed; the private table is not auditable.** Every Table 2/Appendix-table number and the numerical comparisons in `main.tex:111-130,157-163` round to the four JSON files. No public-results mismatch found. Table 1 and the incident/negative-result timings and counts (`main.tex:29-31,78-84,94-96`) have no supporting artifact, so they cannot satisfy the stated “every number is in the result files” standard. At minimum, provide a machine-readable aggregate-only production-results file and a script that produces Table 1.

5. **Several effectiveness claims imply statistical evidence that is absent.** “Indistinguishable” in the abstract (`main.tex:22`) and “within noise” (`main.tex:130`) need paired per-query test results, confidence intervals, or repeated stochastic runs. The released files contain only single mean metrics. The defensible statement is the observed direction and magnitude, not equivalence or noise. Similarly, “failure depends on query length exactly as it did in production” (`main.tex:128`) is causal overreach: collection, domain, corpus, and query style all change simultaneously.

6. **The code reproduces the FTS5 bug, but the diagnostic API claims more than it implements.** `fts_query(..., "and_quoted")` space-joins individually quoted phrases (`hybrid.py:46-51`), which FTS5 indeed reads as implicit AND; the paper’s syntax account is correct. Catching every `sqlite3.OperationalError` and returning `[]` (`hybrid.py:66-73`) also silently converts database failures—not merely malformed MATCH syntax—into the purported symptom.

   `ceiling_report` correctly counts multi-leg documents (`hybrid.py:123-132`), but its docstring asserts that no multi-leg document implies the ceiling without accepting or checking depth \(K\). It is false for the paper’s \(K=100,k=60\) setting. It also reports `at_ceiling=True` for two configured but wholly empty legs. Finally, `HybridRetriever(k=...)` may use a nondefault fusion constant while callers of `ceiling_report` silently test against 60; the BEIR script happens to use 60 throughout.

   `rrf_fuse` prevents duplicate credit within a leg (`hybrid.py:104-108`), but a duplicate still consumes a rank because `enumerate` advances. It also does not itself enforce depth; the runner does. That is acceptable for this experiment, but not the general contract claimed in the prose.

7. **Bibliography and related work need correction and scope.**
   * `refs.bib:16-23` cites the journal version of Bruch, Gai, and Ingber as 2023. It is *TOIS* 42(1), 2024, Article 20. The cited paper supports the fusion-comparison sentence, but the bibliographic year is wrong.
   * `refs.bib:33-39` truncates Demian Gholipour **Ghalandari**’s surname.
   * `xiao2023cpack` supports the BGE family, not specifically the v1.5 checkpoint used. Cite the checkpoint model card/revision and record revisions for both encoders.
   * “Most hybrid-search implementations” retain \(k=60\) (`main.tex:134`) has no evidence or citation; delete or support with a reproducible implementation survey.
   * Add Luan et al., *Sparse, Dense, and Attentional Representations for Text Retrieval* (TACL 2021), for the sparse–dense complementarity premise; and Cooper, *Design Considerations in Instrumenting and Monitoring Web-Based Information Retrieval Systems* (JASIS 1998), for the monitoring claim. The present related-work section has no IR monitoring/failure-analysis lineage.

8. **Cut repetition and move limitations forward.** The “only plausible” language in `main.tex:49` and the prescriptive certainty in `main.tex:142` are stakes inflation, not results. State at the first ceiling claim that it detects non-overlap and requires per-leg telemetry to attribute cause. The private, tiny-sample limitation belongs in the incident and negative-results sections, not only at `main.tex:136-138`.

### Sources:
- [Bruch, Gai, and Ingber, *An Analysis of Fusion Functions for Hybrid Retrieval*](https://ir.webis.de/anthology/publications/rec%2Bjournals%2Btois%2BBruchGI24)
- [SQLite FTS5 query-syntax documentation](https://www.sqlite.org/fts5.html)
- [Luan et al., *Sparse, Dense, and Attentional Representations for Text Retrieval*](https://aclanthology.org/2021.tacl-1.20/)
- [Cooper, *Design Considerations in Instrumenting and Monitoring Web-Based Information Retrieval Systems*](https://ideas.repec.org/a/bla/jamest/v49y1998i10p903-919.html)
