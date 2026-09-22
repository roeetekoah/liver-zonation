# F7 — The integrated donor-level PC-anchor classification (scales documented)

**Status: LIVE.** The "most-information-per-analysis" table: one donor-level row folds depletion,
co-expression, turn-off, and stress-coupling, separating biopsy vs explant. Data:
`results/tables/analysis/load_bearing_donor_table.csv`. Script: `src/census/load_bearing.py`.

## What every column is, and its scale
Down-thinned to B=1,500: each nucleus down-thinned (binomial) to budget **B=1500**; cells below B dropped;
`N_thin` = down-thinned to B=1,500 nuclei kept for that donor. Counts are **out of N_thin**; fractions = count/N_thin.
| column | definition | scale |
|---|---|---|
| `PC_n` | nuclei that are **pericentral-anchor** = detect GLUL and/or CYP3A4 (≥1 UMI) and <2 PP markers | count / N_thin |
| `PP_n` | **periportal-anchor** = ≥2 of {ASS1,PCK1,HAL,ALDOB} (≥1 UMI) and no PC marker | count / N_thin |
| `dual2_n` | **strict co-expression**, ambient-robust = PC marker ≥2 UMI AND ≥2 PP markers ≥2 UMI | eight-draw mean count / N_thin |
| `weak_dual_n` | meets the permissive PC and PP gates but not the strict dual gate | eight-draw mean count / N_thin |
| `null_n` | neither pole detected | count / N_thin |
| `stress_p10k` | stress UMIs per 10⁴ (IEG+HSP) | **UMIs/10k — DEPRECATED metric**, indicator only |
| `F`, `NAS`, `source`, `lobes` | fibrosis 0–4, NAS 0–8, biopsy/explant/healthy, lobe(s) | — |

## Per-stage summary (biopsy, donor-median fractions; from the CSV)
| stage | nD | PC-anchor% | PP-anchor% | strict dual% | weak dual% | null% |
|---|---|---|---|---|---|
| F0 | 2 | 33.86 | 19.33 | 0.20 | 10.51 | 36.10 |
| F1 | 8 | 18.24 | 19.58 | 0.18 | 6.87 | 44.44 |
| F2 | 12 | 23.70 | 22.27 | 0.36 | 10.00 | 35.70 |
| F3 | 12 | 19.20 | 23.89 | 0.31 | 7.61 | 39.51 |
| F4 | 4 | 23.15 | 23.12 | 0.34 | 8.99 | 40.17 |

Biopsy fractions flat/non-monotone; explants heterogeneous and high-stress (see F2/F3 + Item 4 caveat).

## Provenance / what is NOT this table
- An earlier **partition** anchor-classification (`census.py`/`census_v2.py`) produced a PC/PP/dual/null 4-way partition
  plus a **"detox within PC" relative/normalized column (DEPRECATED relative metric)** — different numbers,
  superseded by this count-based version. The relative detox column is not used.
- This table uses ≥1-UMI detection for the PC/PP anchors and ambient-robust ≥2 for `dual2`.
  These columns are separate metrics, not an exhaustive partition. The explicit `weak_dual_n`
  remainder prevents downstream code or prose from silently assigning those nuclei to `null`.
- Counts are means over eight deterministic thinning draws. `N_thin` is the number of eligible
  nuclei and is constant across draws.
