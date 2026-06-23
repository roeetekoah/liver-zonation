# F5 — Cross-lineage stress, SEGMENTED by program (IEG / HSP / HIF)

**Status: LIVE.** Robust rebuild of the old cross-lineage stress table (which used deprecated
UMIs/10k donor-medians — those genes are KEPT, only the metric is upgraded). Data:
[`per_donor.csv`](per_donor.csv), [`by_lineage.csv`](by_lineage.csv). Script:
`src/confound/stress_celltype_segmented.py`. Per-gene (hepatocytes) in `../stress_and_panel_by_stage/`.

## Stress definition (precise — per project definition)
Two **acute** classes form the stress signal; HIF is kept **separate** (chronic low-O2 ≠ acute handling):
- **IEG** = FOS, JUN, JUNB, JUND, ATF3, DUSP1 (immediate-early; the dissociation/handling artifact).
- **HSP** = HSPA1A, HSPA1B (heat-shock / proteotoxic-ischemic).
- **HIF** (separate) = VEGFA, SLC2A1, LDHA, CA9, ENO1, PGK1, HSP90AA1 (hypoxia).

**Metric:** mean **down-thinned to B=1,500 UMIs/cell** = binomial down-thinning of each cell's module-sum to budget
**B=1500** (cells below B dropped), Monte-Carlo averaged over **4 draws**; also det2 = frac with raw
module-sum ≥ 2 (ambient-robust). Unit = donor (mean across donors below).

## Result — down-thinned to B=1,500 mean UMIs/cell, explant/biopsy fold
| cell type | IEG bx | IEG hl | IEG ex | **IEG ex/bx** | HSP ex/bx | HIF ex/bx |
|---|---|---|---|---|---|---|
| Hepatocytes | 0.068 | 0.161 | 1.249 | **18.5×** | 65.7× | 1.7× |
| **Endothelial** | 0.052 | 0.205 | 0.941 | **18.2×** | 45.7× | 2.6× |
| Stellate | 0.062 | 0.176 | 0.738 | 12.0× | 14.8× | 2.6× |
| Macrophages | 0.124 | 0.163 | 0.656 | 5.3× | 25.8× | 1.9× |
| Cholangiocytes | 0.084 | 0.250 | 0.890 | 10.6× | 3.2× | 0.8× |
| Lymphocytes | 0.145 | 0.108 | 0.470 | 3.2× | 9.5× | 1.6× |

## Findings
- **IEG (acute handling) is the dominant signal and is organ-wide:** explant hepatocytes 18.5× ≈
  **endothelial 18.2×** — and endothelium has no hepatocyte zonation. A signal equal in a non-zonated
  lineage = whole-organ procurement/handling, not a hepatocyte program.
- **HIF (hypoxia) is weak everywhere (1.7–2.6×)** → the end-stage signal is **acute handling, not chronic
  hypoxia**. This is exactly why HIF is held out of the stress module.
- **HSP** is also elevated in *healthy* non-parenchymal cells (endothelial 0.356, stellate 0.382) — the
  deceased-donor healthy procurement induces heat-shock too; reinforces that the "healthy" baseline is not
  clean.

## Caveats
- Per-gene segmentation within non-hepatocyte lineages is not yet broken out (program-level here; per-gene
  hepatocyte breakdown in `../stress_and_panel_by_stage/stress_per_donor_alllobe.csv`). Extendable.
- Source split (biopsy / healthy / explant) collinear with disease stage — descriptive of acquisition.
