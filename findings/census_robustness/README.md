# F8 — The structural anchor-classification is robust across the whole sensitivity grid (screenshot 1)

**Status: LIVE — this is the positive case FOR "zonation preserved."** The flat anchor-classification is not one fragile
cut; it holds across every anchor definition and threshold. Reproducible via `census.py` / `census_v2.py`
and `review_checks.py` (k=1 vs k=2 dual).

## The three structural endpoints, across the sensitivity grid (biopsy F0→F4)
- **PC-anchor fraction — flat / non-monotone in EVERY variant** → no pericentral depletion.
  Variants that all agree: GLUL-only / CYP3A4-only / both; k ∈ {1,2}; periportal 2-of-4 / 3-of-4;
  ALDOB in/out; CPS1-based; strict-identity.
- **dual (co-expression) — the key ambient-robustness result:** at **k=1 UMI** biopsy dual ≈ 0.07–0.10
  (looks like ~10% "co-expression"), but at **k≥2 (ambient-robust)** it **collapses to ≈ 0.002–0.006** at
  every fibrosis stage (`review_checks.py`). **The apparent co-expression at 1 UMI was ambient soup**, not
  real co-expression — exactly as the biology agent warned. Real co-expression is ~0 and does not rise →
  **no de-zonation by co-expression.** (Explant dual at k≥2 ≈ 0.029, ~7× higher — the confounded group.)
- **null fraction — flat** → no identity turn-off.

## Why this matters (framing)
This is the **positive evidence** that supports "zonation structure is preserved across biopsy F0–F4":
the negative is solid because it survives the entire grid, not because of any single threshold or a power
calculation. The MDE only bounds *near-total* collapse; the preservation case stands on this robustness +
all-sets invariance (F1) + genome-wide flatness + retained GLUL/CYP3A4 identity.

## Scales
PC-anchor / dual / null = fractions of down-thinned to B=1,500 hepatocyte nuclei (binomial thinning to B=1500).
k = per-gene UMI threshold for "detected" (k=2 = ambient-robust).
