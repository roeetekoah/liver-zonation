# Equivalence bound — the affirmative companion to the zonation-preservation null (O12 / D3)

**Status: LIVE.** Reproducible: `src/confound/equivalence_bound.py` →
`results/tables/analysis/equivalence_bound.csv`. Reuses the existing donor-level metrics in
`results/tables/analysis/load_bearing_donor_table.csv` (no re-classification, no DGE).

## The question
Decision D3 ("hepatocyte gene-expression zonation signal is preserved across biopsy MASLD
F1→cirrhotic F4") rests on a **descriptive null** — across the scenario taxonomy (F9) and the
sensitivity-grid anchor-classification (F8), nothing moved. But "nothing was significant" is
*absence-of-evidence*, not *evidence-of-absence*. A referee wants the affirmative form: not
"we failed to detect a shift" but **"we can EXCLUDE a coordinated zonation shift larger than X."**
This finding supplies that bound via TOST / equivalence testing.

## The data and metrics (what is being bounded)
Donor-level **anchor-classification / donor-proportion (compositional) metrics**, biopsy donors
only, already depth-controlled by binomial down-thinning to B=1500 (per `load_bearing.py`):
- **PC-anchor fraction** = PC_n / N_thin  (proportion in [0,1])
- **PP-anchor fraction** = PP_n / N_thin  (proportion in [0,1])
- **PP:PC ratio** = PP_n / PC_n  (dimensionless composition ratio)

The unit is the **donor** (n donors per stage, not cells) — this is the donor-level structure
metric, not a per-gene or per-cell quantity.

## Method
Two contrasts, diff = mean(high F) − mean(low F):
- **F1 vs F4** — n=8 vs n=4 — the headline fibrosis→cirrhotic-biopsy contrast.
- **F1 vs F3** — n=8 vs n=12 — the better-powered interior contrast (F4 is thin).

For each (contrast, metric):
1. observed group difference;
2. **90% confidence interval** — Welch two-sample t (unequal variance), with a **percentile
   bootstrap 90% CI** (20,000 resamples, seed 0) as a small-n robustness check;
3. **TOST / equivalence** against pre-specified margins. Operationally, a margin is
   **affirmatively EXCLUDED** iff the entire 90% CI lies within ±margin (this is the standard
   90%-CI ⇔ TOST-at-α=0.05-per-side equivalence; a coordinated shift bigger than that margin
   is rejected at α=0.05).

### Margins (pre-specified, and why)
- **±0.05 absolute** in an anchor fraction — a half-of-one-tenth shift in the pericentral (or
  periportal) compartment; biologically a *subtle* compositional change.
- **±0.10 absolute** — a one-in-ten shift in compartment proportion; a *modest, visible*
  re-zonation. (For reference, the F0→F4 PC-anchor spread across stages is only 36/19/23/22/21%,
  so ±0.10 is already on the order of the entire observed cross-stage range.)
- **±20% relative** to the F1 baseline mean — a scale-free version, and the **only** sensible
  margin for the unbounded PP:PC ratio (±20% of the F1 mean 1.197 ≈ ±0.239).

Margins are a deliberate **judgment call**; all three are reported so the reader can apply their
own threshold. The headline is the *tightest* margin the data exclude (the binding CI endpoint).

## Results (every number, with scale)

Anchor fractions are proportions in [0,1]; PP:PC is a ratio.

**F1 (n=8) vs F4 (n=4):**

| metric | mean F1 | mean F4 | Diff | 90% t-CI | 90% boot-CI | tightest excluded |
|---|---|---|---|---|---|---|
| PC-anchor fraction | 0.248 | 0.272 | **+0.024** | [−0.147, +0.194] | [−0.093, +0.153] | ±0.194 (t) / ±0.153 (boot) |
| PP-anchor fraction | 0.239 | 0.221 | **−0.019** | [−0.151, +0.114] | [−0.119, +0.076] | ±0.151 (t) / ±0.119 (boot) |
| PP:PC ratio | 1.197 | 1.070 | **−0.127** | [−0.974, +0.720] | [−0.799, +0.502] | ±0.974 (t) / ±0.799 (boot) |

**F1 (n=8) vs F3 (n=12) — better powered:**

| metric | mean F1 | mean F3 | Diff | 90% t-CI | 90% boot-CI | tightest excluded |
|---|---|---|---|---|---|---|
| PC-anchor fraction | 0.248 | 0.210 | **−0.038** | [−0.119, +0.043] | [−0.111, +0.029] | ±0.119 (t) / ±0.111 (boot) |
| PP-anchor fraction | 0.239 | 0.291 | **+0.052** | [−0.033, +0.137] | [−0.025, +0.128] | ±0.137 (t) / ±0.128 (boot) |
| PP:PC ratio | 1.197 | 1.666 | **+0.469** | [−0.281, +1.219] | [−0.188, +1.161] | ±1.219 (t) / ±1.161 (boot) |

Against the fixed pre-specified margins: **±0.05 and ±0.10 are NOT excluded** for any
metric/contrast (the donor-to-donor fraction spread — e.g. PC-anchor SD ≈ 0.11–0.15 — makes the
90% CIs wider than ±0.10). The bound the data *do* support is the continuous one (the binding CI
endpoint), reported in the last column.

## Affirmative conclusion (the headline)
Stated affirmatively, in the form a referee asked for:

- **F1→cirrhotic-F4 biopsy, PC-anchor fraction:** Δ = **+0.024** (90% CI −0.147 to +0.194) — we
  can exclude any coordinated pericentral shift **larger than ≈ ±0.19** (≈ ±0.15 by bootstrap).
- **F1→cirrhotic-F4 biopsy, PP-anchor fraction:** Δ = **−0.019** (90% CI −0.151 to +0.114) — we
  exclude any coordinated periportal shift **larger than ≈ ±0.15** (≈ ±0.12 bootstrap).
- **F1→F3 interior (better powered), PC-anchor fraction:** Δ = **−0.038** (90% CI −0.119 to
  +0.043) — we exclude a pericentral shift **larger than ≈ ±0.12** (≈ ±0.11 bootstrap).
- **F1→F3 interior, PP-anchor fraction:** Δ = **+0.052** (90% CI −0.033 to +0.137) — we exclude
  a periportal shift **larger than ≈ ±0.14** (≈ ±0.13 bootstrap).

In words: across biopsy MASLD progression — *including into established cirrhotic-F4 biopsy
tissue* — a **large** coordinated re-zonation (≳ ±0.15–0.19 of the compartment, i.e. roughly a
collapse on the scale of the confounded explants) is **affirmatively ruled out**; the better-
powered interior tightens this to ≈ ±0.12. The estimates themselves are small and centered near
zero, consistent with preservation. This converts the D3 null from "nothing was significant"
into a quantified exclusion bound.

## HONEST caveats (what a statistician would raise)
- **Small n, especially F4 (n=4).** The F1-vs-F4 CIs are wide and Welch df is small (≈5–7); the
  bound there is loose (±0.15–0.19). The F1-vs-F3 contrast (8 vs 12) is the more trustworthy
  bound (≈ ±0.12) — and it tests the well-populated interior, not the thin extreme.
- **We do NOT exclude small shifts.** ±0.05 and ±0.10 are NOT ruled out. The donor-level fraction
  variance (PC-anchor SD ≈ 0.11–0.15) is large relative to those margins, so the data are
  consistent with a *modest* (≤±0.10) compositional drift. The affirmative claim is only against
  a *large/coordinated* shift; do not overstate it as excluding any change.
- **The margin is a judgment call.** ±0.05 / ±0.10 / ±20% are defensible but not derived from an
  external clinical threshold; all three are reported so the reader can substitute their own.
- **This is the donor-level STRUCTURE metric (PC/PP anchor proportions / composition), not
  per-gene expression.** It bounds compositional re-zonation (depletion / turn-off / composition
  shift in the taxonomy F9). It is the **affirmative companion to the descriptive null** and
  **supports D3**; by itself it does **not** prove per-gene transcriptional preservation — that
  case rests on the converging positives (F8 sensitivity-grid anchor-classification, F1 all-sets invariance,
  genome-wide FDR>0.79, retained GLUL/CYP3A4, the F9 gradient figure).
- **t-based CIs assume approximate normality of donor fractions** at small n; the percentile
  bootstrap is reported alongside as the assumption-light check and agrees (it is, if anything,
  slightly tighter), so the conclusion is not an artifact of the normal-t approximation.
- **Architecture caveat (inherited from D3) still stands:** snRNA on needle cores measures
  per-cell transcriptional/compositional balance, not lobule geometry. This bound is about the
  gene-expression / compositional signal, not spatial-architectural preservation.
