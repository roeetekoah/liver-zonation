# Primer compliance — specified vs implemented

Maps every method the `docs/` primers specify to where it lives in the code (or flags it as
missing/optional). Sources: `docs/Zonation_Primer.pdf`, `docs/primers/Primer_H1_H3_Statistical_Tests.pdf`,
`docs/primers/Primer_DE_and_FDR.pdf`.

## H1 — ordered-trend (donor-level)
| spec | status | where |
|---|---|---|
| Spearman ρ vs stage rank | ✅ | `steps/step6_collapse.py` → `collapse_trends.csv` `rho_vs_stage`,`p_spearman` |
| **Jonckheere–Terpstra** (dedicated ordered test) | ✅ (added) | `steps/common.py:jonckheere_terpstra` → `collapse_trends.csv` `jt_z`,`jt_perm_p` |
| Donor bootstrap CI | ✅ | `step6_collapse.py` → `ci_lo`,`ci_hi` |
| Label-shuffle permutation null | ✅ | `step6_collapse.py` → `perm_p` |

## H2 — which programs lose zonal restriction (donor-level)
| spec | status | where |
|---|---|---|
| Pseudobulk donor×zone DE + BH-FDR | ✅ | `steps/step7_de.py:de` → `de_portal.csv`,`de_central.csv` |
| Held-out gene split K≈20–50 (anti-circularity) | ✅ | `step7_de.py:h2_slope_loss` (K=20) |
| Program-level differential vulnerability (H2b) | ✅ | `h2_program_analysis.py` → `h2_program_summary.csv` |
| Transcriptome-wide per-gene slope-loss (H2c) | ✅ | `h2_transcriptome_wide.py` |
| Slope-loss × classic-DE cross | ✅ | `h2_slopeloss_vs_DE.csv` |
| **Explicit coord×stage interaction OLS** (`expr~coord+stage+coord:stage`) | ⚠️ proxy only | per-donor slope trend is the donor-level analogue; the exact per-gene interaction model is NOT yet fit |

## H3 — de-zonation ↔ plasticity (donor-level)
| spec | status | where |
|---|---|---|
| Within-donor correlation, aggregate | ✅ | `steps/step8_plasticity.py` → `per_donor_plasticity.csv` |
| Sign test on per-donor ρ | ✅ | `step8` → `h3_summary.csv` `sign_test_p` |
| **Wilcoxon signed-rank** on per-donor ρ | ✅ (added) | `step8` → `h3_summary.csv` `wilcoxon_signed_rank_p` |
| **Mann–Whitney U + AUC / rank-biserial** | ✅ (added, donor-level) | `step8` within-donor de-zonated-vs-zonated AUC → `auc_dez_plast`, `mean_auc_dez_plast` |
| OLS `plast~dez+C(stage)+C(donor)` | ✅ (labeled descriptive) | `step8` (cell-level SE; not a headline p) |

## Cross-cutting (every test)
| spec | status |
|---|---|
| Donor is the unit of inference | ✅ everywhere (per-donor aggregation, donor resampling) |
| BH-FDR across many tests | ✅ `steps/common.py:bh` |
| Effect sizes beside p (ρ, AUC/rank-biserial, β) | ✅ |
| q-values | ✅ (BH q in H2 tables) |
| Score computed BOTH ways (full + landmark) + agreement | ✅ (full battery of rulers) |

## Other primer steps
| spec | status |
|---|---|
| Step 1 ruler / Step 2 load-QC / Step 3 harmonize | ✅ |
| Step 4 score / Step 4b calibrated classifier + entropy + held-out confusion | ✅ |
| Step 5 healthy validation gate / Step 5b ruler diagnostics | ✅ |
| **Step 9 bonus — Paper 3 inherited-risk hypergeometric enrichment** | ❌ optional; needs Paper 3 risk-gene data (not local) |

## Remaining (honest list)
1. **H2 explicit interaction OLS** (`expr~coord+stage+coord:stage` per gene) — currently a per-donor-slope proxy; the exact model can be added.
2. **Step 9 bonus** (Paper 3 enrichment) — optional; needs the risk-gene supplementary.
3. JT / Wilcoxon / MWU are added in code; a full `run_everything.py` pass propagates them to every set's tables and into the reports.

## Honest H3 note
With JT+Wilcoxon added, H3 is **statistically detectable but biologically marginal and
ruler-dependent**: marker rulers (landmark/expanded) give Wilcoxon p≈1e-4 yet a tiny effect
(AUC≈0.505, mean ρ≈0.025); the unsupervised axis gives null (AUC≈0.496). H1 and H2 are the robust results.
