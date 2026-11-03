**1. What this paper proposes**

The paper proposes a zero-cost diagnostic for hybrid search systems that fuse ranked lists with reciprocal rank fusion (RRF): read the maximum fused score per query. Because a document returned by only one retriever scores at most 1/k and a document returned by two retrievers scores above 1/k (provided each retriever's list is cut at depth K ≤ k), a fused list whose top score sits at exactly 1/k — called being "at the ceiling" — provably contains no document both retrievers returned. The test detects zero overlap between retriever lists; it does not by itself detect which retriever failed or whether either is healthy, since two nonempty but disjoint lists produce the same ceiling as an empty list, so per-retriever row counts are needed to tell those cases apart.

**2. How the system in the incident works, according to this document**

The author's personal search engine runs two retrievers over the same text chunks across five SQLite databases: an FTS5 keyword index ranked by BM25, and a 768-dimensional embedding index searched by exact cosine, each cut at K = 60 and fused by RRF with k = 60. The keyword query builder wrapped every query token in quotes, which FTS5 interprets as an implicit AND requiring all phrases in one row — so conversational queries matched nothing in the ~1,400-character chunks, while short technical queries still matched and masked the bug. The dense retriever filled every list, so results always looked complete. The bug was found when keyword row counts were logged on ten real queries and came back zero on all conversational ones; the maximum fused score had been 1/60 on all ten, and that flatness had twice been recorded as an intrinsic property of RRF rather than a symptom.

**3. What the experiments show, according to this document**

On six BEIR collections (SciFact, NFCorpus, ArguAna, SciDocs, FiQA, TREC-COVID) with three encoders (bge-base, nomic-embed-v1.5, e5-base-v2), run at K = 100 > k = 60 across 22,362 hybrid query runs, the buggy builder returned nothing on 50.8% to 98.0% of queries on five collections, and the ceiling never missed an empty keyword list — which is guaranteed with two retrievers. The ceiling also appeared over 174 runs where the keyword list was nonempty but disjoint from the dense list (mostly short lists on larger corpora), and twice where the two lists shared a single document ranked too deep in both to exceed 1/k. ArguAna is a blind spot by construction: each query is itself a corpus document, so the buggy retriever always returns the query's own text — nonempty, always shared with the dense list, almost never relevant — and the ceiling never fires. Fixing the keyword retriever raised overlap everywhere but made the hybrid beat the dense retriever alone at nDCG@10 in only 5 of 18 collection–encoder pairs (2 significant), losing in 13 (5 significant).

**4. Undefined or unclear terms**

- "at the ceiling": defined in the paper as a fused list whose maximum score is ≤ 1/k; I took it to mean the boundary where no document received contributions from two retrievers.
- "singleton": a document returned by exactly one retriever.
- "row counts": the number of documents each individual retriever returned, before fusion.
- "self-match" (my label): ArguAna's situation where the keyword list returns the query's own text as a document.
- "one-based vs zero-based RRF": rank indexing convention; it shifts the ceiling to 1/(k+1).
- The named reviewer models in the AI-tools note (GPT-6, Fable 5.1, etc.): presumably model codenames; I could not map them to public names.

**5. Where you lost the thread**

Section "Does repairing the keyword retriever improve retrieval?" — the passage explaining why the buggy hybrid beats the repaired one in 12 pairs required a second read, because it hinges on the buggy builder effectively abstaining (empty lists make the hybrid identical to dense), which is easy to misread as the buggy retriever helping.
