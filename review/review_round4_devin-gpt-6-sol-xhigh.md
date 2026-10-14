## Corrections before submission

1. **The title and short heading overstate the theorem.** “Detects Zero Overlap” is an equivalence only when \(K\leq k\). The journal experiments use \(K=100>k=60\) and report two ceiling firings *with* overlap. Qualify the title or replace “detects” with wording that permits this failure. The operator advice’s “not agreeing near the top” is also imprecise: for two retrievers, a shared document exceeds \(1/k\) exactly when \(r_1r_2<k^2\).

2. **“A leg that is never empty and never useful” is false.** The ArguAna AND leg returned a relevant document for **one of 1,406** queries; its BM25-only nDCG@10 is **0.0004487**, not zero. Correct that subsection heading and the abstract’s “never useful” to “almost never retrieves a relevant document.” The equal dense and hybrid aggregate metrics establish no change in those metrics, not that every ranking is identical.

3. **The abstract overclaims the production history.** “Returned no results for most natural-language queries from the system’s first version until 2026-08-18” is not established by ten replayed queries on one shard, five of them conversational. “Nobody noticed” and “visible the whole time” likewise lack a longitudinal record. State what was observed and when it was diagnosed. Its “two working retrievers can return disjoint lists, and in the incident four of ten queries did” should say **two nonempty legs**: those four keyword lists came from the faulty builder.

4. **Section 6 has reproducible numerical errors.**
   - “13 of 330 on NFCorpus (**3.6k documents**)” implies **3.9%**, not the printed **3.6%** short-list ceiling rate; the next rates are 18/141 = 12.8%, 90/219 = 41.1%, and 16/18 = 88.9%.
   - SciFact’s largest \(\lvert\textsc{hybrid-and}-\textsc{dense}\rvert\) at nDCG@10 is **0.002193** (e5), not “at most 0.002.” SciDocs’s Recall@100 differences reach **0.0002** (bge and nomic), not “0.000”; the bge table itself prints 0.495 versus 0.496.
   - Raw OR is not strictly “within 0.008 nDCG@10” of filtered OR on five collections: ArguAna differs by **0.008368**. The quoted **2.6-to-18-times** latency range also excludes NFCorpus/e5, **2.331/0.937 = 2.49**. Round or phrase these as approximations.

The other requested aggregate checks agree with the attachments: \(3{,}727\) collection queries × three encoders × two hybrids = **22,362** runs; the five AND-empty counts, retained-token ordering, legs-table ranges, **164 + 12 = 176** excess ceilings, and pooled natural-length counts **137/726, 35/588, 4/6,636** follow. The effectiveness comparisons are **5/18** nDCG gains over dense, **9/18** Recall gains, and **12/18** cases where the buggy hybrid exceeds the repaired hybrid at nDCG; the named ArguAna, SciFact, TREC-COVID gains and FiQA loss range agree with the unrounded summaries. These are observed differences, not established improvements.

The inline files **cannot independently establish** “1,402 … one document … four” on ArguAna, “174 of the 176” with zero overlap, the **two FiQA shared documents at deep ranks**, or the sweep’s no-leak claim. Those require the omitted per-query or sweep records; check them before retaining the corresponding abstract sentences.

## Interpretation and citations

The five-collection ordering pairs mean **retained-token** counts with AND-empty rates; it does not isolate content words as a cause. Document length, corpus size, vocabulary and query type vary together, and short retained content terms are discarded. Likewise, the four nonzero short-list rates increase with corpus size **across different collections**, not under controlled changes to corpus size; “Expect more such queries on a large corpus” in the operator advice reads as a prediction these data cannot support.

ArguAna demonstrates self-matching when a **whole indexed argument** is submitted as the query. It does not establish that ordinary mailbox, notes or ticket searches “routinely” submit an indexed item’s text; confine that advice to systems accepting copied or near-verbatim indexed text. The distinction between a leg-health monitor and an effectiveness verdict **is supported**: overlap rises after repair while nDCG@10 rises in only 5/18 pairs.

Section 5 calls a title prefix “the cheapest form of document expansion” while citing **doc2query**, which predicts queries to add to documents. Call this a metadata prefix *distinct from* doc2query; that citation does not substantiate the claimed classification.

## Journal-fit priorities

1. **Require:** Report paired per-query confidence intervals or randomization tests for the effectiveness comparisons, particularly the five positive nDCG differences and TREC-COVID’s 50 queries, without treating three encoders on the same queries as independent replications.
2. **Require:** Explain the diagnostic’s incremental operational value over logging row counts and computing overlap directly, using the existing **176 excess firings and two \(K>k\) leaks** rather than a new experiment.
3. **Require:** Expand related work on retrieval monitoring and overlap diagnostics enough to locate the contribution beyond the elementary \(1/k\) derivation.
4. **Optional:** Move the two Section 5 feature trials out of the main argument and add one figure showing ceiling rate against natural keyword-list length; neither needs new experiments.
