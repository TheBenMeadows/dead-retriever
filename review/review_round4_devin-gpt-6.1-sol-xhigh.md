**Revise before submission.** The following claims need correction or narrower wording.

## 1. False sentences and unsupported scope

- **Section 6, “A leg that is never empty and never useful,” and the abstract:** “never useful” exceeds the evidence. The AND leg retrieves a relevant document on **one of 1,406 queries**; its unrounded nDCG@10 is **0.000448741**. Equality of the hybrid and dense aggregate metrics does not establish absence of every query-level contribution. Say “almost always nonrelevant” or “did not change the reported aggregate effectiveness.”

- **“What fusion did with an empty list”:** “differ by at most 0.002 nDCG@10” is not an exact bound on SciFact: e5 gives  
  \(0.7216220733-0.7194288840=0.0021931892\).  
  On SciDocs, “0.000 Recall@100” conceals differences of **−0.0002 for bge and +0.0002 for nomic**. These are rounded descriptions, not exact bounds or equality statements; identify them accordingly.

- **“The leg”:** “within 0.008 nDCG@10 … on five collections” needs the same rounding qualification: ArguAna differs by **0.0083675555**. “2.6 to 18 times slower” is not the range across all supplied timings: NFCorpus/e5 gives \(2.330779/0.937358 \approx 2.49\). Specify the timing run used to construct the range.

- **“Effectiveness is a separate question”:** “from at most 4.0” is a rounded maximum: NFCorpus/bge has **4.0061919505** shared documents per query. Again, avoid presenting rounded values as strict bounds.

- **Section 5:** Nogueira et al. supports document expansion by learned query generation, not the assertion that a heading prefix is “the cheapest form of document expansion.” Remove the superlative or supply its actual basis; the bibliography entry itself is not the problem.

- **Abstract:** “most natural-language queries … from the system’s first version until 2026-08-18” needs an identified evidentiary basis. The ten-query replay establishes the observed failure, while the builder’s history establishes that the defective code persisted; neither supplies a historical query denominator. Mark the lifetime claim as a retrospective inference.

## 2. Numerical audit

**Reproduced from the supplied material:**

- The legs table’s sizes, query lengths, empty rates and ceiling ranges agree with the JSON at displayed precision. The AND-empty counts are **294, 164, 0, 942, 530, 37**, in table order. The five-collection content-token ordering also reproduces.
- \(2\times3\times(300+323+1406+1000+648+50)=22,362\). These are repeated condition/encoder evaluations, not 22,362 independent queries.
- The buggy-builder excess counts, in **bge/nomic/e5** order, are NFCorpus **3/3/2**, SciDocs **7/6/5**, FiQA **35/37/43**, TREC-COVID **8/7/8**: total **164**. Fixed-builder excesses are **3/2/0**, **1/1/1**, **2/0/2**, respectively: total **12**. The stated live-leg percentages reproduce.
- Natural-length counts reproduce: **137/726 = 18.9%**, **35/588 = 6.0%**, **4/6,636 = 0.0603%**, rounded to 0.1%; the four-or-more total is **39**. The named short-list fractions reproduce.
- The effectiveness counts **5/18, 9/18 and 12/18** reproduce using unrounded values. The ninth Recall gain includes NFCorpus/bge, **+0.00058755**, invisible in the rounded table.
- Named gains and losses reproduce. In particular, ArguAna/e5 gains **0.059202**, not the 0.060 obtained by subtracting rounded cells; SciFact/nomic gains **0.004335**; the FiQA losses span **0.037144–0.058631**. The effectiveness and Appendix A tables agree with rounded JSON.

**Not independently reproducible from these attachments:**

- “**1,402**” one-document ArguAna lists and “**four**” two-document lists: the supplied facts aggregate lengths 1–3. The text-match count **1,406**, own-ID count **1,298**, rank-one count **1,296**, and relevant-hit count **one** do reproduce.
- “**174**” disjoint excess runs and “**two**” overlap-present runs, including their identities and deep ranks, require the per-query rows.
- The sweep’s query-by-query ceiling/disjointness equality, “**11 of those 20 cells**,” and nomic’s “**within 4.4 points**” and “**within 1.0 point**” cannot be checked from the inline summaries. The **2,392** eligible sweep-run denominator does reproduce.

These are verification requests, not demonstrated contradictions.

## 3. Interpretation and title

**(a) Content tokens:** The five-point ordering is supported as an aggregate observation, not a causal explanation or per-query predictor. “The content words are what run out” states a mechanism more firmly than the supplied evidence warrants; qualify it as an explanation consistent with the observations.

**(b) Corpus size:** The recommendation “Expect more such queries on a large corpus” is wider than the evidence. Collection, query type and builder condition change together. The relationship is not even monotonic across all five collections: NFCorpus has **13/330 = 3.9%** short-list firing at 3,633 documents, whereas larger SciFact has **0/18**. Describe the four named collections’ pattern without turning corpus size into a predictive rule. Also, the ≥50 bucket contains two overlap-present cases: ceiling firing and disjointness are not interchangeable there.

**(c) ArguAna:** The mechanism generalises conditionally, not its prevalence or irrelevance. In a mailbox or ticket search, finding the indexed source of pasted text may be the desired result. Replace “routinely receives” with a possibility statement, and specify that the blind spot requires a shared self-match that is nonrelevant to the task and retained during fusion.

**(d) Different instruments:** The separation from effectiveness is supported. But scores and counts monitor **activity and overlap**, not sufficient “leg health”; ArguAna demonstrates that limitation.

**Title:** “Detects Zero Overlap” omits \(K\le k\), while the principal reproduction uses \(K>k\) and supplies two counterexamples. Qualify the title. The abstract states the depth condition, but still needs the ArguAna and historical-scope corrections above, and “observed higher nDCG@10” rather than unqualified “improves.”

## 4. Journal requirements, ranked

1. **Required:** State the research contributions explicitly and distinguish them from existing fusion, overlap and monitoring work; this is the principal acceptance question for a normal paper.
2. **Required:** Document ArguAna’s self-match exclusion policy separately for fusion and evaluation, plus query fields, relevance handling, tokenizer and stopword specification, because these choices determine what the results mean.
3. **Required:** Report paired query-level uncertainty for the named effectiveness contrasts using existing rows; repeated retrieval runs are not needed, and captions disclaiming significance do not provide uncertainty.
4. **Optional:** Add a short Introduction and Conclusion identifying the question, contributions and bounded conclusions rather than relying on “The incident” and operator advice to perform those functions.
5. **Optional:** Add a rank-pair figure showing \(r_1r_2=k^2\) and the depth boundary; no additional experiment is needed.

I would not require new retrieval experiments to resolve these findings.
