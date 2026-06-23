# F14 — Per-donor end-stage anchor scrutiny: the 5 explants are 5 different phenotypes

**Status: LIVE — this is the load-bearing evidence that end-stage is NOT one coherent program.** Data:
`results/tables/analysis/load_bearing_donor_table.csv` (per-donor) + `review_checks.py` (section C). Scales:
fractions of down-thinned-to-B=1,500 hepatocyte nuclei; dual at **≥2 UMI** (ambient-robust); PP:PC = PP_n/PC_n.

## The five end-stage explants, one row each
| explant | nuclei | PC-anchor% | PP-anchor% | dual(≥2)% | null% | PP:PC | phenotype |
|---|---|---|---|---|---|---|---|
| **CL104** | 1,908 | **49.7** | 6.7 | 1.1 | 17.7 | **0.13** | *retains* pericentral — MORE than the average biopsy donor (~24%) |
| CL18 | 8,285 | 20.5 | 18.7 | **22.4** | 5.3 | 0.92 | **co-expression explosion** (22% real dual) |
| CL103 | 1,960 | 14.2 | 41.7 | 2.7 | 25.5 | 2.93 | periportal-leaning |
| CL17 | 4,111 | 9.1 | 50.5 | 5.9 | 16.7 | 5.55 | periportal-leaning + elevated dual |
| **CL16** | 5,955 | **3.2** | 65.2 | 2.4 | 18.0 | **20.3** | **near-total pericentral collapse** (PP:PC ≈ 20) |

## What it shows
- The five separately-procured organs go in **opposite directions**: one keeps its pericentral pole
  (CL104), one collapses to periportal (CL16), one floods into co-expression (CL18). Per-donor PC-anchor
  ranges **3%→50%**, PP:PC ranges **0.13→20**.
- This is the signature of **heterogeneous, separately-handled organ procurement**, NOT a single coherent
  end-stage disease program. A pooled marker-correlation (Paper 1's approach) collapses these five
  discordant organs into one number and reports a uniform "collapse."
- **This is the caveat on the group-mean "end-stage selective shape" (F2/F3 / Item 4):** the group average
  (detox-down + PP-induced + PC-retained) is a mean over these five discordant donors — do not read it as a
  single mechanism.

## Why end-stage is excluded, restated
Combined with the organ-wide stress (F2/F5, 5–21× across all lineages incl. non-zonated endothelium) and
the perfect stage⟂tissue-source collinearity, the explant signal is **unattributable to disease** and is
treated only as a heterogeneous contrast — not a disease endpoint, not a clean positive control.
