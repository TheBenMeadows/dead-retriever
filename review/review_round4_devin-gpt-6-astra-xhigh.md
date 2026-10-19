## 1. Corrections required before submission

**“Never useful” is contradicted by the reported result.** Section 6.2 and the abstract say this, but the AND leg retrieves a relevant document on 1/1,406 ArguAna queries; its nDCG@10 is 0.000448741, not zero. Equality of aggregate hybrid and dense metrics also does not establish equality on every query. Report near-exclusive self-matching and no observed aggregate effectiveness gain, not universal uselessness.

**ArguAna’s evaluation protocol needs an explicit account.** Appendix B does not specify whether identical query/document IDs are excluded, or whether exclusion happens before fusion, after fusion, or only during evaluation. The standard BEIR evaluator normally removes identical IDs; directly using `pytrec_eval` does not establish that policy. This matters when the claimed blind spot is precisely self-retrieval. Separate raw diagnostic lists from evaluated rankings, document treatment of the 108 differently identified text matches, and recompute from existing outputs if the implemented policy differs from the intended one.

**The abstract overstates historical coverage.** “Returned no results for most natural-language queries … from the system’s first version” is a claim about historical traffic. An unchanged builder plus ten replayed queries establishes neither that historical proportion nor every intervening period. Identify supporting traffic evidence or restrict the claim to the tested queries and the builder’s documented lifetime.

## 2. Numerical audit

The displayed result tables agree with the supplied summaries at their printed precision. The AND-empty counts, query-token means and five-collection content-token ordering reproduce. The total is
\[
(300+323+1406+1000+648+50)\times3\times2=22,362.
\]

Excess ceilings reproduce as follows, in **bge / nomic / e5** order:

| Collection | AND excess | OR excess |
|---|---:|---:|
| NFCorpus | 3 / 3 / 2 | 3 / 2 / 0 |
| SciDocs | 7 / 6 / 5 | 1 / 1 / 1 |
| FiQA | 35 / 37 / 43 | 2 / 0 / 2 |
| TREC-COVID | 8 / 7 / 8 | 0 / 0 / 0 |

These sum to **164 + 12 = 176**. The stated percentages among live AND queries reproduce. So do the natural-length counts **137/726, 35/588, 4/6,636**, their rounded percentages, and the **39** firings with four or more keyword documents.

The effectiveness counts **5/18, 9/18 and 12/18**, and all named gains and losses, reproduce from unrounded values. NFCorpus/bge’s Recall@100 gain is approximately **0.000588**, explaining one gain hidden by the rounded table.

ArguAna’s **1,406** text matches, **1,298** own-ID matches, **1,296** own-ID rank-one matches and remaining **108** reproduce.

Correct these precision claims:

- **“2.6 to 18 times slower”:** NFCorpus/e5 gives \(2.330779/0.937358\approx2.487\), so the lower endpoint should be approximately **2.5**.
- **“Within 0.008 nDCG@10”:** ArguAna’s difference is **0.00836756**. Label the bound approximate or increase it.
- **“At most 0.002”** on SciFact: e5’s difference is **0.00219319**.
- SciDocs’s **“0.000 Recall@100”** difference conceals absolute changes of **0.0002** for bge and nomic; report those rather than suggesting exact equality.
- **“At most 4.0”** shared documents is likewise a rounded approximation: the maximum is **4.00619**.

Not independently reproducible from these aggregates: **“1,402” singleton versus “four” two-document ArguAna lists; “174” disjoint versus “two” overlapping excess ceilings; the nomic sweep ranges and “11 of those 20 cells.”** These are not disputed counts, but require the omitted records. Put the two exceptional FiQA rank pairs and maximum scores in the paper: they are central evidence for the newly observed failure mode.

## 3. Interpretation, abstract and title

**Content-token ordering:** the descriptive ordering across the five non-self-matching collections is supported, and the confounding qualification is necessary. “The content words are what run out” goes further: collection-level means do not establish which constraints caused individual failures, nor that stopwords were generally harmless. Keep the association; qualify the mechanism.

**Corpus-size interpretation:** the presentation omits SciFact’s **0/18** short-list firings, despite including NFCorpus’s **13/330** at a smaller corpus size. Thus the five-collection relationship is not monotonically increasing. Moreover, TREC-COVID’s 18 short-list runs represent only six queries across three encoders, and the pooled populations mix AND and OR conditions. Include SciFact and remove the operator instruction **“Expect more such queries on a large corpus”** as a general prediction; the observed cross-collection contrast is not a controlled size effect.

**Self-match generalisation:** indexing query text can reproduce the mechanism, but not necessarily the failure. Finding the original email, note or ticket can be the intended task. The warning needs the condition that self-retrieval is unwanted or non-relevant; a singleton return is not intrinsically “as suspect” as zero.

**Health versus effectiveness:** the distinction is supported. However, neither overlap nor a nonzero row count certifies health, as ArguAna demonstrates. Describe these as diagnostic signals, not a health verdict.

**Abstract:** “Repairing the leg restores overlap on every collection” is wrong for ArguAna, which already overlaps on every query. The supported statement is an increase in **mean overlap in every pair**. Replace “improves nDCG@10 … in 5 of 18” with explicitly observed, numerical superiority unless paired uncertainty is supplied.

**Title:** “Found a Dead Retriever” does not follow the chronology in Section 1: row-count logging discovers the fault, and the scores provide retrospective evidence. Document a score-led discovery or remove that attribution. “Detects Zero Overlap” also needs conditional framing given the paper’s own \(K>k\) counterexamples.

Sections 1–5 do not retain the superseded four-document or never-observed-leak claims; Section 2 already permits the new exceptions. In Section 5, however, doc2query supports generated-query expansion, not the superlative **“the cheapest form of document expansion”** for a title prefix; remove that unsupported comparison.

## 4. Journal-fit requests, ranked

1. **Required:** State the journal-level contribution explicitly and deepen its comparison with existing fusion and monitoring work; the inequality alone does not establish sufficient novelty, so acceptance depends on the empirical failure analysis.
2. **Required:** Resolve the evaluation-policy ambiguity above and make the exact reproducible implementation identifiable through immutable runner/model revisions and specified tokenizer, stoplist and filtering settings.
3. **Required if effectiveness remains prominent in the abstract:** Add paired uncertainty from existing per-query outputs, with multiplicity handling for any significance claims; deterministic single runs do not prevent paired analysis.
4. **Optional:** Separate experimental protocol from results, move Section 5’s ancillary negative results to an appendix, and add one diagnostic figure rather than expanding prose merely to approach 20 pages.

No additional retrieval experiments are essential to address these points.
