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
| `dual2_n` | **co-expression**, ambient-robust = PC marker ≥2 UMI AND ≥2 PP markers ≥2 UMI | count / N_thin |
| `null_n` | neither pole detected | count / N_thin |
| `stress_p10k` | stress UMIs per 10⁴ (IEG+HSP) | **UMIs/10k — DEPRECATED metric**, indicator only |
| `F`, `NAS`, `source`, `lobes` | fibrosis 0–4, NAS 0–8, biopsy/explant/healthy, lobe(s) | — |

## Per-stage summary (biopsy, donor-median fractions; from the CSV)
| stage | nD | PC-anchor% | dual2% | null% | stress/10⁴ |
|---|---|---|---|---|---|
| F0 | 2 | 36 | 0.05 | 34 | 0.3 |
| F1 | 8 | 19 | 0.23 | 44 | 0.4 |
| F2 | 12 | 23 | 0.45 | 36 | 0.5 |
| F3 | 12 | 22 | 0.21 | 39 | 0.4 |
| F4 | 4 | 21 | 0.24 | 39 | 0.5 |
| explant | 5 | (heterogeneous 3–50) | (1–22) | (5–26) | 6–20 |

Biopsy fractions flat/non-monotone; explants heterogeneous and high-stress (see F2/F3 + Item 4 caveat).

## Provenance / what is NOT this table
- An earlier **partition** anchor-classification (`census.py`/`census_v2.py`) produced a PC/PP/dual/null 4-way partition
  plus a **"detox within PC" relative/normalized column (DEPRECATED relative metric)** — different numbers,
  superseded by this count-based version. The relative detox column is not used.
- This table uses ≥1-UMI detection for the PC/PP anchors and ambient-robust ≥2 for `dual2`. A fully
  ambient-robust re-derivation of all classes is optional (queue if wanted).
