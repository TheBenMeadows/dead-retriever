## Corrections before posting

### 1. Section 2: distinguish the general theorem from the two-retriever alarm

For positive integer \(k\), the separation bound, the implication \(\max s>1/k\Rightarrow\) overlap at any \(K\), and
\[
\frac1{k+r_1}+\frac1{k+r_2}>\frac1k
\iff r_1r_2<k^2
\]
are correct. So are the one-based ceiling \(1/(k+1)\) and strict separation for \(K\le k+1\).

However:

- Explicitly assume integer \(k>0\); otherwise the exact depth conditions are \(K<k+1\) and, one-based, \(K<k+2\), not the displayed integer equivalents.
- **“An empty leg always produces the ceiling”** requires **two retrievers**: with three, one can be empty while the other two overlap and exceed the ceiling.
- Conversely, the zero-overlap equivalence works for arbitrary \(L\); remove **“and two retrievers”** from §8’s statement of its requirements. The pairwise-disjoint \(L>2\) remark is correct.
- At \(K=k+1\), the deepest two-list contribution equals \(1/k\); a contribution strictly below it requires \(K\ge k+2\).

### 2. Sections 1 and 5 retain the old single-list inference

Section 1’s **“one retriever’s rank list passed through the RRF formula”** and **“signature of the single list”** contradict the four live-but-disjoint cases. Disjoint lists also produce reciprocal-integer scores, including repeated scores at corresponding ranks. Neither the scale nor the staircase identifies one contributing retriever. Describe *singleton contributions*, not a single source list.

Section 5’s **“the relative step is a property of the formula at any overlap”** is false. The derivation covers consecutive singleton ranks and identically ranked lists with constant multiplicity, not arbitrary overlap. If only the rank-0 document is shared, the first two fused scores can be \(2/60\) and \(1/61\), giving a relative drop of \(31/61\approx50.8\%\), not \(1/61\). Also, the step derivation is in §1, not §2.

### 3. Abstract, title, and final advice: retain the qualifications

The abstract’s **“restores overlap and recall at depth”** misstates the repair comparison: bge/NFCorpus Recall@100 falls from **0.341377 to 0.337309**. Recall rises relative to dense alone, but not consistently relative to the buggy hybrid; name the comparator.

**“The fusion is fusing nothing”** is also too strong: merging disjoint lists still changes the candidate set and ranking. What disappears is reinforcement from multiple retrievers.

The title can function as shorthand for the conditional theorem. Section 9 cannot: **“the retrievers are not agreeing on anything”** needs \(K\le k\), or \(K\le k+1\) one-based. At greater depths, require direct overlap counts; repeated ceiling observations do not remove that mathematical limitation.

The abstract’s “within one percentage point” claim and the main tables’ effectiveness values and reported deltas agree with the supplied JSON.

### 4. Table 4: numerical transcription versus prose

The table entries and caption’s encoder-difference bounds match the sweep files. For **\(K=60\), across both encoders**, the ranges are:

| Keyword cap | Observed ceiling rate |
|---|---:|
| \(n=1\) | 8.7–15.1% |
| \(n=3\) | 2.7–6.7% |
| \(n=10\) | **0.7–2.3%**, not “1 to 2%” |

The first two prose ranges are whole-percentage approximations; use consistent precision.

**“Usually under 1%”** does not hold for the preceding \(K=60\) scope at \(n\ge20\): only **3 of 8 cells** are below 1%.

**“A deeper dense list lowers every figure”** should be **“never increases these rates”**: nomic/SciFact at \(n=20,50\) remains zero.

### 5. The sweep measures a cap, not a known realized length

**“A live leg of known length”** and **“a list of twenty or more”** misdescribe the experiment. Taking the first \(n\) documents produces length \(\min(n,\text{available rows})\). The same 298 NFCorpus queries remain in every cell, including naturally short lists.

Indeed, the preceding paragraph attributes the full-depth NFCorpus ceiling cases to lists containing one or three documents; these remain in the large-\(n\) cells.

The measured quantity is
\[
P(\text{ceiling}\mid\text{keyword nonempty},\ \text{truncation cap }n),
\]
not the ceiling rate conditional on the retriever naturally returning \(n\), or at least \(n\), documents. Consequently, the operator advice about naturally returned “a dozen or more” versus “one or two” is not calibrated by this experiment. Restrict it to these artificial truncations, or use existing row-count diagnostics to report the relevant conditional rates.

### 6. “The \(K>k\) leak never occurred”: correct observation, inflated exposure

The **60 cells / 17,940 evaluations** are correct, and every supplied cell has zero fired-with-overlap rate. Keep the claim scoped to these evaluated configurations.

But most configurations cannot exhibit this failure mathematically. With keyword cap \(n\) and dense depth \(K\), every overlap clears the ceiling whenever
\[
(n-1)(K-1)<k^2.
\]
Thus only **\(K=100,\ n\in\{50,100\}\)** permits hidden overlap among the tested configurations: **8 cells and 2,392 evaluations**, themselves repeated queries. Distinguish those observations from the configurations where absence is guaranteed.

### 7. Section 5: HyDE is misclassified

HyDE generates hypothetical documents from queries to construct query representations; it does not expand indexed documents, so remove its citation from the heading-prefix/document-expansion claim.

## Missing or unfinished

- Replace the repository-URL placeholder before submission.
- Define the timing boundary: Table 2’s “keyword and fusion only” caption does not explain its nonzero dense-only timings.
- State the numerical ceiling-comparison tolerance and that the diagnostic uses unweighted RRF scores before downstream filtering or score transformations.
