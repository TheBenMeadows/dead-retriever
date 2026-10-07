# Round 1: 6 lanes + Orrery on the dead-retriever paper, draft 1 (2026-10-07)

Lanes asked, and what each could see:

| Lane | Route | Saw | Result |
|---|---|---|---|
| Gemini | `agyx` on the repo dir, brief by absolute paths | tex, bib, code, 4 result JSONs | `review_gemini-agyx.md` 6.6 KB. Relative-vs-absolute step error; `ceiling_report` fires on all-empty; "collapses" over-claim; Fox & Shaw / Lee / Kamphuis missing. |
| GPT-6 Sol | `council-devin.sh gpt-6-sol-high`, files inline | same, inline | `review_devin-gpt-6-sol-high.md` 7.0 KB. Theorem proves zero overlap, not an empty leg; K>k tie at rank k/k; per-query diagnostics needed; cache reuse unvalidated; BGE query instruction missing. |
| GPT-6 Astra | `council-devin.sh gpt-6-astra-high`, files inline | same, inline | `review_devin-gpt-6-astra-high.md` 7.7 KB. Same core correction; false-positive denominator (3/159 = 1.9%); "flatness was the dead leg" is not causal; "confounded" is the wrong word for a vector-only A/B. |
| SWE-2 Max | `council-devin.sh swe-2-max`, files inline | same, inline | `review_devin-swe-2-max.md` 7.0 KB. Recomputed all 60 table cells; Bruch is 2024; L=2 assumption; docstring drift; bm25-or still empty on 7.7%. |
| DeepSeek Flash | `council-ccx.sh deepseek-flash`, sources appended | same | `review_deepseek-flash.md` 10.2 KB. Incident Table 1 shows 4/10 live-but-disjoint, i.e. a 40% alarm rate on short lists; buggy hybrid beats fixed hybrid at nDCG@10 in 3 of 4 pairs; `"il-6"` is a phrase constraint; `build_keyword` can adopt a half-built index; RBO / Montague-Aslam / Luan / HyDE / doc2query. |
| Codex (GPT-5.6 Terra) | `council-ccx.sh gpt-5.6-terra`, sources appended | same | `review_gpt-5.6-terra.md` 7.5 KB. Same core correction; Ghalandari surname truncated; `k` not passed through to `ceiling_report`; Table 1 needs a machine-readable aggregates file; Cooper 1998 for monitoring. |

First attempt on the three Devin seats, with files listed by path, returned 0, 0 and 63 bytes: print mode gives nothing once the model reaches for a file tool (same trap as the eval lane earlier today). The inline brief (`brief-inline.md`, 42 KB) fixed all three.

Orrery audit (`orrery-audit.py`, deterministic, log-only): 73 PASS after fixes. It caught the NFCorpus "identical Recall@100" error before any lane reported, and two rounding-precision bugs in itself.

---

## A. Verified defects (measured here, not claimed)

**A1 — The paper's thesis over-reached.** *All six lanes.* Max fused score ≤ 1/k (K ≤ k) proves no document was credited by two retrievers; it does not prove a retriever returned nothing. The incident's own Table 1 shows 4 of 10 queries where the keyword leg returned rows and still overlapped with nothing. Probe: `probe-ceiling.py` G2b confirms the exact theorem; the counter-example (two live disjoint lists) is Table 1 itself. Fix applied: the paper now states the ceiling as a zero-overlap screen whose cause (empty leg, disjoint legs, short lists) needs per-leg row counts; the incident is the case where the cause was an empty leg.

**A2 — Relative vs absolute step.** *Gemini, Sol, Astra, SWE-2, DeepSeek, Codex.* The observed 1.4% is the relative step 1/(k+r+1), not the absolute 1/k². Probe G1: relative step 1.64% at r=0, 1.41% at r=10. Fixed in §1. Astra's addition also applied: two identical live lists have the same relative step, so flatness was never the dead-leg signature; the scale was.

**A3 — K > k weak form was wrong as written.** *Sol, Astra, DeepSeek, Codex, SWE-2.* Rank k in both legs scores exactly 1/k (probe G2). Fixed: §2 now gives the counter-examples and reads the test as a fingerprint plus a direct overlap count when K > k.

**A4 — `ceiling_report` fired on an all-empty union.** *Gemini, Sol, Astra, Codex, SWE-2.* Probe G6 reproduced before the fix. Fixed: `mx > 0` required; test added.

**A5 — "identical Recall@100 on both collections".** *Orrery audit, then Sol, SWE-2, DeepSeek.* False on NFCorpus (0.3365 vs 0.3320). Fixed.

**A6 — "shared nothing with the dense top 100" unsupported at K=100.** *Sol, Astra, DeepSeek, Codex, SWE-2.* A ceiling query can hold overlap at ranks whose combined credit is ≤ 1/k. The runner kept only means. Fix in progress: per-query diagnostics (`*.perquery.jsonl`) now written; rerun on ryzen; the sentence will be replaced by what those rows show.

**A7 — Buggy hybrid beats fixed hybrid at nDCG@10 in 3 of 4 pairs.** *DeepSeek, Astra, SWE-2.* True from the result files. Stated in §6 now, with the mechanism (a short high-precision AND list out-ranks the OR list at 10).

**A8 — BGE query instruction not applied.** *Sol, Astra, SWE-2.* The v1.5 model card prescribes it. Fixed: applied to bge queries; dense numbers will change; rerun in progress.

**A9 — `KeywordIndex.search` swallowed every OperationalError.** *Sol, Astra, Codex.* Fixed: only parser rejections return []; other errors raise.

**A10 — `build_keyword` could adopt a half-built index; cache reuse unvalidated.** *DeepSeek; Sol, Astra.* Fixed: temp-and-rename build with a row-count check; embedding caches carry a signature (model, prefix, n, sha256 of texts); unsigned caches adopted only under an explicit flag after the changed ones were deleted.

**A11 — `"il-6"` is a phrase, not a token, under FTS5.** *DeepSeek, Astra.* True (unicode61 splits on the hyphen). The code is faithful to the production bug; §3's description is now qualified.

**A12 — Bibliography.** Bruch TOIS 42(1) is 2024 (*SWE-2, Codex*); Boteva co-author is Ghalandari (*Codex*); `sqlite_fts5` lacked a year and duplicated the section pointer (*DeepSeek*); C-Pack's current title differs from v1 (*own check*). All fixed. Added and verified against primary listings: Fox & Shaw 1994, Lee 1997, Kamphuis 2020, Webber-Moffat-Zobel 2010, Montague & Aslam 2001, Luan 2021, Nogueira 2019, Gao 2023 (HyDE), Gao 2021 (CLEAR), Cronen-Townsend 2002, Cooper 1998.

**Exonerated:** Gemini's objection to citing C-Pack for `bge-base-en-v1.5` — the C-Pack paper covers the BGE model class and BAAI's model card cites it; kept, with the version noted in run details. Table 2/3 transcription — five lanes and the Orrery audit recomputed every cell; all match.

**Inconclusive:** none.

## B. Where the lanes converge

**B1 — Separate leg health from retrieval effectiveness.** 6 of 6. Repairing the leg restores overlap and recall at depth; it does not improve nDCG@10 with a strong dense encoder here. Now the opening of §6.

**B2 — Table 1 is not auditable from the released files.** 4 of 6 (Sol, Astra, Codex, DeepSeek). Fix: `results/production-aggregates.json` + `scripts/table1.py`; the paper labels these as operator-recorded aggregates.

**B3 — Move limitations beside the claims they qualify.** 5 of 6. Done for K > k, L = 2, private evidence, and no paired uncertainty.

### Tensions to resolve

None between lanes. One between a lane and the brief: Gemini called the two §5 negative results "inflation without empirical value"; the owner chose to keep them. Kept, trimmed, and with the causal sentence Astra refuted removed.

## C. Performance

Not a performance paper. Per-condition mean query time added to the runner so the stopword-drop latency claim has a public counterpart (`bm25_or_raw` vs `bm25_or`).

## D. What each lane got wrong

- Gemini: the C-Pack objection (see Exonerated). Otherwise precise.
- DeepSeek: called the incident's 4/10 a "40% false-positive rate" of the test; it is the rate on legs returning 1–3 rows, which the paper now says. Also listed "Montague et al., 2023" (Gemini) — no such paper found; not added.
- Astra: suggested "Cooper 1998" as a monitoring citation — real, added; suggested "component-level confirmation" wording — adopted.
- Devin seats on first attempt: 0 bytes each — a harness failure, not a review failure.

## E. Proposed order of work

1. Rerun (in progress) → fill Tables 2/3 with instruction-corrected bge numbers, the `bm25_or_raw` row and timings; replace A6's sentence with the per-query facts.
2. Re-run `orrery-audit.py` (extend it to Table 1 via the aggregates file and to the per-query claims).
3. ai-lint pass; recompile; serve; second council round only on §2 and §6 if the rewrite changed the argument's shape.
