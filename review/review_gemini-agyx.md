### 1. Derivation (Section 2 & Section 1)

* **Relative vs. Absolute Score Decay**: Section 1 ([main.tex:31](file:///Users/bemeadows/Projects/dead-retriever/paper/main.tex#L31)) conflates absolute score step size with relative percentage change. The adjacent rank drop in RRF is:
  $$\Delta s = \frac{1}{k+r} - \frac{1}{k+r+1} = \frac{1}{(k+r)(k+r+1)} \approx \frac{1}{k^2}$$
  For $k=60, r=0$, $\Delta s = 1/3600 \approx 0.000278$ (absolute). However, the *relative* drop between adjacent ranks is:
  $$\frac{\Delta s}{s(r)} = \frac{1}{k+r+1} \approx \frac{1}{k}$$
  For $k=60$, $1/61 \approx 1.64\%$, which explains the observed ~1.4–1.6% relative change. Equating relative rank decay directly to $1/k^2$ is mathematically incorrect.
* **Failure Case under $K \le k$**: The derivation $s(d) \ge \frac{2}{k+K-1} > \frac{1}{k}$ holds strictly for $K \le k$ under the assumption that both retrievers return at least $K$ candidate documents. If a retriever returns $M < K$ documents, a document at rank $r_1$ in leg 1 and rank $r_2$ in leg 2 still satisfies $r_1, r_2 \le K-1$, so the bound holds.
* **Weak-Form Limitations ($K > k$)**: In Section 2 ([main.tex:50-51](file:///Users/bemeadows/Projects/dead-retriever/paper/main.tex#L50-L51)), the claim that $\max_d s(d) = 1/k$ strictly implies the top document came from one retriever at rank 0 is incomplete. When $K > k$ (e.g., $K=100, k=60$), multi-leg documents can exist at deeper ranks (e.g., $r_1=90, r_2=90 \implies s(d) = 2/150 = 0.0133 < 1/60$). If no document occupies rank 0 in any single leg, $\max_d s(d) \le 1/k$ can occur even when multi-leg documents exist in the result set.

---

### 2. Numbers & Verification

* **Discrepancies**: All rounded values in Tables 1–3 match the JSON result files (`results/beir_*.json`).
  * SciFact `bge-base-en-v1.5`: `bm25_and` `recall_100` is 0.0175 (rounds to 0.018 in Table 2).
  * NFCorpus `nomic-embed-text-v1.5`: `hybrid_and` `multi_leg_docs_mean` is 3.70588 (matches 3.7 in Table 3); `hybrid_or` is 20.9938 (matches 21.0 in Table 3).
* **False-Positive Reading Inference**: Reading false positives as $\text{at\_ceiling\_rate} - \text{kw\_empty\_rate}$ (3 queries on NFCorpus before fix, 2 after) is valid **only if** $\text{kw\_empty} \subseteq \text{at\_ceiling}$. This subset relation holds if and only if the dense retriever returns at least 1 document for every query (guaranteeing a rank-0 score of $1/k$). Because dense retrieval on BEIR never returns 0 documents, empty keyword legs always yield $\max_d s(d) = 1/k$. The difference therefore accurately isolates non-empty keyword queries whose retrieved documents failed to overlap in the top $K$ with dense results.

---

### 3. Claims vs. Evidence

* **Unwarranted Collapse Claim**: Section 6 ([main.tex:128](file:///Users/bemeadows/Projects/dead-retriever/paper/main.tex#L128)) states that `hybrid-and` "collapses to dense-only retrieval". Table 2 & Table 3 show this is false for NFCorpus: `hybrid-and` achieves 0.377 nDCG@10 (bge) and 0.361 (nomic) vs `dense` 0.369 and 0.347. Because 49.2% of NFCorpus queries return non-empty keyword results under `bm25-and`, fusion still occurs and actually *improves* nDCG@10 over pure dense retrieval.
* **Missing Supported Conclusions**: The tables demonstrate that RRF with default $k=60$ hurts nDCG@10 when combining a strong dense model (bge) with BM25 on SciFact (0.730 vs 0.738) and NFCorpus (0.358 vs 0.369), but improves Recall@100 on a weaker dense model (nomic) on SciFact (0.958 vs 0.928). The paper fails to highlight how fusion effectiveness varies inversely with dense retriever quality under fixed $k$.

---

### 4. Code Inspection

* **`and_quoted` Query Syntax**: In [`dead_retriever/hybrid.py:47-48`](file:///Users/bemeadows/Projects/dead-retriever/dead_retriever/hybrid.py#L47-L48), `fts_query` formats queries as `"t1" "t2" ...`. FTS5 interprets adjacent quoted strings as phrase sequences (implicit AND), matching Section 3.
* **`ceiling_report` Defect**: In [`dead_retriever/hybrid.py:132`](file:///Users/bemeadows/Projects/dead-retriever/dead_retriever/hybrid.py#L132):
  ```python
  at_ceiling = len(ranks) > 1 and mx <= 1.0 / k + eps
  ```
  If both retrievers return 0 documents, `mx = 0.0 <= 1/60 + eps`, causing `at_ceiling` to evaluate to `True`. A total system outage (0 results) is falsely categorized as a single-leg ceiling signature.
* **`rrf_fuse` Handling**: In [`dead_retriever/hybrid.py:105-108`](file:///Users/bemeadows/Projects/dead-retriever/dead_retriever/hybrid.py#L105-L108), duplicates within a leg are deduplicated (`if d in ranks[name]: continue`), correctly preventing self-fusion credit.
* **`beir_run.py` Experimental Setup**:
  * In [`scripts/beir_run.py:66-69`](file:///Users/bemeadows/Projects/dead-retriever/scripts/beir_run.py#L66-L69), `docs` are inserted as `(doc_id, title, text)`. Default FTS5 BM25 weights `title` and `text` equally (1.0, 1.0), which under-weights title matches compared to standard tuned BM25 baselines.

---

### 5. Citations & Related Work

* **Incorrect Citations**:
  * [main.tex:101](file:///Users/bemeadows/Projects/dead-retriever/paper/main.tex#L101): `bge-base-en-v1.5` is cited using `\citep{xiao2023cpack}`. `xiao2023cpack` refers to "C-Pack: Packaged Resources To Advance General Chinese Embedding", which covers Chinese models, not the English BGE model family (`bge-base-en-v1.5`).
* **Missing Related Work**:
  * **Score Distribution & Fusion Analysis**: Missing foundational data fusion literature on overlap metrics and score distribution behavior in CombSUM/CombMNZ (Fox & Shaw, 1994; Lee, 1997).
  * **System Health & Pipeline Diagnostics**: Missing references to rank fusion normalization techniques (e.g., Montagu et al., 2023) and BM25 parameter sensitivity in hybrid pipelines (Kamphuis et al., 2020).

---

### 6. Prose & Structure

* **Fluff & Inflation**:
  * Section 4 ([main.tex:88-89](file:///Users/bemeadows/Projects/dead-retriever/paper/main.tex#L88-L89)): "the second lesson of the incident: a copied bug costs one investigation per copy..." is textbook software engineering filler.
  * Section 5 ([main.tex:90-97](file:///Users/bemeadows/Projects/dead-retriever/paper/main.tex#L90-L97)): Spending two full paragraphs detailing un-reproducible internal experiments on $N=7$ and $N=15$ private queries inflates the paper's scope without adding empirical value.
* **Misplaced Limitations**: Section 8 contains core mathematical caveats—specifically that $K > k$ invalidates the strict ceiling theorem—that belong directly in Section 2 where $K > k$ is introduced.
