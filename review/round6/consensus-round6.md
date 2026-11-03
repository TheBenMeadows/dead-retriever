# Round 6 (rewrite, round 1 of 3): twelve seats on the arXiv v2 draft (2026-11-02)

Context: IRRJ desk-rejected the journal version on 2026-11-02 ("hard to understand, as if it was AI-generated based on some personal experiences with SQLite FTS5"); the arXiv v1 (10 pp, on hold since 10-07) was withdrawn the same day. The paper was rewritten (article class, property first, incident one section, terms defined once, counts moved to tables). Before the critique, one fresh seat paraphrased the draft (explain-back, `brief-explainback.md`, SWE-2 high, 4.0 KB): every section paraphrased correctly; three terms it had to guess (singleton, row count, self-match) were defined; the paragraph it read twice (why the buggy hybrid "wins" 12 pairs) was restructured.

Brief: `brief.md` (inline form `brief-inline.md`, 129 KB, by `make-brief.sh`; Kagi/Cursor/ccx form `brief-kagi.md` with attachments; Gemini form with absolute paths).

## Lanes

| Seat | Route | Bytes | Strongest finding |
|---|---|---|---|
| GPT-6 Astra (xhigh) | Devin, inline | 7.1 KB | intro/abstract/conclusion still say scores diagnose health; "overlap count needs both id lists kept" is false |
| GPT-6.1 Sol (xhigh) | Devin, inline | 7.3 KB | same two; state zero-based ranks at the first formula |
| Gemini 4 Argon (high) | Devin, inline | 12.6 KB | §6.5 ¶3 unreadable; defensive repeats; collapse the three appendix tables; cut Appendix A; Kumaran & Allan 2007, Bendersky & Croft 2008 |
| Kimi K3 (high) | Devin, inline | 9.4 KB | two sentences break the stated rounding rule (0.010 → 0.011, 0.012 → 0.013) |
| SWE-2 (max) | Devin, inline | 7.1 KB | "twice" has no referent; Nuray & Can 2006, Aslam & Montague 2001 |
| GPT-6 Luna | Kagi (attach), 2nd try | 8.6 KB | "row counts say ... disjoint" overstates counts; the no-false-negative guarantee needs a nonempty counterpart |
| Grok 4.7 (medium) | Cursor, staged | 10.4 KB | intro ¶3 overclaims; use the inequality for "at the ceiling"; product-condition-first rewrite of the K > k paragraph |
| Gemini 3.9 | agyx, worktree | 9.6 KB | "exact-match list" is false for the pooled 1–3 bucket (fixed-builder runs inside); Table 1 forward reference |
| DeepSeek V4.1 Flash | ccx, appended | 9.1 KB | conclusion reverses the thesis; abstract applies the K ≤ k equivalence to K = 100 runs; "instrument"/"alive" survive |
| Codex GPT-5.6 Terra | ccx, appended | 9.2 KB | "174 nonempty keyword lists" counts runs; AI-tools roster is the strongest remaining AI tell |
| Claude Fable 5.1 | fresh subagent, inline | ~9 KB | "why not just log row counts" is answered only in Related Work; eleven "X, not Y" closers; Chen 2022, Wang 2021 |
| GLM-5.3 Flash | Kagi (attach) ×2, then OpenRouter (inline, MAXTOK 16000) | 0 B / 0 B / 0 B | Kagi: upload timeout, then "error decoding response body" twice; OpenRouter: 0 chars on the 66 KB inline brief (the runner's documented failure mode for a brief this size). No finding; the seat needs a short brief (under ~800 words) to answer, which this round could not give it |

Verifier: `review/orrery-audit.py` re-anchored to the new text (469 checks, all PASS after the fixes). Probes: `probe-round6.py`.

## A. Verified defects (applied)

**A1 — Rounding rule violated twice (K3, Astra, Sol, DeepSeek, SWE-2, Fable, Grok).** The paper states differences are of printed three-decimal values; §6.1 quoted raw-difference roundings. Probe K3-1: ArguAna bm25-or − bm25-or-raw printed 0.484 − 0.473 = 0.011 (raw 0.0103); FiQA R@100 0.521 − 0.508 = 0.013 (raw 0.0125). Text now 0.011 and 0.013; the audit's two checks were themselves using raw differences and now use `pdiff` (the checker had the same bug the text had).

**A2 — "174 nonempty keyword lists" (Codex, Gemini, Fable).** Probe CDX-4: 174 at-ceiling zero-overlap runs cover 78 distinct (collection, builder, query) keyword lists; the unit is runs. Abstract fixed; the abstract also now says the two overlap-present runs were under the repaired builder (Luna).

**A3 — Scores presented as diagnosing retriever health (Codex, Astra, Sol, Grok, DeepSeek, Luna).** Intro ¶3 "The fused scores can make that distinction", abstract "reveal the problem", conclusion "only the first can be answered from the scores" all rewritten to the chain: ceiling → no shared document (at K ≤ k); row counts → empty, short or full; relevance judgements → effectiveness. Luna's narrower point applied too: row counts say list size, not disjointness ("empty, short or full").

**A4 — No-false-negative guarantee needs a nonempty counterpart (Codex, Luna).** Probe CDX-2: 0 at-ceiling rows with both lists empty in 22,362 runs; every nonempty fused list has max ≥ 1/k. Stated in §2, the contribution list, Limitations.

**A5 — "twice" has no referent (SWE-2, DeepSeek, Fable).** §4.3 documents one earlier note (2026-08-07). Intro and conclusion now say it once ("eleven days earlier").

**A6 — "exact-match list" false for the pooled bucket (Gemini, Fable).** Probe: the 1–3-document bucket on SciDocs holds 138 AND runs + 3 OR runs, NFCorpus 219 + 111. Wording now "a list of one to three documents".

**A7 — "A direct overlap count needs both id lists kept past fusion" (Astra, Sol).** Overlap can be counted during fusion; the ceiling's advantage is that it can be read afterwards from a scores-only log. Rewritten in the introduction (the cost-and-placement argument moved there, Fable's structural point).

**A8 — Limitations "ten and fifteen queries" (Argon, SWE-2, Fable)** — Appendix A is cut (below), so "ten queries".

**A9 — "at the ceiling" named as equality, defined as ≤ (Argon, Grok).** Now: at the ceiling = max ≤ 1/k, with the clause that a nonempty list always holds a rank-0 document scoring ≥ 1/k, so the maximum is then exactly 1/k.

**A10 — Terms used before definition (Argon, K3, DeepSeek, SWE-2).** "row counts" defined in the intro; "at the ceiling" in the abstract; "content tokens" in Setup; "shared document" in §2; "instrument", "alive", "exact-match", "leak" removed; "Table 3 gives the buggy builder's by collection" (missing noun) fixed.

**A11 — Zero-based ranks stated at the first formula (Astra, Sol, Codex).** Abstract and intro.

**Exonerated.** DeepSeek: "no quoted token" wrong because the fixed builder does not quote — hybrid.py lines 51–56 show all three builders quote each token (reworded anyway to "no token"). DeepSeek: "905/52 = 17.4, not 18" — the 18× is the ArguAna bge run's mean_query_ms ratio 905.4/51.5 = 17.6, rounding to 18 (the paper no longer juxtaposes the pair with the ratio). Astra: "fewer after per-file deduplication" vs "before any filtering" — result assembly dedups per parent document keeping its best chunk, which cannot lower the maximum; stated in §4.3.

## B. Convergent judgements (applied)

- Cut Appendix A (Argon, Codex, Astra, Sol, DeepSeek, Gemini, Grok, Fable; K3 wanted it trimmed). Cut; one sentence in Appendix C points at `production-aggregates.json`.
- Collapse the three per-encoder appendix tables (Argon, Codex, Astra, Sol, SWE-2, Gemini, Grok, Fable). Replaced by Table 7 (BM25-only conditions with query ms) and Table 8 (shared documents by encoder). Audit checks both.
- Stop reciting tables in prose (every seat): §6.1 content-token list → a "content" column in Table 2; §6.2 per-collection short-list counts → two columns in Table 3; §6.4 sweep ranges → one sentence; §6.5 ¶3 halved, "(before rounding)" parentheticals gone.
- Cut the review-scar sentences (Argon, Astra, Sol, Fable, SWE-2, Grok): "That is close to arithmetic", "The fix has two parts, and the second is not cosmetic", "Two in 22,362 is rare, but it is not zero", "checked by nobody but the operator", "Two questions run through this section", "whether or not the list was any good", "which is what a dead retriever looks like from the outside"; the not-a-controlled-comparison caveat now appears once (Limitations), the no-query-log inference twice (§4.3 where it belongs, Limitations as a limitation).
- Shorten the AI-tools section to roles and responsibility (Codex, Astra, Sol, DeepSeek, Luna).
- Keep "What to log" before Limitations (Codex, Astra, Sol, Argon, SWE-2, DeepSeek, Luna; K3 and Gemini would fold it into the conclusion). Kept; its K ≤ k and K > k rules are separate sentences, "on more than a few queries" dropped (Astra, Sol), the effectiveness sentence names the metric (Grok).
- Related work moved after "What to log" (Argon) so the derivation runs straight into the incident; six references added after Crossref/ACL Anthology verification: Kumaran & Allan 2007, Bendersky & Croft 2008 (conjunctive matching fails on verbose queries), Nuray & Can 2006 (system quality from agreement with fused output), Aslam & Montague 2001, Chen et al. 2022 and Wang et al. 2021 (BM25 + dense on BEIR).
- §4 merged into two subsections (Gemini); the relative-step sentence split (Grok); the K > k paragraph leads with the product condition (Grok).

### Tensions (not silently picked)

- **Title.** Nine seats judge "Agree on Nothing" colloquial or as hiding the K ≤ k condition; two (K3, SWE-2) accept it. Alternatives offered: "The 1/k Ceiling: A Zero-Overlap Test for Hybrid Retrieval" (DeepSeek and SWE-2, independently), "A Score Ceiling for Detecting Zero Overlap in Reciprocal Rank Fusion" (Astra), "Detecting Zero Retriever Overlap in Reciprocal Rank Fusion" (Gemini), "The 1/k Ceiling in Reciprocal Rank Fusion Detects Zero Top-K List Overlap" (Luna). Ben's call; the draft keeps the current title until he rules.
- **The sweep (§6.4).** Codex and DeepSeek would cut it; Grok says "do not cut the sweep"; the rest would shorten it. Shortened, table kept.
- **Section 4 length.** Astra and Sol: compress by a third; K3, SWE-2, DeepSeek, Grok, Luna, Fable: right length. Lightly trimmed (dates, the sibling-engine sentence kept).

## C. Prior art (question 5)

No seat named a prior statement of the 1/k maximum as an overlap test or a published report of a silently inert retriever in a hybrid; several (Argon, Astra, Fable, SWE-2) note that vendor RRF documentation (Elasticsearch, OpenSearch, Azure AI Search, Vespa) walks through the 1/(k+r) contribution and may state the singleton maximum, none confident enough to cite. The paper now says "I know of no earlier statement ... that is what I could find, not evidence that there is none". Rejected as citations: Sculley et al. 2015 (Gemini; too far), Shokouhi & Si 2011 (Gemini; federated-search monitoring is not this), Beitzel et al. 2004 (Fable; the Crossref hit is a different LNCS paper, the JASIST article was not located), Carmel & Yom-Tov 2010 (DeepSeek; QPP survey, the 2002 citation suffices).

## D. What each lane got wrong

DeepSeek: the fixed builder does quote tokens; 17.4× from printed values. Luna: could not see refs.bib (not attached on the Kagi route) and said so. GLM: two Kagi stream failures, no finding. Gemini: proposed folding "What to log" into the conclusion against seven seats. K3: "fold Table 3 into Table 2" would lose the per-encoder ranges.

## E. Result

17 pages (from 20), 0 overfull, audit 469/469, tests ok, ai-lint 30.1% (MIXED; the 28.6% HUMAN reading before this pass was on the same text minus the bibliography and tables that pdftotext now includes more of). Round 2 of 3 on the rewrite: diff since this round plus this record, same roster, after Ben's read.
