# Round 7 (rewrite, round 2 of 3): twelve seats on the diff since round 6 (2026-11-02)

Brief: `brief.md` (unit under review = `diff-since-round6.patch` + `diff-refs.patch`, with the full `main.tex` and the result files inline; `make-brief.sh` builds the inline, Gemini, Kagi and short-GLM variants). Title now "The $1/k$ Ceiling: A Zero-Overlap Test for Hybrid Retrieval" (Ben's choice after round 6).

## Lanes

| Seat | Route | Bytes | Strongest finding |
|---|---|---|---|
| Kimi K3 (high) | Devin, inline | 6.6 KB | Wang et al. 2021 is MS MARCO/TREC DL, not BEIR (two sentences); abstract's guarantee clause lacks the nonempty-counterpart condition |
| GPT-6 Luna | Kagi (attach) | 4.1 KB | same two; conclusion's "scores can say whether two retrievers agreed" needs K <= k; Kumaran/Bendersky support query reduction, not conjunctive failure |
| DeepSeek V4.1 Flash | ccx, appended | 5.4 KB | new §2 sentence "a ceiling over a full list means two full lists that share nothing" is false at K > k (the paper's own FiQA runs); "so on a nonempty list the maximum is then exactly 1/k" misreads as unconditional |
| Gemini 4 Argon (high) | Devin, inline | 9.1 KB | abstract lost the predicate "at the ceiling" on the 174 + 2 runs and scopes them to the buggy builder (164 buggy + 10 repaired); "the 294 SciFact queries" orphaned |
| GPT-6.1 Sol (xhigh) | Devin, inline | 5.6 KB | "two full lists" also wrong at K = k (a full keyword list and a short disjoint dense list); Nuray & Can "degenerate case" misstates the relation; Results opener points at an appendix that no longer holds every condition; CPU-reproduction claim widened to e5 |
| SWE-2 (max) | Devin, inline | 7.1 KB | same locator and Wang; "50.8 to 98.0%" should name the exclusion of ArguAna; two orphaned bib entries (nogueira2019, anthropic2024) |
| Codex GPT-5.6 Terra | ccx, appended | 4.5 KB | Wang; locator; short-list sentence rewrite |
| GPT-6 Astra (xhigh) | Devin, inline | 5.4 KB | Nuray & Can conflates two meanings of agreement (highest value); CPU claim; "The fused scores had said so" has a loose antecedent |
| Grok 4.7 (medium) | Cursor, staged | 6.0 KB | the same Wang, Kumaran/Bendersky, Nuray, locator and counterpart findings; the §2 "because" clause justified only the second of two claims (applied) |
| Gemini 3.9 | agyx, worktree | 7.5 KB | the TREC-COVID sentence was orphaned at the end of the "12 wins" paragraph; "content words" vs "content tokens"; appendix pointer for shared counts should be Table 8; stopword-drop pointer; (wrongly passed Wang as BEIR) |
| Claude Fable 5.1 | fresh subagent, inline | ~7 KB | Wang; CPU claim; the `\par}` of a `\sloppy` group split the ArguAna paragraph mid-argument; one note quoted two ways; "The fused scores had said so" antecedent; title should say "Reciprocal Rank Fusion", not "Hybrid Retrieval" |
| GLM-5.3 Flash | OpenRouter, short brief (title + abstract + intro + conclusion, 1,409 words) ×2 (MAXTOK 12000, 24000) | 0 B / 0 B | the whole output budget goes to hidden reasoning (in=2010, out=12000, 0 chars); after two Kagi failures in round 6 the seat has produced nothing on this paper across five attempts and is retired for it |

Verifier: `review/orrery-audit.py` 469/469 after the fixes. Probes: `probe-round7.py` (ARG-1 174 = 164 buggy + 10 repaired, the 2 overlap-present under the repaired builder; DS-1 two at-ceiling runs with both lists full and a shared document; SOL-1 a full keyword list plus one disjoint dense document is at the ceiling at K = k; SOL-2 no e5 CPU run exists).

## A. Verified defects (applied)

**A1 — Wang, Zhuang & Zuccon 2021 credited with BEIR results (K3, Luna, DeepSeek, Argon, SWE-2, Codex, Astra).** The ICTIR paper interpolates BM25 with BERT dense retrievers on MS MARCO passage ranking (its own text: "gains ... significant only for MS MARCO"). Both sentences now name MS MARCO for Wang and BEIR for Chen et al.

**A2 — "a ceiling over a full list means two full lists that share nothing" (DeepSeek, Sol, Astra).** False at K > k (probe DS-1: FiQA bge query 1391 and e5 query 104, both lists 100 documents, one shared, at the ceiling) and, as Sol noted, fullness of one list says nothing about the other at any depth (probe SOL-1). Now: "The row counts say whether each list was empty, short or full; at K <= k, the ceiling says the lists shared no document, whatever their lengths."

**A3 — "so on a nonempty list the maximum is then exactly 1/k" (DeepSeek).** Reads as unconditional. Now "so a nonempty list at the ceiling has maximum exactly 1/k".

**A4 — Abstract and conclusion state the no-false-negative guarantee without the nonempty counterpart (K3, Luna, DeepSeek, SWE-2).** Both now say "with two retrievers and a dense list that was never empty". The conclusion's last sentence is restricted to K <= k, with the direct count at greater depth (Luna).

**A5 — Abstract dropped "at the ceiling" from the 174 + 2 runs and scoped them to the buggy builder (Argon).** Probe ARG-1: 164 buggy + 10 repaired zero-overlap runs, the two overlap-present runs under the repaired builder. One sentence now covers both builders and says the fused list was at the ceiling.

**A6 — Results opener claimed Appendix A holds every condition (Sol, SWE-2, Codex, Astra).** It holds the keyword-only results, timings and shared counts; Tables 5 and 6 hold the rest. Rewritten.

**A7 — CPU-reproduction claim widened to e5 (Sol, Astra).** Probe SOL-2: no e5 CPU run exists. Restricted to the four bge/nomic pairs.

**A8 — Nuray & Can described as the ceiling's "degenerate case" (Sol, SWE-2, Astra).** Their agreement is between a system and the fused output; the ceiling is overlap between inputs. Rewritten.

**A9 — Kumaran & Allan and Bendersky & Croft cited for conjunctive-query failure (Luna, Argon, Sol, Codex, Astra).** They study query reduction and key-concept selection for verbose queries under language-model retrieval. Sentence narrowed to that.

**A10 — Orphans.** "the 294 SciFact queries" (Argon) → "the 294 of SciFact's 300 queries"; `nogueira2019doc2query` and `anthropic2024contextual` removed from refs.bib (SWE-2); Limitations "production measurements used here are on ten queries" against the appendix pointer's seven to fifteen (DeepSeek).

**A11 — Local antecedents and stops (Astra, SWE-2, Luna, DeepSeek, Codex).** "The fused scores had said so" → "had shown zero overlap"; "With two retrievers it must" → "…whenever the other list is nonempty"; "These are read from the lists as fused" → the runner sentence; "Two in 22,362 is why" → "Two such runs in 22,362 are why"; "Outside ArguAna, which Section 5.3 treats separately, the buggy builder's empty rate runs from…"; the short-list sentence names SciDocs, FiQA and TREC-COVID; "It is one, but it was the wrong thing to look at" → "Flatness is a property of RRF; …"; "Two details made the constraint stricter" → "made things worse than 'every token present' suggests"; "The ceiling sits upstream of that choice" → "applies to unweighted RRF scores as assigned; it does not bear on which fusion function to choose".

**A12 — Gemini's four (applied).** The TREC-COVID contrast folded into the NFCorpus sentence of the "12 wins" paragraph (TREC-COVID with nomic is one of the 12; bge and e5 are not); "content words" → "content tokens"; the shared-count pointer → Table 8; the stopword-drop pointer → the setup section that defines the builder.

**A13 — Fable's layout and wording (applied).** The `\sloppy` group in §5.5 ended with `\par}` after two sentences, so "The other three gains" opened a new paragraph; moved to the paragraph's end. The 2026-08-07 note is now quoted one way ("flat near the top") in the introduction and §3.2. The fix paragraph and the Table 1 sentence in §3.2 shortened; intro ¶3 opens "The fused scores show something narrower than health: whether the two lists overlapped at all."

### Tension (not silently picked)

- **Title, "Hybrid Retrieval" vs "Reciprocal Rank Fusion" (Fable).** The test is arithmetic on RRF's $1/(k+r)$; a reader fusing by convex combination gets nothing from it. Fable proposes "The $1/k$ Ceiling: A Zero-Overlap Test for Reciprocal Rank Fusion". Ben chose the current title after round 6; the record notes the alternative for his decision, and the draft is unchanged.

**Exonerated / not applied.** DeepSeek's title subtitle "at K <= k" (Codex, Luna also note the omission; K3, Argon, SWE-2, Astra, Sol judge the condition abstract-level): the abstract carries the condition in its third sentence; title unchanged. Argon's Table 3 header "buggy builder, per encoder": the caption already says the first column is encoder-independent; header kept. K3's "the 174 lists reduced to 'a short list'": superseded by the A5 rewrite.

## B. Verdicts on posting

K3, DeepSeek, Argon, Sol, SWE-2, Codex, Astra: post after the corrections above (all now applied). Luna: not before the nonempty-counterpart and K <= k clauses (applied). No seat asked for a structural change.

## C. Round 3

Confirmation round on the diff since this round plus this record, same roster minus GLM; close with "reconsider the approach" per the three-round rule. After it: Ben's APPROVE for the new Zenodo version and the arXiv submission (each its own approval).
