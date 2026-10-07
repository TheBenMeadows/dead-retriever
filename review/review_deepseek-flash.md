Read all four files and checked the arithmetic. Findings ranked by expected impact.

## 1. The abstract states the ceiling claim universally; §2 proves it only for K ≤ k, and §6 runs at K = 100 > k = 60

`main.tex:22` asserts outright: "When the maximum fused score across a result list is exactly 1/k, no document was found by more than one retriever." That is false at the setting the paper's own experiments use. A two-leg document scores 2/(k+r); this is ≤ 1/k exactly when r ≥ k, and K−1 = 99 ≥ 60, so a shared document sitting at rank 60–99 in both lists drags the max to or below the ceiling. The body admits this at `main.tex:51`, but then states a replacement that is also not true: "a maximum of exactly 1/k still means the top fused document was found by one retriever at its rank 0." Two documents at rank 60 in both lists give 1/120 + 1/120 = 1/60 exactly, tying the single-list top. The correct weak statement is a disjunction: max = 1/k iff every shared document has 1/(k+r_ℓ) + 1/(k+r_m) ≤ 1/k; the rank-0/single-list reading is the K ≤ k special case. Either restrict the abstract to K ≤ k, or state the weak form as the disjunction.

The K ≤ k derivation itself is right: 2/(k+K−1) > 1/k ⟺ K < k+1, attained exactly at K−1, so no ties at K = k. The implication is also an equivalence (the max of any non-empty list is achieved by a rank-0 document, scoring 1/k), which means the test **cannot** miss an empty leg — only over-fire. Say so; it makes the false-positive rate the sole thing to calibrate.

## 2. The incident table shows a 40% false-positive rate, not the sub-1% §6 claims

Table 1 (`main.tex:78–80`): before the fix, the keyword leg returned a row on 4/10 queries, **zero** queries had a document found by both legs, and the max fused score was 1/60 on all ten. So on 4 of the 10 queries the ceiling fired while the keyword leg was alive. §2 (`main.tex:49`) reports "the ceiling held on 10 of 10" as clean evidence and mentions the four live-but-disjoint queries only in passing; §6 (`main.tex:128`) concludes the false-positive rate is "under one percentage point". The rate is a function of live-list length, not of the test: the AND leg returns 1–3 rows, so overlap is structurally near-impossible. The paper's own incident sample gives 4/10. This is the strongest internal inconsistency in the draft and it cuts against the paper's central practical claim (a 40% alarm rate is not a usable monitor).

## 3. §2's "across a set of queries it is strong evidence" needs the depth assumption stated, and Table 1's 0/4 violates it

`main.tex:49` grounds the inference on "two retrievers … that both return K results almost always share at least one document". The qualifier is doing all the work and is never made: the justification holds only when both lists are near depth K. Production had 4 live keyword legs with 0 overlap; the BEIR bm25-and legs share a mean 3.9 docs/query and 3/323 still fire at the ceiling. State the condition (live leg near depth K; short lists inflate false positives) and §6's "under one percentage point" becomes a property of these collections, not of the test.

## 4. The buggy hybrid beats the fixed hybrid at nDCG@10 in 3 of 4 collection/encoder pairs, and the paper never says so

`main.tex:128–130` compares only hybrid-or against dense. From the result files: SciFact/bge hybrid-and 0.7386 vs hybrid-or 0.7302; NFCorpus/bge 0.3769 vs 0.3583; NFCorpus/nomic 0.3606 vs 0.3445. Only SciFact/nomic goes the other way (0.7049 vs 0.7076). Recall@100 favours the fixed leg on nomic and ties on bge. A reviewer computing the direct comparison from Table 2 will read the omission as selective emphasis; the honest reading — when the AND leg fires it is a short high-precision list, so it can out-rank the OR leg at 10 — should be stated, and it is also the explanation for the NFCorpus false positives.

## 5. Units error in the flatness remark

`main.tex:31`: "the '1.4% flatness' is 1/(k+r) − 1/(k+r+1) ≈ 1/k²". The 1.4% is a **relative** gap; 1/(k+r) − 1/(k+r+1) is **absolute**. Relative gap = 1/(k+r+1) ≈ 1/k (1.64% at r=0, 1.41% at r=9, which is where "1.4%" comes from); absolute gap = 1/(k(k+1)) = 2.73e-4 ≈ 1/k². Both statements are true separately; equating them conflates a ratio with a difference.

## 6. `and_quoted` is not exactly implicit AND

`hybrid.py:36–37` keeps `. - $ # @` inside tokens; FTS5's unicode61 tokeniser treats them as separators, so a hyphenated or dotted token is emitted as a **quoted phrase** (`"il-6"`), i.e. an adjacency constraint, not a co-occurrence constraint. The paper's §3 description ("every quoted token must occur in the same row", `main.tex:63`) is then inaccurate for the tokens where the failure is most likely (SciFact claims carry `IL-6`, `5-FU`, `TNF-alpha`). Tokenise as FTS5 does, or emit `"a" AND "b"`, and describe the bug as "one quoted phrase per token: implicit AND, adjacency where FTS5 splits further".

Also: §3 says "the vector retriever returns exactly K results for any query"; `DenseIndex.search` (`hybrid.py:86–95`) returns `min(limit, len(sims))` — harmless here, but the incident narrative leans on the exact-K property.

## 7. The false-positive reading is valid, but was computable and thrown away

The arithmetic is exact: (0.517028 − 0.507740) × 323 = 3.00; (0.083591 − 0.077399) × 323 = 2.00. The subtraction is legitimate because a non-empty dense leg guarantees max = 1/k, hence empty ⟹ at_ceiling, so the difference is precisely the count of live-leg queries at the ceiling — not a difference of two sets that could move independently. But `run_query` computes per-query `multi_leg_docs` and `max_score` (`beir_run.py:86–87`) and `main` keeps only means (`beir_run.py:142`, `summarize_diag:98–107`); `CeilingReport.legs_configured/legs_nonempty/max_score` are never consumed. The paper's stated mechanism for the three NFCorpus queries ("shared nothing with the dense top 100") is therefore unverifiable from the stored files, and at K > k a shared document at rank ≥ 60 produces the same signature. Persist per-query diagnostics; without them the sentence is an assertion.

## 8. "a fusion with an empty list is the other list"

`main.tex:128` is a claim of exactness; the numbers are +0.00093 nDCG@10 and +0.0075 on NFCorpus with the live half. Replace with the measured differences, or say "within 0.001 nDCG@10 on the 294 empty-leg queries". "Identical Recall@100" (0.970 = 0.970) is fine.

## 9. Citations

Entries check out: Cormack SIGIR 2009 758–759; Thakur NeurIPS D&B 2021; Bruch TOIS 42(1); Wadden EMNLP 2020 7534–7550; Boteva ECIR 2016 716–722; Robertson/Zaragoza FnTIR 3(4); Van Gysel SIGIR 2018 873–876; MacAvaney SIGIR 2021 2429–2436; Nussbaum arXiv:2402.01613; Xiao arXiv:2309.07597. Defects: `sqlite_fts5` has **no `year` field** — plainnat will print "(n.d.)"; and the section pointer is duplicated (the `\citep[\S 3]` at `main.tex:63` and "Section 3 …" inside the entry's `note`). Give it `year = 2026` or the manual's date, and drop one pointer.

Missing, in the order a reviewer will look: **(a)** rank-biased overlap (Webber, Moffat, Zobel, TOIS 2010) — the principled version of the "both-leg docs" statistic; **(b)** CombSUM/CombMNZ and score normalisation (Fox & Shaw 1994; Montague & Aslam CIKM 2001) — the lineage of "is the score scale relevant" that RRF quietly departs from, and which the one-leg ceiling is a direct consequence of; **(c)** sparse–dense fusion beyond Bruch — SPLADE (Formal SIGIR 2021), Luan et al. NeurIPS 2021; **(d)** expansion for the §5 negative result — doc2query/docTTTTTquery (Nogueira, ICTIR 2019) and HyDE (Gao ACL 2023), since a title prefix is a weak instance of that family; **(e)** anything on zero-result/empty-leg monitoring in query logs — the paper presents noticing an inert leg as novel, and search-ops practice predates it.

## 10. Remaining code and claim issues (lower impact)

- `build_keyword` (`beir_run.py:64–69`) keys freshness on file existence after `CREATE VIRTUAL TABLE IF NOT EXISTS`; a run that dies between create and `add` leaves an empty index that later runs reuse as "not fresh", which would report 100% empty legs with no error. Write to a temp path and rename.
- The stopword drop's claim "not cosmetic" (`main.tex:65`) is supported only by latency. No condition ablates it for effectiveness; adding `bm25_or_nostop` is cheap and makes the sentence true.
- `summarize_diag` drops `max_score`, the exact quantity the checklist at `main.tex:142` tells readers to log.
- Doc-text construction, prefixes, depth and qrels filtering in `beir_run.py:43–48, 126–131` are consistent across conditions; BM25 rows are genuinely encoder-independent (identical to 6 decimals across both files); the cache/db keys are per-dataset and per-model correctly.
- Table 1 row 3 ("0.025–0.033") is consistent with the post-fix two-leg range [2/119, 2/60] = [0.0168, 0.0333]; no conflict with the 10/10 overlap row.

## 11. Prose

"the system's own scores had been saying so" appears at `main.tex:22`, `:31`, `:130`; "can be read from the scores alone" at `:22` and `:51`; "spot checks" at `:22`, `:29`, `:63`. "The second lesson of the incident: a copied bug costs one investigation per copy" (`:88`) is a truism and sits beside the statement that the five engines have since been merged, which retires it. "for several months" (`:22`) is unanchored — give the build date, since the incident dates are pinned. Two limitations belong in §1–§2 rather than §8: the exact statement needs K ≤ k, and the ten-query production base (the deck is stacked by the six zero-row queries; 4/10 were live). The checklist at `:142` should carry the false-positive caveat, or it will be applied literally to short-list systems and fire at 40%.

One conclusion the tables support but the text omits: with nomic on SciFact, the fixed hybrid moves Recall@100 by +3.0 points and nDCG@10 by +0.004 — RRF here adds deep candidates, not top-10 ordering. That is the honest framing of "the hybrid does not beat dense", and it also predicts the bge result.
