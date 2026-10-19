**Hold submission for the corrections below.** No additional retrieval experiment is essential.

### 1. Significance tests and stars

Every star in Tables 3 and 4 agrees with `p_holm ≤ 0.05`; I found no missing or misplaced star. The prose’s significance counts also agree:

- Repaired hybrid versus dense, nDCG@10: two significant gains and five significant losses.
- Repaired hybrid versus dense, Recall@100: one significant gain and three significant losses.
- Buggy versus repaired hybrid, nDCG@10: six significant wins and two significant losses.

In particular, NFCorpus/nomic and FiQA/e5 **are not significant** for buggy versus repaired nDCG@10: both have `p_holm = 0.065499345`. NFCorpus/nomic **is significant** for buggy versus dense (`0.020249798`). The paper keeps these comparisons straight.

Query-paired, two-sided sign-flip randomization is appropriate under the usual querywise exchangeability assumption. The encoders are separate, correlated comparisons, not three independent query samples; Holm does not require independence between their tests. Six families of 18 are defensible for six separately defined metric/comparison questions, but control familywise error separately, not across all 108 tests. Section 9 acknowledges that limitation.

**Required:** Section 6 should explicitly define each family as one `(metric, comparison)` combination, with two metrics and three comparisons.

### 2. Differences computed from rounded table entries

Several numerical differences in Sections 7.3 and 7.5 do not equal the differences in the JSON. Compute differences before rounding.

| Claim | Difference from JSON |
|---|---:|
| ArguAna BM25 exceeds nomic “by 0.001” | `0.483605192 − 0.483440717 = 0.000164475` |
| ArguAna repaired hybrid gains “0.034” for nomic | `0.033090974`, rounding to **0.033** |
| ArguAna repaired hybrid loses “0.035” for bge | `0.034304841`, rounding to **0.034** |
| SciFact repaired hybrid gains “0.005” for nomic | `0.004335396`, rounding to **0.004** |
| FiQA repaired-hybrid losses reach “0.058” | Maximum `0.058631144`, rounding to **0.059** |
| NFCorpus buggy-hybrid gains reach “0.014” | Maximum `0.013274470`, rounding to **0.013** |

Thus the ArguAna statement that BM25 exceeds two encoders is numerically true, but the nomic margin is approximately **0.00016**, not 0.001; it is not an established significant BM25 advantage.

Section 7.3’s SciDocs claim, “by at most 0.001 in each,” also needs qualification: bge’s nDCG difference is `−0.001661474`. It is 0.001 only when subtracting the printed table entries, not when rounding the actual difference.

### 3. “The buggy hybrid’s 12 wins”

The **12 wins**, **eight not above dense**, and the identification of the four exceptions—NFCorpus’s three encoders and SciFact/bge—follow from the results. The “mostly abstention” interpretation is consistent with the empty-leg rates.

Two sentences require narrower wording:

- “On ArguAna with bge it returned only the self-match” contradicts Section 7.2: four queries returned two documents, and one query received a relevant keyword hit. Say **“almost always returned only the self-match.”**
- “The fused list was the dense list on those queries” is guaranteed for empty keyword legs, not established for ArguAna by equality of aggregate effectiveness scores. Reserve list identity for the empty-leg queries; report unchanged measured effectiveness for ArguAna.

### 4. Section 7.4 and Figure 1

The supplied counts support `137/726`, `35/588`, and `4/6636`, the 176 excess runs, and the per-collection short-list fractions. Including SciFact and explicitly pooling both builders resolves the corresponding scope problems. The four nonzero collection rates increase with corpus size, and the text correctly excludes a causal size interpretation.

However:

> “A short exact-match list over a large corpus was, on these collections, usually a different handful of documents from the dense top 100”

If “different” means disjoint, **“usually” is false**. Across SciDocs, FiQA and TREC-COVID, the short-list ceiling rate is

\[
(18+90+16)/(141+219+18)=124/378=32.8\%.
\]

FiQA is `90/219 = 41.1%`; only TREC-COVID exceeds half (`16/18 = 88.9%`). Replace that sentence with the collection-specific rates or the pooled fraction.

The Figure 1 image is not attached, so this confirms its caption and aggregate basis, not its rendered points. Likewise, the supplied summaries cannot independently establish the two FiQA overlap ranks or the sweep’s per-query assertions.

### 5. Title, abstract and conclusion

The title’s \(K\le k\) restriction follows from the stated unweighted, zero-based derivation. The abstract’s effectiveness counts and diagnostic totals agree with the supplied aggregates.

The conclusion overstates the incident’s historical evidence:

> “the ceiling had been present on every query for as long as the keyword query builder had existed”

There is no historical query log, and Section 1 expressly identifies persistence on prose queries as an inference. “Every query” additionally expands beyond those prose queries and the ten-query replay. State that the ceiling appeared on **all ten replayed queries**, with historical persistence inferred from unchanged code.

### 6. Remaining acceptance requirements

- **Required:** Add the bibliography entry for `smucker2007comparison`, cited in Section 6 but absent from `refs.bib`.
- **Required:** Remove Appendix B’s explanation that query times were omitted because collections were timed “on two different machines”; Section 6 and Appendix C say every reported result file comes from the Kaggle runs and that CPU runs serve only as reproduction checks.
- **Optional:** Give confidence intervals for the paired differences if the journal requests estimation alongside significance; this needs no new retrieval runs.
