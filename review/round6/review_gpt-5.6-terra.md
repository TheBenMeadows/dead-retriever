## Highest-impact findings

1. **The paper still occasionally equates a score symptom with a retriever failure.** This is the central conceptual trap the paper otherwise works hard to avoid.

   - Introduction: “**The fused scores can make that distinction.**” The preceding distinction is between a retriever that legitimately finds nothing relevant and one that is broken. The ceiling cannot make that distinction; a row count only distinguishes an empty list from a nonempty disjoint one, and neither proves *why* it is empty. Rewrite:
     > “The fused scores can show that the two input lists have no top-\(K\) overlap. Per-retriever row counts then distinguish an empty list from a nonempty disjoint list; investigating the cause still requires query and system context.”

   - Abstract: “**This paper shows that the fused scores reveal the problem.**” This overclaims before the abstract immediately retracts it with “The test measures overlap, not health.” Replace with:
     > “This paper shows that fused scores can reveal zero overlap between the input lists, a useful trigger for inspecting retriever activity.”

2. **The “no false negatives” claim needs the nonempty counterpart condition everywhere.** Section 2 correctly states, “If one of two lists is empty and the other is not,” but then concludes that the test has “no false negatives for an empty list.” If both retrievers return nothing, the fused list is empty and \(\max_d s(d)\) is undefined; it is not a list “at the ceiling.” The Results subsection gets this right with “whenever the dense retriever returned anything,” but the abstract, ceiling qualification, logging advice, and conclusion flatten that condition.

   Use one formulation consistently:
   > “With two retrievers, if one list is empty and the other is nonempty, the fused maximum is exactly \(1/k\). Thus, in systems where the counterpart retriever normally returns results, a ceiling cannot miss an empty input list.”

   This is a scope correction, not a numerical objection.

3. **State the rank convention before using the value \(1/k\).** The abstract and introduction present \(1/(k+r)\), but only Section 2 says ranks are zero-based. A reader accustomed to Cormack et al.’s one-based formulation will stop at “rank 0 gives exactly \(1/k\)” and wonder whether the paper changed RRF. At first occurrence, write:
   > “Using zero-based ranks \(r=0,1,\ldots\), RRF assigns \(1/(k+r)\); the usual one-based form is equivalent after shifting \(k\).”

   Then the title, abstract, and \(1/60\) incident are immediately legible.

4. **The unit “174 nonempty keyword lists” is imprecise.** In the abstract, these are **174 hybrid query runs**, not necessarily 174 distinct keyword lists: the same keyword output is reused across encoders. The body correctly says “174 of the 176 [query runs].” Make the abstract match it.

No numerical contradiction jumped out between the main claims, tables, and supplied JSON. The abstract, contribution list, logging section, and conclusion generally track the body once the two conditional claims above are repaired.

## Readability and prose

The rewrite has removed much of the prior failure mode, but several sentences still make the reader unpack a proof, qualification, and empirical aside at once.

- Ceiling section:
  > “At \(K > k\), then, a maximum of \(1/k\) shows that every retriever’s top document is exclusive to it and leaves deeper overlap open.”

  “Every retriever’s top document is exclusive” is true but not the operational conclusion a reader needs. Rewrite:
  > “At \(K>k\), a ceiling still rules out overlap involving a rank-0 document. It does not rule out overlap at deeper ranks.”

- Results, fixed-OR cost sentence:
  > “\(\textsc{bm25-or-raw}\) is 2.2 to 18 times slower (13.6 against 4.1 ms … 905 against 52 …) and worse … on five collections.”

  This contains three latency comparisons, a range, and an effectiveness claim. Put the timing pairs in a small appendix table or repository file. In prose:
  > “Removing stopwords reduced keyword-search latency on every collection; the largest reduction was on ArguAna. The raw-OR variant was also worse at nDCG@10 on five collections.”

- Sweep:
  > “Pooling the two encoders’ cells … at \(K=60\): a cap of one … a cap of three … a cap of ten … and a cap of twenty…”

  This is a verbal second table. Keep the table and state only the trend:
  > “For both encoders, disjointness fell sharply as the keyword cap increased; the complete cell values are in Table 5.”

- The sentence “**The ceiling tests for agreement, and a retriever that agrees with the other on one useless document passes it**” is clear. The later sentence “**A monitor for overlap and activity and a verdict on retrieval effectiveness are different instruments**” is not. It also retains *instrument*, which the rewrite notes say was removed. Write:
  > “Overlap/activity monitoring and relevance evaluation answer different questions.”

- The **Use of AI tools** section is the strongest remaining source of the editor’s “AI-generated” impression: it lists products and models, asserts that every reviewer defect was reproduced or refuted, and separately claims every reference was checked. Cut the vendor/model inventory and audit-process narrative. If disclosure is desired:
  > “AI tools assisted drafting and code development. The author directed the work, verified the reported results, and takes responsibility for the paper.”

## Structure and cuts

Leading with the property works. It gives an IR reader a transferable diagnostic before asking them to care about one FTS5 incident. The incident is not an afterthought because it establishes why row counts and score maxima belong together.

Section 4 is still longer than its evidentiary role requires. Keep the system, the query-builder example, the replay table, and the two-part fix. Compress the dated discovery chronology and the extended “flatness” derivation; the latter belongs as a short operational note in “What to log.”

For a 16-page arXiv version, cut, in this order:

1. **Appendix A, “Two negative results.”** It is explicitly not evidence for the ceiling and returns the paper to a personal-system notebook.
2. **The truncation sweep subsection and table.** The theorem already establishes the clean \(K\leq k\) case; the natural runs plus the two observed deep-overlap cases make the practical point.
3. **The three full-condition appendix tables**, retaining the two main effectiveness tables and linking machine-readable results.
4. Reduce the run-details appendix to reproducibility-critical configuration; put the stoplist and hardware narrative in the repository.

Keep “What to log” before Limitations. It is the paper’s operational payoff and should not be folded into the conclusion.

## Title

The present title is accurate only if “agree” is read as **top-\(K\) document overlap**, not retriever health or relevance. It also omits the crucial \(K\leq k\) condition.

- **Plain:** *Monitoring Hybrid Retrieval with Reciprocal Rank Fusion Scores*
- **Finding named:** *The \(1/k\) RRF Ceiling Signals Zero Top-\(K\) Overlap*

The second can use a subtitle to state the condition: “when \(K\leq k\).”

## Prior art

I do not know a prior paper I can confidently say explicitly observed and operationalized this exact \(1/k\) ceiling as a zero-overlap diagnostic. The closest cited foundations are appropriate:

- **Cormack, Clarke, and Büttcher (2009)** define RRF and supply the formula from which the bound follows, but do not, to my knowledge, present the ceiling as a production monitor.
- **Fox and Shaw (1994)**, especially CombMNZ, make agreement/count of contributing systems explicit, but not the RRF bound.
- **Lee (1997)** studies agreement among component systems as a condition for useful fusion.
- **Webber, Moffat, and Zobel (2010)** provide RBO for ranking overlap, not an RRF score alarm.
- **Cooper (1998)** is the right broad citation for retrieval instrumentation and monitoring, but not evidence that fused maxima or per-retriever counts were used for this particular hybrid failure mode.
- **Bruch, Gai, and Ingber (2024)** is the appropriate modern hybrid-fusion reference, but it is about effectiveness of fusion functions rather than silent inert-retriever monitoring.

I would not add a claim that this is the *first* such observation without a targeted literature search; say instead that the paper derives and evaluates the diagnostic.

## Would I post it?

I would post it after the conditional guarantee is made precise and the paper is shortened. An IR reader can now follow the main theorem, see why a full fused page masks a missing input, and understand why the ceiling is an overlap alarm rather than a health test. The single most valuable change is to replace every implication of “ceiling \(\Rightarrow\) broken retriever” with the exact operational chain: **ceiling \(\Rightarrow\) no qualifying overlap; row counts identify emptiness; system context identifies a fault.**
