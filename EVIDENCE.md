# LiZARD evidence map

This page is the current public claim-to-evidence index. Historical investigation notes remain in `FINDINGS.md` and `CLAIMS_LEDGER.md`, but they do not override the scoped statements below.

## Cohorts

| Analysis | Donors | Comparison and input |
|---|---:|---|
| Study inventory | 47 | 4 healthy, 38 biopsy, 5 explant; 99,809 nuclei in the saved metadata |
| Matched biopsy measurements | 38 | F0/F1/F2/F3/F4 = 2/8/12/12/4; raw RNA panel; eight deterministic 1,500-UMI thinning draws |
| F1–F4 endpoint comparison | 12 | 8 F1 versus 4 F4 biopsy donors |
| Gene-set trend | 38 | Continuous F0–F4 trend on donor pseudobulk, raw RNA counts with CPM/TMM checks |
| Within-PC detox measure | 37 eligible | At least 20 PC-like nuclei per donor; five-gene burden after depth matching |

## Claims and boundaries

| Public statement | Current evidence | Source | Boundary |
|---|---|---|---|
| No clear progressive collapse in the selected matched-biopsy transcriptional measurements | PC/PP/strict-dual/null measurements are flat or non-monotone. F1→F4 PC fraction: +0.0345, 90% CI [−0.1363, +0.2054] | [`load_bearing_donor_table.csv`](results/tables/analysis/load_bearing_donor_table.csv), [`equivalence_bound.csv`](results/tables/analysis/equivalence_bound.csv), `src/census/load_bearing.py` | ±0.05 and ±0.10 equivalence are not established. These measurements do not observe spatial architecture |
| The mixed-threshold columns are separate metrics | Weak-dual remainder: 3,790.6 of 40,303 retained biopsy nuclei across eight draws (9.41%) | [`load_bearing_donor_table.csv`](results/tables/analysis/load_bearing_donor_table.csv), `src/census/load_bearing.py` | Do not describe PC/PP/strict-dual/null as an exhaustive four-way partition |
| A CYP detoxification program declines relatively with fibrosis | CAMERA: 13 genes, Down, FDR 2.32×10⁻⁶. mROAST: Down, FDR 0.0152 | [`geneset_camera.csv`](results/tables/analysis/geneset_camera.csv), [`geneset_verify_roast.csv`](results/tables/analysis/geneset_verify_roast.csv), `src/dge/geneset_camera.R`, `src/dge/geneset_verify.R` | Competitive and self-contained tests answer different questions; neither measures enzyme activity or absolute molecules |
| A related within-PC burden also declines | Five-gene measure: F1 11.861 → F4 9.015; difference −2.846, 95% CI [−4.383, −1.309], Welch p=0.0022; stage trend ρ=−0.461, p=0.0041 | [`geneset_verify_within_pc_detox.csv`](results/tables/analysis/geneset_verify_within_pc_detox.csv), `src/dge/geneset_verify_test4.py` | This five-gene measure overlaps the 13-gene CYP set in only two genes; it is corroborating, not an identical replication |
| No individual zonation marker is significant in Plan A | GLUL FDR 0.803; CYP3A4 FDR 0.851; 64 genes pass FDR overall, dominated by biliary/ductular signals | [`dge_planA_F4vsF1.csv`](results/tables/analysis/dge_planA_F4vsF1.csv), `src/dge/plan_a_genomewide.R` | Lack of per-gene significance is not proof of no coordinated program change |
| The biliary rise is an open source-attribution lead | decontX reduces the per-gene hit count and changes which biliary genes remain; the cohort also shows a ductular increase | [`dge_planA_decontx_F4vsF1.csv`](results/tables/analysis/dge_planA_decontx_F4vsF1.csv), `src/dge/decontX_replan_a.R` | decontX was applied to per-gene Plan A, not to the CYP gene-set trend. Do not claim that the detox set “survives decontX” |
| Endpoint disease and acquisition effects cannot be separated in this cohort | Healthy and end-stage groups are organ tissue; F0–F4 disease series is needle biopsy; run/source association is strong | [`batch_qc.csv`](results/tables/analysis/batch_qc.csv), `src/confound/batch_qc.py` | Cross-lineage stress is compatible with a handling effect but does not identify a single causal mechanism |

## Verification state

The bounded route was rerun twice in fresh output directories on 22 September 2026. All result tables were byte-identical across repeats after deterministic eight-draw thinning was introduced; the only intentional schema change between development runs was renaming the descriptive CI endpoint fields in the equivalence table. Raw-count checks passed 9/9, including 69,426 hepatocytes and explicit RNA-versus-SCT separation.

The current verified route does not rerun decontX, which is a much heavier optional analysis. Its saved per-gene output is retained and scoped as an exploratory source-attribution check.
