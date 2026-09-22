# Precision and fixed-margin equivalence checks

**Status: current.** Script: `src/confound/equivalence_bound.py`. Output: `results/tables/analysis/equivalence_bound.csv`.

## Question

How precisely do the donor-level PC/PP anchor measurements estimate the difference between biopsy fibrosis stages, and do the data establish equivalence within the pre-specified ±5 or ±10 percentage-point margins?

The inputs are the deterministic eight-draw means in `load_bearing_donor_table.csv`. The unit is the donor. The comparisons are F1 versus F4 (8 versus 4 donors) and F1 versus F3 (8 versus 12 donors).

## Results

| Contrast and metric | Estimate | 90% Welch CI | ±5 pp | ±10 pp |
|---|---:|---:|---:|---:|
| F1→F4 PC fraction | +0.0345 | [−0.1363, +0.2054] | not established | not established |
| F1→F4 PP fraction | −0.0239 | [−0.1279, +0.0800] | not established | not established |
| F1→F3 PC fraction | −0.0505 | [−0.1334, +0.0324] | not established | not established |
| F1→F3 PP fraction | +0.0503 | [−0.0370, +0.1376] | not established | not established |

Bootstrap intervals are included in the CSV and lead to the same decision about the fixed margins.

## Interpretation

The point estimates are small relative to the hypothesized collapse and the stage pattern is non-monotone, but the confidence intervals remain wide. These tests **do not establish equivalence** within ±5 or ±10 percentage points. Report the estimate and interval directly; do not turn the largest absolute CI endpoint into a retrospectively chosen equivalence margin.

The metrics are transcriptional detection proportions under the project’s anchor definitions. They do not measure lobular geometry, and they do not prove that every aspect of zonation is unchanged.
