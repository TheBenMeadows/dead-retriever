# Review: dead-retriever draft 1

Findings ranked by expected impact.

## 1. The "false positives" inference is not licensed by the data (Sec. 6)

Empty ⊆ at-ceiling always: an empty keyword leg leaves the fused list = the dense list, so `max = 1/60` is forced. The count 167−164 = 3 (51.7%−50.8% of 323) is therefore exact as a count. But the characterization — "three queries on which the keyword leg returned documents that happened to share nothing" — is not implied. Under K > k a shared document routinely hides under the ceiling: `1/(60+r_d) + 1/(60+r_k) ≤ 1/60` whenever `r_d·r_k ≥ 3600` (e.g., rank 60 in both lists scores exactly 1/60; rank 40 + rank 90 also exactly 1/60). So the three excess queries may include queries that *did* share, at deep ranks. The one-direction containment means the sets cannot drift in both directions, but the claim needs a per-query join of `at_ceiling` ∧ `multi_leg_docs == 0` against `keyword_empty` — which `beir_run.py` does not emit (only `summarize_diag` aggregates survive in the JSON). Emit per-query diagnostics and report the conditional decomposition; as written, the "under one percentage point" FPR number is a bound on the wrong event.

## 2. bge ran unprefixed; Appendix B's description is wrong for it

`DOC_PREFIX`/`QRY_PREFIX` only contain nomic keys; `bge-base-en-v1.5` gets `""` via `prefix.get(a.model, "")` — a silent default. bge v1.5's documented usage prepends a query instruction ("Represent this sentence for searching relevant passages: "), none for documents. Appendix B claims "the encoder's document prefix… queries with its query prefix" — false for the encoder that fills Table 2. Dense, and therefore both hybrid conditions, are understated relative to documented usage; the headline honesty ("hybrid-or does not beat dense at nDCG@10 for bge") could move in either direction with the proper instruction. Fix the dicts to include bge's query instruction and re-run, or state the deviation explicitly. Independently, make the `.get(..., "")` fail loudly for unlisted models — silent prefix-free embedding is exactly the class of bug this paper is about.

## 3. Weak-form statement in Sec. 2 is slightly mis-stated

Under K ≤ k the exact form is airtight — a two-leg document scores ≥ 2/(k+K−1) > 1/k strictly, and the all-empty case is vacuously true. No counterexample exists. But for K > k, "a maximum of exactly 1/k still means the top fused document was found by one retriever at its rank 0" needs the existential phrasing: at least one max-scorer must be single-leg rank-0 (every non-empty leg's rank-0 doc scores ≥ 1/k; equality forces it single-leg), but a two-leg doc at (60,60), (40,90), (48,75), etc. sits *at* the same maximum. Also worth one sentence: since the dense leg always returns K results, `max ≥ 1/k` always holds here, so the code's `mx ≤ 1/k + eps` collapses to equality — the table caption "sat at 1/k" is accurate only because of that.

## 4. Missing related work

- Query-performance prediction: post-retrieval predictors read score distributions for exactly this purpose (Cronen-Townsend, Zhou & Croft, SIGIR 2002; the predictor survey line through Shtok/Kurland/Carmel). The ceiling statistic is a structural cousin — closest existing literature to the paper's actual contribution.
- The comb-lineage RRF positions against: Fox & Shaw "Combination of multiple searches" (TREC-2), Lee (SIGIR 1997) on CombSUM/CombMNZ.
- Rank-vs-score fusion with partial/missing lists: Renda & Straccia (SIGIR 2003). Nothing canonical covers a silently-empty leg — say that explicitly rather than leaving related work thin.

## 5. A supported conclusion is left on the table

On NFCorpus, hybrid-**and** beats dense at nDCG@10 on *both* encoders (+0.0075 bge, +0.013 nomic): a leg alive on only 49% of queries still added nDCG, while SciFact's 2%-alive leg added ~0. Value tracks alive-fraction — that observation is in the table and unwritten. On the author's standing worry: the motivation is the *diagnosis*, not hybrid efficacy, but the paper should state plainly that on these two collections the restored leg buys Recall@100 (nomic SciFact +3.0) but not nDCG@10 — one complete sentence instead of dispersing it.

## 6. Code defects (lower impact)

- `ceiling_report`: all-legs-empty → `mx=0` → `at_ceiling=True` since `len(ranks)>1`. That flags "everything dead" as the single-list fingerprint — arguably desirable, but it is a different failure; require `legs_nonempty ≥ 1` or report separately.
- `build_keyword`: `fresh = not path.exists()` — a crashed run leaves an existing-but-empty FTS table that is silently reused forever. Check row count, not existence.
- `and_quoted` faithfully reproduces implicit AND (quoted single-token phrases space-joined; `OperationalError → []` mirrors the swallowed syntax error). `rrf_fuse` dedups within-leg at first rank and caller-side depth-cutting is consistent — both match Sec. 2–3. `ceiling_report`'s `multi` matches the Sec. 2 definition.
- `bm25_or` still returns empty on 7.7% of NFCorpus queries — no token matched at all. The paper never explains this; one clause (e.g., rare/absent terms after the <3-char drop) is owed since it's a headline-adjacent rate.

## 7. Numbers — all check out

Every Table 2/3 value matches the JSON at shown rounding, including the exact-half 0.0175→0.018. Prose bounds verified: hybrid-and vs dense |ΔnDCG| = 0.0009 (SciFact), 0.0075 / 0.0045 R@100-nDCG gaps (NFCorpus < 0.005/0.008); nomic R@100 +0.030; both-leg means 3.9/3.7/28.4/25.9/20.2/21.0 all correct. Table 1's post-fix range 0.025–0.033 is consistent with the two-leg max 2/60 = 0.033.

## 8. Flatness wording (Sec. 1–2)

`1/(k+r) − 1/(k+r+1) = 1/((k+r)(k+r+1)) ≈ 1/k²` is the *absolute* gap; the reported "1.4%" is the *relative* gap `1/(k+r+1)` (≈1.64% at r=0, 1.4% near r≈10). Correct to first order each, but the sentence equates them — split into two clauses.

## 9. Citations

All entries verified as real and correctly attributed. Two nits: `xiao2023cpack` truncates the author list (missing Defu Lian, Jian-Yun Nie) — use "and others"; `bruch2023fusion` — ACM lists TOIS 42(1) as the Jan-2024 issue against 2023 online-first; pick one consistently. The "k=60 set by experiment" claim matches Cormack et al.; the BEIR/baseline claim is fair.

## 10. Prose

- "which is what makes the 1/60 ceiling recognisable on sight" — unverifiable flourish, cut.
- "the second lesson of the incident: a copied bug costs one investigation per copy" — keep the five-engines-merged fact, drop the aphorism.
- "regardless of corpus" overclaims (no corpus-varied evidence) → "in all four sibling engines".
- Abstract's "read from the scores alone" is repeated nearly verbatim in §2's last paragraph.
- Checklist "one of your retrievers is returning nothing" overclaims the single-query case (persistent disagreement also sits at ceiling) → "contributing nothing".
- Move n=10/n=15 into the §4/§5 text itself; the K≤k caveat is already correctly placed.

Verdict: correct in derivation and arithmetic; the two substantive fixes are the Sec. 6 false-positive argument (needs per-query output) and the bge prefix (needs a re-run or an honest Appendix B sentence).
