**Corrections are still required before submission.**

## 1. Significance: reporting matches the supplied tests

All stars and omissions in Tables 3 and 4 agree with `p_holm` at \(\alpha=0.05\). The prose’s significance counts also agree:

- Repaired hybrid versus dense, nDCG@10: **2 significant gains, 5 significant losses**.
- Repaired hybrid versus dense, Recall@100: **1 significant gain, 3 significant losses**.
- Buggy versus repaired hybrid, nDCG@10: **6 significant wins, 2 significant losses**.

In particular, NFCorpus/nomic and FiQA/e5 are **not** significant for buggy versus repaired nDCG@10; both have \(p_{\mathrm{Holm}}=0.065499\). The supplied Holm adjustments are consistent with the six families of 18.

Query-paired sign-flip tests are appropriate for these per-pair comparisons, assuming within-query system-label exchangeability under the null and independent query units. Reusing queries across encoders creates dependence between tests, which Holm permits; it does not require independent p-values. Six separately corrected families are defensible for separately scoped questions, but do not provide paper-wide 0.05 familywise control. Section 6 should explicitly identify them as **two metrics × three comparisons**. This checks the reported results, not the randomization implementation.

## 2. Section 7.5: calculate differences before rounding

The statement that BM25 exceeds two ArguAna encoders follows from the unrounded means, but “by 0.001” for nomic does not: the difference is **0.00016448**. This is effectively a tie at the precision relevant to that explanation, not evidence that BM25 meaningfully outperforms nomic.

Several other differences were calculated from rounded table entries:

| Comparison | Difference from JSON | Claimed |
|---|---:|---:|
| ArguAna, repaired − dense, nomic | +0.033091 | +0.034 |
| ArguAna, repaired − dense, bge | −0.034305 | −0.035 |
| SciFact, repaired − dense, nomic | +0.004335 | +0.005 |
| FiQA, repaired − dense, bge | −0.058631 | −0.058 |
| NFCorpus, buggy − dense, nomic | +0.013274 | +0.014 |

Thus the NFCorpus range in Sections 7.3 and 7.5 should round to **0.008–0.013**, and the FiQA loss range to **0.037–0.059**. Generate prose differences from unrounded values consistently.

## 3. “The buggy hybrid’s 12 wins”: counts follow, ArguAna explanation does not

The **8 of 12** split is correct, including the seven pairs with empty-leg rates of 74–94.2%.

However, “on ArguAna with bge it returned only the self-match” contradicts Section 7.2: four queries returned two documents, and one query had a relevant AND hit. Moreover, identical aggregate nDCG and recall do not establish that “the fused list was the dense list,” particularly for the 108 self-matches not removed by identifier.

Keep the empty-leg argument for the seven pairs; describe ArguAna as **unchanged on the two reported aggregate effectiveness metrics**, unless ranked-list identity has separately been established.

## 4. Section 7.4 and Figure 1: one frequency claim remains too strong

The pooled counts **137/726, 35/588 and 4/6,636**, and all five collection-specific short-list counts, match the supplied JSON. Including SciFact and stating the builder pooling addresses those qualifications.

But this sentence exceeds the counts:

> “A short exact-match list over a large corpus was, on these collections, usually a different handful of documents from the dense top 100.”

If “different” means disjoint, the short-list rates are **12.8% on SciDocs, 41.1% on FiQA and 88.9% on TREC-COVID**; pooled across those three larger collections, **124/378 = 32.8%**, not “usually.” Replace that sentence with the observed rates. The abstract’s narrower statement that the *observed excess events* were mostly short lists on larger corpora is supported.

Figure 1’s caption should say SciFact and ArguAna are zero in every **populated** cell: ArguAna has no 4–49 cell. The figure graphic itself is not attached, so its rendering cannot be checked.

## 5. Title, abstract and conclusion

The title’s \(K\le k\) qualification matches the zero-based derivation, and the abstract’s headline counts and significance claims match the supplied results.

The conclusion does not preserve the historical limitation:

> “the ceiling had been present on every query for as long as the keyword query builder had existed”

There is no query log, and unchanged code does not establish zero overlap for every historical query. State that the ceiling held on **all ten replayed queries**, with earlier behavior inferred rather than observed. Section 1’s “from the start” needs the same qualification.

## 6. Other corrections before acceptance

- **Required:** Add the missing bibliography entry for `smucker2007comparison`; Section 6 cites a key absent from the supplied bibliography.
- **Required:** Correct Appendix B’s explanation that timings were omitted because collections were timed on “two different machines,” which contradicts Section 6 and Appendix C’s statement that every reported result file comes from the Kaggle runs.
- **Required:** Replace Section 6’s inference about unchanged FiQA effectiveness with the observed before/after comparison: excluding a nonrelevant document outside the top 10 can still change Recall@100 by promoting rank 101, and “fused top 10” does not cover standalone conditions.
- **Required:** Qualify Section 7.1’s “none of whose tokens occur in the corpus at all,” because raw-OR emptiness establishes no matching quoted phrase only when execution succeeds, not vocabulary absence given Section 4’s phrase tokenization and suppressed errors.

No new retrieval experiment is essential for these corrections.
