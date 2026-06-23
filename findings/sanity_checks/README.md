# F11 — Raw-extraction sanity checks (each an explicit falsifiable assertion)

**Status: LIVE — 9/9 PASS.** Reproducible: `python src/prep/06_sanity_raw.py` (committed). These verify the
extracted panel really is the **raw RNA-assay UMI counts** (not the SCT-corrected matrix). Authoritative
cross-check: the R object-schema dump `src/prep/07_dump_object_schema.R`.

| # | check (assertion) | why it matters | result |
|---|---|---|---|
| 1 | panel values are non-negative **integers** | SCT `data`/`scale.data` are fractional; raw UMIs are integers | PASS (min 0, max 1602) |
| 2 | `E_raw` == metadata `nCount_RNA` **exactly** | confirms E_raw is the authors' raw RNA library size | PASS |
| 3 | library spans **920–49,854** (raw range), not the SCT ~3–5.7k band | SCT counts are depth-squeezed; raw are not | PASS |
| 4 | panel counts **DIFFER** from `counts.npz` (the SCT matrix) | proves we pulled RNA, not SCT | PASS (565/800 cell,gene differ; RNA median 5,491 vs SCT 4,706) |
| 5 | **ALB** is a top-burden hepatocyte gene | biological sanity (albumin dominates hepatocytes) | PASS (ALB 43/10k, top) |
| 6 | per-cell panel sum ≤ `E_raw` | the panel is a subset of the transcriptome | PASS |
| 7 | hepatocyte nuclei == paper's **69,426** | matches Paper 1's reported count | PASS |
| 8 | detection plausible (ALB high, GLUL/LGR5 sparse) | not all-or-nothing; biologically sensible | PASS (ALB 0.99, CYP2E1 0.77, GLUL 0.24, LGR5 0.06) |
| 9 | all analysis-critical genes present (no silent drop) | guards against an extraction gap | PASS (RPLP0 legitimately absent — ribosomal, removed at Paper-1 QC) |

## Conclusion
All 9 pass → the extracted panel is the **raw RNA-assay UMI counts**, integer-verified, donor/stage/lobe
metadata intact, matching Paper 1's hepatocyte count. This is the audited foundation every downstream
finding rests on (the SCT matrix was abandoned for molecule-level inference; see schema dump, prep/07).
