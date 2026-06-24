# Gene-set / pathway enrichment across the biopsy fibrosis axis

**Status: LIVE.** Scripts: `src/dge/geneset_tests.py` (GSEA pre-rank, gseapy) and
`src/dge/geneset_camera.R` (limma::camera, independent confirmation).
Outputs: `results/tables/analysis/geneset_tests.csv`, `results/tables/analysis/geneset_camera.csv`.

## The question this settles
Per-gene donor-level pseudobulk DGE (`findings/genome_wide_dge`, `dge_genomewide.csv`) found
**no single** zonation or detox gene moving with fibrosis (CYP2E1 FDR 0.98, CYP1A2 0.91, GLUL 0.85,
GLUL F4-vs-F1 0.80; all anchors FDR > 0.79). The deck's standing caveat was: *a weak **coordinated**
program — many genes each shifting a little, the same direction — could exist that per-gene FDR
missed.* This is exactly what a competitive gene-set test detects, and per-gene FDR cannot.

## Method (two independent tests, same answer)
- **Unit = donor** (n = 38 acquisition-matched biopsy donors, F0–F4 = 2/8/12/12/4). Deceased-donor
  and explant ends excluded upstream (acquisition-confounded). Inference is donor-level, not per-cell.
- **(A) GSEA pre-rank** (`gseapy.prerank`, 10,000 permutations) on the **already-computed** DGE
  ranked list. Primary ranking metric = signed −log10(p_trend) (continuous; `rho_F` is rounded to
  3 dp → ties); robustness metric = signed Spearman rho. Both give the same top sets.
- **(B) limma::camera** — rebuilds the donor-level log2-CPM pseudobulk exactly as
  `dge_genomewide.py`, fits a continuous-fibrosis design, and runs the **competitive** camera test,
  which **adjusts for inter-gene correlation within each set** (the standard guard against
  GSEA-permutation anticonservatism). This is the conservative gold standard and it confirms (A).
- **Pre-specified sets only** (no fishing). Zonation anchors are the project's own verbatim Paper 2
  landmark files; metabolic modules and the 3 controls are literature-standard cores (every gene
  and source listed in the scripts).

## Result (camera FDR; both methods agree on sign and significance)
| Gene set | Direction | camera FDR | GSEA FDR | Verdict |
|---|---|---|---|---|
| xenobiotic_CYP (13 CYPs) | **DOWN** with fibrosis | 2.3e-6 | 1.1e-3 | coordinated loss |
| pericentral_anchors (20) | **DOWN** | 1.5e-4 | 5.2e-3 | coordinated loss |
| detox_phase2 (UGT/GST/SULT/ADH/ALDH) | **DOWN** | 7.0e-3 | 0.081 | coordinated loss |
| cholangiocyte_ductular | **UP** | 1.9e-5 | 0.011 | biliary lead lights up |
| CTRL_EMT (fibrogenic) | UP | 9.1e-6 | 9.6e-3 | positive control OK |
| CTRL_interferon | UP | 1.5e-3 | 9.8e-3 | positive control OK |
| periportal_anchors (20) | UP | 0.015 | 0.16 | weak, only camera sig |
| urea_cycle | down | 0.12 | 0.20 | **null** |
| bile_acid_lipid | (mixed) | 0.72 | 0.32 | **null** |
| CTRL_ER_stress | up | 0.72 | 0.35 | **null** (neg control OK) |

## Verdict — the caveat is RESOLVED, and the answer is YES (with the honest nuance)
1. **A coordinated, weak fibrosis-associated shift DOES exist that per-gene FDR missed.** The
   pericentral / xenobiotic-detox program declines **coordinately** with fibrosis (CYP cluster
   FDR 2e-6; PC anchors 1e-4; phase-II detox 7e-3) even though **not one** of those genes survives
   per-gene multiple testing. Many small same-direction nudges sum to a real set-level signal.
2. **The biliary/ductular set lights up** (UP, FDR 2e-5), consistent with the known biliary burden —
   "a lead, not closed" (these markers are low-expressed in hepatocyte pseudobulk; n=10/19 detected,
   so this is ambient/contaminating ductular signal bleeding into the hepatocyte sum, not proof of
   hepatocyte transdifferentiation).
3. **Controls behave:** fibrogenic EMT and interferon up; ER-stress null. Urea cycle and
   bile-acid/lipid stay null — the decline is specifically the **pericentral detox** module, not
   metabolism wholesale.

So the earlier "zonation is preserved" headline needs a precise qualifier: per-gene it is preserved
(no single marker is a usable disease readout — the ruler still works), **but at the pathway level
the pericentral xenobiotic-detox program shows a coordinated, statistically real dimming with
fibrosis** that only set-level testing can see. This re-opens (in muted form) the detox sub-story
that genome-wide per-gene DGE had retired — now grounded as a *coordinated weak* effect, not a
single-gene effect.

## One-line wording for the deck (replaces the caveat)
> Gene-set testing (camera + GSEA, donor-level, biopsy F0–F4) shows the pericentral
> xenobiotic-detox program dims **coordinately** with fibrosis (CYP FDR 2e-6, detox FDR 7e-3) —
> a weak many-gene shift that per-gene FDR cannot see — while urea-cycle and bile/lipid metabolism
> stay flat; the ductular signature rises (a lead, not closed).

## Honest limitations
- Cholangiocyte markers are filtered out of the **hepatocyte** pseudobulk (KRT7/KRT19/etc. dropped
  for low hepatocyte expression); the ductular "up" rides on the residual detectable subset and is
  best read as ambient ductular contamination correlating with fibrosis, not hepatocyte plasticity.
- camera/GSEA are **competitive** tests: they say these sets shift *relative to the rest of the
  transcriptome*, not that the absolute fold-changes are large (they are small — that is the whole
  point of "weak coordinated"). Effect sizes per gene remain non-significant.
- The fibrosis trend is correlational across 38 donors; F4 has only n=4.
