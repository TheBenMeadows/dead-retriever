# Round 8 (rewrite, round 3 of 3, confirmation): eleven seats on the diff since round 7 (2026-11-03)

Brief: `brief.md` (unit = `diff-since-round7.patch` with the full `main.tex` and result files inline; `make-brief.sh`). Title set by Ben before the round: "The $1/k$ Ceiling in Reciprocal Rank Fusion: A Zero-Overlap Test for Hybrid Retrieval". GLM retired after round 7 (five empty replies).

Launch note: five Devin seats started in the same minute tripped Cognition's per-minute request limit ("Reached request rate limit ... reset in 1 minute"); Astra got through, the other four were relaunched 40 s apart. Future rounds: stagger Devin launches.

## Lanes

| Seat | Route | Bytes | Verdict |
|---|---|---|---|
| Codex GPT-5.6 Terra | ccx, appended | 3.1 KB | every hunk holds; page one: none; post it |
| GPT-6 Luna | Kagi (attach) | 3.6 KB | abstract/intro opening claim lacked the K <= k scope (blocking); otherwise holds |
| GPT-6 Astra (xhigh) | Devin, inline | 4.2 KB | two overclaims introduced by round-2 wording (§5.5 causal link to Wang/Chen; §5.2 "not a size effect"); post after |
| Gemini 3.9 | agyx, worktree | 3.3 KB | all 30 hunks hold; page one: none; post it |
| GPT-6.1 Sol (xhigh) | Devin, inline (relaunch) | 4.3 KB | the same two as Astra; post after |
| Gemini 4 Argon (high) | Devin, inline (2nd relaunch) | 5.4 KB | every hunk holds; page one: none; post it |
| SWE-2 (max) | Devin, inline (relaunch) | 4.2 KB | every hunk re-derived against the JSON; "demonstrated" size-effect hedge (same as A3); the stopword fallback fires on any empty survivor set, not only all-stopword queries; post it |
| Kimi K3 (high) | Devin, inline (2nd relaunch) | 4.6 KB | every hunk holds, every count re-derived; page one: none; post it |
| Grok 4.7 (medium) | Cursor, staged | 2.9 KB | the Wang/Chen "one reason" clause (as A2) and the size-effect wording (as A3); counts re-derived; post it |
| DeepSeek V4.1 Flash | ccx, appended | 3.9 KB | A2 and A3 again; "Sections 4 and 5 repeat the measurement" (only §5 measures); abstract "usually with RRF" is an uncited frequency claim → "often"; post it |
| Claude Fable 5.1 | fresh subagent, inline | ~5 KB | every count re-derived from the JSON; Wang/Chen sentence (as A2) plus "confirm Chen's fusion is weighted"; conclusion and intro antecedents ("the ceiling had been read as", "it had been written down as flat"); "matched no chunk" vs §3.1's "almost never"; redundant "whenever" in §5.2; post it |

Verifier: `review/orrery-audit.py` 469/469 after the edits below.

## A. Verified and applied

**A1 — Page-one scope (Luna).** Abstract: "This paper shows that, at per-retriever depth $K \le k$, the maximum fused score reveals whether the two lists shared any document." Introduction ¶3: "The fused scores show something narrower than health: at $K \le k$, whether the two lists shared any document at all." The derivation two sentences later already carried the condition; now the claim does too.

**A2 — §5.5 causal overreach (Astra, Sol).** "one reason Wang ... and Chen ... find that BM25 helps ... under weighted score interpolation" made RRF's equal weighting an explanation of other papers' gains. Now an independent sentence: "Wang et al. on MS MARCO and Chen et al. on BEIR report gains from combining BM25 with dense retrieval under weighted score interpolation."

**A3 — §5.2 "This is an ordering, not a size effect" (Astra, Sol).** The data neither establish nor exclude a size effect. Now "This ordering does not establish an effect of corpus size: ...".

**A4 — Fallback condition (SWE-2).** "If a query is all stopwords, the raw tokens are used" understated the rule: the fallback fires whenever no token survives the drop (all-stopword queries and queries whose tokens are all under three characters). Now "If no token survives the drop, the raw tokens are used", matching `or_bm25` in `hybrid.py` and the Setup description.

**A5 — Fable's antecedents and strength of claim.** The Wang/Chen sentence no longer asserts the fusion type for Chen et al. (unconfirmed from the inline material): "Wang et al. on MS MARCO, by score interpolation, and Chen et al. on BEIR report gains from combining BM25 with dense retrieval." Conclusion: "the ceiling held on all ten replayed queries; eleven days earlier the scores had been noted only as flat" (the flatness was read, the ceiling was not). Intro ¶4: "the scores had been written down as 'flat near the top'" (not "it", the maximum). Intro ¶4: "almost never matched a 1,400-character chunk" (four of the ten replayed keyword lists were nonempty; §3.1 says "almost never"). §5.2: the second "whenever" clause dropped.

**A6 — DeepSeek's two (applied).** §3.2 now says "Section 5 repeats the measurement on public collections" (Section 4 is setup). Abstract sentence 1: "often with reciprocal rank fusion", not "usually".

## B. Verdicts

Eleven of eleven: post it. Codex, Gemini, Argon, K3 with no change; Astra, Sol, Grok, DeepSeek, SWE-2, Fable after the wording edits A2 to A6 (all applied); Luna after A1 (applied). No seat found a number, table or significance claim wrong against the result files, and none asked for a structural change. The round is closed; the text after A1 to A6 is the version that goes to Zenodo and arXiv.

## C. Reconsider the approach (the round-3 close)

What the seats say a different paper would have been: a controlled-failure study (Astra, Sol) that plants empty, truncated, stale and irrelevant-but-overlapping retrievers and compares what the ceiling, the row counts and a direct overlap count each detect, with false-alarm rates; or a parameter study over $k$, $K$ and fusion weights with adaptive-fusion baselines (Gemini, Luna); or a multi-system observability study with real query logs (Codex). Each would gain external validity or a conventional venue slot and would cost the present paper's one exact RRF property, its incident-to-reproduction arc, and new experiments. None of the seats recommends doing that before posting; the consensus is to post this paper as the compact result and leave the controlled-failure study as a possible later paper.
