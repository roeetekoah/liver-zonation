<div align="center">

# Liver zonation re-analysis in MASLD

**A donor-level, raw-count re-test of the single-nucleus RNA-seq evidence for hepatocyte de-zonation and transdifferentiation in metabolic-dysfunction–associated steatotic liver disease (MASLD).**

Re-examining Gribben et al., *Nature* 2024 — "Acquisition of epithelial plasticity in human chronic liver disease" (GEO: GSE202379).

[![R](https://img.shields.io/badge/R-Seurat%20%7C%20edgeR%20%7C%20limma-276DC3?logo=r&logoColor=white)](https://www.r-project.org/)
[![Python](https://img.shields.io/badge/Python-numpy%20%7C%20scipy%20%7C%20statsmodels-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Data: GSE202379](https://img.shields.io/badge/data-GSE202379-8A2BE2?logo=databricks&logoColor=white)](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE202379)
[![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-green.svg)](LICENSE)

</div>

---

## Abstract

This repository re-examines the single-nucleus RNA-seq (snRNA-seq) evidence in Gribben et al. (*Nature* 2024; GSE202379) for **progressive hepatocyte de-zonation** and hepatocyte→cholangiocyte **transdifferentiation** in human MASLD. Two features of the original analysis motivate a re-test: the zonation signal was summarised with a *relative*, scale-free statistic (a z-scored zonation coordinate and marker–marker correlations, pooled across samples), and disease stage is collinear with how each sample was procured — the healthy and end-stage groups are deceased-donor organ tissue, whereas the F0–F4 fibrosis spectrum are 16-gauge needle biopsies.

Restricting the disease axis to the acquisition-matched needle biopsies (F1 → cirrhotic F4) and working on raw UMI counts with the **donor** as the unit of inference, we find **no transcriptional de-zonation signal**: the pericentral and periportal classification fractions, dual co-expression, and the double-negative fraction are flat across fibrosis, and an equivalence test (TOST) excludes a large coordinated shift (> ±19 percentage points) while leaving a subtle (≤ 10 pp) drift unexcluded. A genome-wide per-gene pseudobulk scan finds no zonation gene moving (`GLUL` FDR 0.80).

The one robust biopsy-internal change is a **coordinated decline of the pericentral cytochrome-P450 detoxification program**. It is the only gene set significant in *both* a competitive and a self-contained test (camera FDR 2×10⁻⁶; roast FDR 0.015), survives composition-robust (TMM) normalization and ambient-RNA removal (decontX), and is reproduced by a per-cell, depth-matched measure (within-pericentral detox output 11.9 → 8.8 UMIs/nucleus, F1 → F4; Spearman ρ = −0.48, p = 0.003). No single gene clears per-gene FDR, and the cells retain their pericentral **class**, so this is **functional dimming of a program, not de-zonation**. The only per-gene genome-wide signal is a small biliary/ductular-marker rise at cirrhosis, most consistent with compositional contamination (ambient cholangiocyte RNA and the ductular reaction) rather than widespread transdifferentiation — a lead, not a closed result.

We re-examine **only** the snRNA-seq transcriptional evidence; the paper's imaging, protein, and organoid findings are not addressed.

---

## Background

Hepatocytes are transcriptionally **zonated** along the porto-central axis: cells near the central vein run a *pericentral* program (e.g. `GLUL`, `CYP3A4`, the cytochrome-P450 / xenobiotic-detox genes), while cells near the portal tract run a *periportal* program (e.g. `ASS1`, `CPS1`, `PCK1`, the urea cycle). Gribben et al. (2024) reported that across MASLD hepatocytes progressively lose this zonation and acquire a cholangiocyte-like identity through transdifferentiation, "prominent in end-stage."

This project asks two questions of the deposited snRNA-seq data: **(i)** does hepatocyte zonation degrade across MASLD fibrosis once the analysis is made robust to the metric and to sample procurement, and **(ii)** is any change linked to the reported hepatocyte→cholangiocyte transdifferentiation?

---

## Data

| | |
|---|---|
| **Source** | Gribben et al., *Nature* **630**:166–173 (2024) — GEO accession [GSE202379](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE202379) |
| **Scale** | ~99,809 QC-passing nuclei · 69,426 hepatocytes · 47 donors |
| **Disease cohort analysed** | Acquisition-matched needle biopsies, fibrosis F1 → cirrhotic F4 (38 donors; F0/F1/F2/F3/F4 = 2/8/12/12/4). Healthy and end-stage groups are deceased-donor organ cubes / explants and are excluded from the disease axis as acquisition-confounded. |
| **Unit of inference** | The **donor**, never the cell |

Raw and processed data are gitignored (large, and the source is copyrighted); fetch them locally with [`scripts/download_data.sh`](scripts/download_data.sh) (see [`data/data_urls.md`](data/data_urls.md)).

---

## Methods

**Count-based classification.** Rather than a relative zonation coordinate, each hepatocyte nucleus is classified from absolute molecule counts. Raw RNA-assay UMIs are binomially down-thinned to a common 1,500-UMI budget (depth-matched; stable at 1,000 / 1,500 / 3,000), a marker is called present at ≥ 2 UMI (ambient-robust), and each nucleus is assigned to one of four classes — **PC-anchor** (pericentral only), **PP-anchor** (periportal only), **dual** (both; co-expression), **null** (neither). Donor-level class proportions are the inference target, robust across six marker sets (including the original paper's own landmark genes). Raw-extraction integrity is checked (9/9 sanity checks; 69,426 hepatocytes reproduce the published count).

**Differential expression and gene-set tests.** Donor-level pseudobulk with edgeR (TMM normalization, negative-binomial quasi-likelihood) for the genome-wide F4-vs-F1 contrast; pre-specified gene-set tests with `camera` (competitive: is the set shifted more than the rest of the genome?) and `mroast` (self-contained: does the set move on its own, against zero?), plus GSEA pre-rank; ambient-RNA removal with `decontX`.

**Per-cell detox measure.** Detox transcripts per pericentral nucleus on depth-matched counts (composition-independent), summarised per donor.

**Equivalence testing.** Two one-sided tests (TOST) on the donor-level anchor fractions provide an affirmative bound on the largest coordinated shift compatible with the data.

**Confound audit.** Tissue source, procurement stress, sequencing batch, lobe, depth, ambient RNA, cholangiocyte mis-annotation, ploidy/complexity, depth-match discard, and clinical covariates are each tested against the result.

---

## Results

### 1. No transcriptional de-zonation signal in matched biopsies

Across acquisition-matched fibrosis F1 → F4, the count-based classification is flat: pericentral and periportal anchor fractions are non-monotone, dual co-expression stays ~0.4 % (vs ~2.9 % in the confounded explants) and does not trend, and the null fraction (~44/36/39/39 %) and PP:PC ratio (~1.1) are stable. The per-cell pericentral↔periportal gradient retains its shape (only the confounded explant collapses to one pole). Genome-wide pseudobulk DGE finds no zonation gene moving (`GLUL` FDR 0.80); 64 of ~21,000 genes pass FDR, almost all biliary/ductular. An equivalence test excludes a coordinated shift larger than ±19 percentage points, while a ≤ 10-pp drift is **not** excluded (F4 has only 4 donors). The 10-confounder audit does not reproduce the result from any single nuisance variable.

### 2. The published healthy→end-stage trajectory is collinear with tissue acquisition

The dramatic signal is concentrated in the deceased-donor organ tissue (healthy and end-stage), which is procured differently from the needle biopsies that constitute the disease spectrum. The endpoint groups carry an organ-wide handling signature: immediate-early / heat-shock transcripts are elevated ~18× at end-stage in hepatocytes **and** ~18× in endothelium (which has no zonation program), while the hypoxia (HIF) program is comparatively flat — consistent with acute procurement/dissociation, not a zonation change. This is documented as a confound on the endpoint axis; the disease conclusions are drawn only from the matched biopsies.

### 3. One robust biopsy-internal change: the pericentral CYP-detox program dims

A weak coordinated program can evade per-gene FDR but be detected by set-level and per-cell tests. The **pericentral cytochrome-P450 detox set** is the one program that is robust by every standard: competitive camera FDR 2×10⁻⁶, self-contained roast FDR 0.015, GSEA NES −2.04, unchanged under TMM and after decontX, and reproduced by the composition-independent per-cell measure (within-PC detox output 11.9 → 8.8 UMIs/nucleus F1 → F4; Spearman ρ = −0.48, p = 0.003).

The broader pericentral *landmark* set and the phase-II detox set lean down **only faintly** — they reach significance in the competitive test but **fail the self-contained test** (roast FDR 0.081 and 0.220), with no single gene reaching individual significance; a shift this weak cannot be called a turn-off, and the landmark set largely overlaps the detox genes (not independent evidence). The classification gates (`GLUL`, `CYP3A4`) do not move at the per-gene level (FDR 0.80, 0.85), so the cells keep their **class**: this is functional dimming, not de-zonation or transdifferentiation. Load-bearing caveats: the decline is *relative* (transcripts within a fixed budget), a donor-level trend, and could partly reflect a shift among pericentral subzones.

### 4. The biliary/transdifferentiation signal is most consistent with composition

The only per-gene genome-wide change is a small biliary/ductular-marker rise at cirrhotic F4 inside hepatocyte-labelled nuclei. Biliary genes are 5–78× more abundant in cholangiocytes; per-cell hepatocyte co-expression is only ~0.4 %; `decontX` ambient-RNA removal roughly halves the hits. A few genes (`EPCAM`, `SPINT2`, `B3GNT3`) survive, so a rare intrinsic state is not excluded. The leading explanation is compositional (ambient cholangiocyte RNA tracking the F4 ductular reaction) rather than widespread transdifferentiation — **a lead, not a closed result**.

---

## What we claim, and what we do not

- We re-test **only** the snRNA-seq transcriptional evidence. Imaging, protein staining, organoid, and 3D-architecture evidence are not re-analysed, and the strong end-stage phenomenon is not disputed *at end stage*.
- "**No transcriptional de-zonation signal**" in matched biopsies — stated as the absence of a detectable signal with an affirmative equivalence bound, not as a claim that zonation is "preserved" or "intact." A large collapse is excluded; a subtle drift is not.
- The detox **dimming** is a coordinated, *relative*, donor-level decline of the pericentral CYP program — **not** de-zonation or transdifferentiation. No single gene clears per-gene FDR.
- The **biliary** signal is a compositional lead, not a closed verdict.
- Counts measure a **"PC-like program," not lobular position** — they cannot see spatial location.

---

## Repository structure

| Path | Contents |
|---|---|
| [`src/`](src/README.md) | Analysis code by leg: `prep/` (raw→processed extraction + sanity), `confound/` (provenance / source / lobe / stress / batch / power / equivalence), `census/` (count-based PC/PP/dual/null classification + scenario taxonomy), `dge/` (genome-wide + compositional + gene-set DE), `plotting/`. Paths centralised in `config.py`. |
| [`findings/`](findings/README.md) | One folder per finding, each with its data file(s) and a README of numbers / method / caveats — including `DETOX_DIMMING_dossier.md`, `geneset_detox_verification.md`, and `geneset_tests/`. |
| [`results/`](results/) | Generated outputs: `figures/`, donor-level / per-gene `tables/`, provenance schema. |
| [`presentation/`](presentation/) | Slides, figure-generation (`make_figures.py`), the methods/concepts reference (HTML/PDF), and the gene-set-test explainer. Build scripts in [`presentation/build/`](presentation/build/). |
| [`reports/`](reports/) | Written reports (`SYNTHESIS.md`, `finding_stories.md`, LaTeX/PDF). |
| [`data/`](data/) | Raw + processed data and gene-set `signatures/` (large files gitignored). |
| [`scripts/`](scripts/) | `download_data.sh` — fetch the raw data locally. |
| `FINDINGS.md` · `CLAIMS_LEDGER.md` | Story-ordered finding summary, and the audited claim-by-claim trail. |

---

## Reproducing the analysis

```bash
# Python:  numpy scipy pandas scikit-learn statsmodels matplotlib h5py openpyxl
# R:       Seurat · Matrix · edgeR · limma · celda (decontX)

bash    scripts/download_data.sh                 # 0 · fetch data locally

Rscript src/prep/05_extract_raw_panel.R          # 1 · raw RNA-assay UMIs for the marker panel
python  src/prep/06_sanity_raw.py                #     9/9 raw-extraction sanity checks

python  src/census/census_v2.py                  # 2 · count-based PC/PP/dual/null classification
python  src/census/load_bearing.py               #     integrated donor-level table

python  src/confound/raw_counts.py               # 3 · provenance / source / stress / batch / lobe
python  src/confound/equivalence_bound.py        #     affirmative TOST bound

Rscript src/dge/plan_a_genomewide.R              # 4 · edgeR pseudobulk, F4 vs F1
Rscript src/dge/geneset_camera.R                 #     camera / roast gene-set tests (detox dimming)
Rscript src/dge/decontX_replan_a.R               #     ambient-RNA removal, re-test (biliary lead)

python  presentation/make_figures.py             # 5 · regenerate figures
```

See [`src/README.md`](src/README.md) for the full script → finding map.

---

## References

1. Gribben C. *et al.* Acquisition of epithelial plasticity in human chronic liver disease. *Nature* **630**, 166–173 (2024). GSE202379.
2. Squair J. W. *et al.* Confronting false discoveries in single-cell differential expression. *Nat. Commun.* **12**, 5692 (2021).
3. Wu D., Smyth G. K. Camera: a competitive gene set test accounting for inter-gene correlation. *Nucleic Acids Res.* **40**, e133 (2012).
4. Wu D. *et al.* ROAST: rotation gene set tests for complex microarray experiments. *Bioinformatics* **26**, 2176–2182 (2010).
5. Yang S. *et al.* Decontamination of ambient RNA in single-cell RNA-seq with DecontX. *Genome Biol.* **21**, 57 (2020).

---

<div align="center">

**Roee Tekoah** · **Shira Gelbstein** — Computational Genomics (76553), The Hebrew University of Jerusalem

</div>
