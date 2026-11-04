## 1. Round-2 fixes, hunk by hunk

All applied fixes held, verified against the tables and JSON:

- **Abstract.** "A dense list that was never empty" is the correct qualifier (every corpus ≥3,633 docs against K=100; §2's third qualification). "Across both builders… 174 query runs where the keyword list was nonempty but shared nothing" — 174 = 164 buggy + 10 fixed disjoint; 137 sit in the 1–3-document bucket, 124 of those on the three largest collections. "Two runs under the repaired builder where the lists shared one document at deep ranks" matches §5.2 (FiQA, bge and e5, both lists full 100).
- **§2.** "A nonempty list at the ceiling has maximum exactly 1/k" — right. The new "rank product is 0" clause is right: r=0 gives product 0 < k², so that document scores above 1/k at any K.
- **§2 first qualification.** "The row counts say whether each list was empty, short or full; at K ≤ k, the ceiling says the lists shared no document, whatever their lengths" — exactly the equivalence.
- **§3.1.** "Made things worse than 'every token present' suggests" is better than the old "stricter": the swallowed syntax errors are a silent failure mode, not a stricter constraint.
- **§3.2.** "Shown zero overlap on every replayed query" — six empty lists, four lists of 1–3 chunks disjoint from the dense top 60; at K=k=60 a 1/60 maximum is disjointness. Production numbers (161 ms/100k → 2–4 ms/3.5k) match Table 3 and caption.
- **§5.1.** "Outside ArguAna… 50.8 to 98.0" correct. "Saves time on every collection" — raw/or ratios 2.2–17.6 (printed as 18). "0.001–0.011 on five; FiQA +0.009/+0.013 at 5.6×" all match.
- **§5.2.** "294 of SciFact's 300" ✓. "Highest on SciDocs, FiQA and TREC-COVID, the three largest" — 12.8/41.1/88.9 vs 3.9/0 ✓; 124/378 ✓; "39 runs, all on FiQA, TREC-COVID and SciDocs" = 35 + 4, right collections. In the 1–3 bucket ceiling ⟺ disjoint exactly (keyword rank ≤2 → product ≤198 < k²), so "were disjoint" is safe.
- **§5.4.** 0.001 SciFact; 0.008–0.014 NFCorpus (bge p_holm 0.25 n.s.; nomic 0.020, e5 0.022 sig); "86 of those 159" = 73+86 nonempty, 49% "half"; TREC-COVID −0.027 to −0.039, bge p=0.043 Holm, 13 = 50−37. All correct.
- **app:run.** "Four SciFact and NFCorpus pairs with bge and nomic" is consistent with the nomic batch comparison on those two collections. Table ref to `tab:shared` is correct; bounds 4.0 / 19.0–43.7 match the JSON means.

Two nits, ranked by impact:

a) **"This is an ordering, not a size effect"** (§5.2). The reasons given — SciFact's 0/18 consistent with NFCorpus's 3.9%, collections differing in more than size — show the effect is not *demonstrated*, not that it is absent; a monotone size ordering is still compatible with the data. The round-7 wording, "not a demonstrated size effect", was the defensible claim. Restore "demonstrated".

b) **"If a query is all stopwords, the raw tokens are used"** (§3.2). The fallback fires whenever no token survives the drop, including stopword-free queries whose tokens are all under three characters; "when no token survives the drop" covers both. Pre-existing sentence, but the rewritten fix sentence beside it now lists both drop rules, so the gap is more visible.

## 2. Title

It promises exactly what the paper delivers — a zero-overlap test read off RRF's own scores on a hybrid pair — with the only unstated condition (K ≤ k for the full equivalence) carried by the abstract, as settled.

## 3. Page one

None.

## 4. Post it?

Yes. Every changed sentence checks against the result files and its neighbours; the only edit worth making before upload is restoring "demonstrated" in nit (a), a one-word hedge, not a blocker. A different approach would have run the public experiments at K ≤ k, exercising the biconditional directly with no direct-count fallback and no two-run exception — at the cost of the common K=100>k=60 setting and the two FiQA runs that show where the boundary actually sits. A shorter note without the incident would have removed every unverifiable production claim — and with it the evidence that this failure happens silently in the wild, which is the paper's reason to exist.
