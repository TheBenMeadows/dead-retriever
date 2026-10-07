#!/opt/homebrew/bin/python3
"""Probes for the round-1 council claims about Section 2. Each prints PASS
(the claim reproduces) or REFUTED with the arithmetic."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dead_retriever import RRF_K, ceiling_report, rrf_fuse  # noqa: E402

k = RRF_K

# G1 (Gemini): the observed ~1.4% "flatness" is the RELATIVE step 1/(k+r+1), not 1/k^2.
abs_step = 1 / k - 1 / (k + 1)
rel_step_top = abs_step / (1 / k)
rel_step_r10 = (1 / (k + 10) - 1 / (k + 11)) / (1 / (k + 10))
print("G1", "PASS" if abs(rel_step_top - 1 / (k + 1)) < 1e-12 and 0.013 < rel_step_r10 < 0.015 else "REFUTED",
      f"absolute step {abs_step:.6f} (~1/k^2 = {1/k**2:.6f}); relative step top {rel_step_top:.4f}, rank 10 {rel_step_r10:.4f}")

# G2 (Gemini + own check): with K > k, a document deep in both legs scores below 1/k,
# and one at rank k in both scores exactly 1/k.
deep = 1 / (k + 90) + 1 / (k + 90)
exact = 1 / (k + k) + 1 / (k + k)
print("G2", "PASS" if deep < 1 / k and abs(exact - 1 / k) < 1e-12 else "REFUTED",
      f"rank 90 in both: {deep:.6f} < 1/k={1/k:.6f}; rank {k} in both: {exact:.6f}")

# G2b: for K <= k no two-leg document can score <= 1/k (exhaustive over ranks).
viol = [(r1, r2) for r1 in range(k) for r2 in range(k) if 1 / (k + r1) + 1 / (k + r2) <= 1 / k]
print("G2b", "PASS" if not viol else "REFUTED", f"{len(viol)} two-leg rank pairs at or below 1/k with K=k")

# G6 (Gemini): both legs empty was reported as at_ceiling before the fix.
s, r = rrf_fuse({"a": [], "b": []})
rep = ceiling_report(s, r)
print("G6", "PASS (fixed)" if not rep.at_ceiling else "STILL PRESENT", f"max {rep.max_score}, at_ceiling {rep.at_ceiling}")

# G3 (Gemini): empty keyword leg => max fused score is exactly 1/k whenever dense returned >= 1 doc.
s, r = rrf_fuse({"dense": ["x"], "keyword": []})
print("G3", "PASS" if abs(max(s.values()) - 1 / k) < 1e-12 else "REFUTED", f"max {max(s.values()):.6f}")
