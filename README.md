<div align="center">

# 🧬 Liver Zonation Re-Analysis in MASLD

### A rigorous, honest re-test of the single-nucleus RNA-seq evidence for hepatocyte de-zonation in fatty-liver disease

*Re-examining Gribben et al., **Nature** 2024 — "Acquisition of epithelial plasticity in human chronic liver disease" (GEO: GSE202379)*

<br>

[![Language: R](https://img.shields.io/badge/R-Seurat%20%7C%20edgeR%20%7C%20limma-276DC3?logo=r&logoColor=white)](https://www.r-project.org/)
[![Language: Python](https://img.shields.io/badge/Python-numpy%20%7C%20scipy%20%7C%20statsmodels-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Data: GSE202379](https://img.shields.io/badge/data-GSE202379-8A2BE2?logo=databricks&logoColor=white)](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE202379)
[![Course: 76553](https://img.shields.io/badge/Computational%20Genomics-76553%20·%20HUJI-0D9488)](https://www.cs.huji.ac.il/)
[![Nuclei](https://img.shields.io/badge/nuclei-~99,809-EA580C)]()
[![Donors](https://img.shields.io/badge/donors-47-1D4ED8)]()
[![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-green.svg)](LICENSE)

<br>

**One-line result:** *In acquisition-matched MASLD biopsies we find **no transcriptional de-zonation signal** — but the pericentral **detox** program **dims** (relative, donor-level). The dramatic published trajectory tracks how the tissue was acquired, not the disease.*

</div>

---

## 📑 Table of contents

- [The question](#-1--the-question)
- [The catch](#-2--the-catch)
- [The method](#-3--the-method)
- [Results](#-4--results)
- [The one real change: detox dimming](#-5--the-one-real-change-detox-dimming)
- [Where the biliary signal comes from](#-6--where-the-biliary-signal-comes-from)
- [Conclusion](#-7--conclusion)
- [Repository structure](#-repository-structure)
- [Data](#-data)
- [Reproduce](#-reproduce)
- [Scope & honesty](#-scope--honesty)
- [Authors](#-authors)

---

## ❓ 1 · The question

Hepatocytes are **transcriptionally zonated**: cells near the central vein run a *pericentral* program (e.g. `GLUL`, `CYP3A4`, the CYP/detox genes, Wnt-driven), while cells near the portal tract run a *periportal* program (e.g. `ASS1`, `CPS1`, `PCK1`, the urea cycle).

Gribben et al. (2024) reported that across MASLD (metabolic dysfunction–associated steatotic liver disease, i.e. fatty-liver disease) hepatocytes **progressively lose this zonation** and acquire cholangiocyte-like identity through a hepatocyte→cholangiocyte **transdifferentiation**, "prominent in end-stage."

> **Our question:** Does hepatocyte zonation degrade across MASLD — and is that degradation linked to the hepatocyte→cholangiocyte transdifferentiation the paper describes?

---

## ⚠️ 2 · The catch

Two problems sit underneath the original reading.

**(a) The metric is relative.** The signal was first read with a *relative* ruler — a z-scored zonation coordinate plus marker–marker correlations, pooled across all samples. A relative summary is scale-free: it divides out the overall level and reads only the *shape* of the gradient. So it **hides who moved** — which cells, how many, from where — and it is tilted by sequencing depth, cell number, and tissue source. "Losing zonation" is not one event but four distinct, dissociable moves (depletion, co-expression, turn-off, composition shift), each with its own count signature — a single z-score or correlation collapses all four into one number.

**(b) Disease stage is entangled with how the tissue was taken.** Healthy and end-stage samples are **deceased-donor organ cubes / explants**; the F0–F4 fibrosis-stage samples are **16-gauge needle biopsies** (n = 2 / 8 / 12 / 12 / 4). The ends are *not* acquisition-matched to the biopsies, so a "progressive" trajectory can be manufactured by procurement, ischemia, dissociation, and batch — not disease. The explant ends also carry organ-wide handling stress: immediate-early / heat-shock genes spike ~18× in the ends, but **endothelium — which has no zonation program — spikes ~18× too**, while hypoxia (HIF) stays flat. That is acute handling, not a zonation change.

> **Our response:** count molecules instead of reading a relative summary, and analyze **biopsy-only F1–F4** so disease stage is not confounded with acquisition.

---

## 🔬 3 · The method — raw-count anchor classification

We re-test the claim in **absolute molecule counts**, with the **donor** (~47) as the unit of inference — never the cell.

```text
  raw UMI counts  →  down-thin to 1,500  →  marker ON if ≥ 2 UMI  →  classify nucleus (PC/PP/dual/null)  →  fraction per donor
```

| Step | Why |
|---|---|
| **Raw UMIs, not SCT** | A single molecule may be ambient — absolute detection is what matters; SCT residuals are the wrong object. |
| **Binomial down-thin to 1,500 UMIs** | Depth-match every nucleus so sequencing depth can't drive detection (stable at 1k / 1.5k / 3k). |
| **Call a marker at ≥ 2 UMI (not ≥ 1)** | Kills ambient "soup" — apparent co-expression drops ~7–10% → ~0.2–0.5%. |
| **Classify each hepatocyte** | PC-anchor (pericentral only), PP-anchor (periportal only), Dual (both — co-expression), Null (neither). |
| **Infer at the donor level (~47)** | No pseudoreplication; robust across 6 marker sets (2–1,637 genes, including the original paper's own landmarks). |

Raw-extraction integrity: **9/9 sanity checks pass** (integer UMIs; 69,426 hepatocytes match the paper).

---

## 📊 4 · Results

Across matched biopsy **F1–F4**:

- **No depletion.** Pericentral and periportal anchor fractions are flat / non-monotone.
- **No co-expression.** Dual (≥ 2 UMI) stays ~0.4% (vs ~2.9% in confounded explants) and does not trend.
- **Null & PP : PC flat too.** Null ≈ 44 / 36 / 39 / 39%; PP : PC ratio ≈ 1.1.
- **The per-cell gradient holds its shape.** The mass stays spread across the pericentral↔periportal axis; only the confounded explant collapses to a single pole. The middle drifts only 22 → 24 → 28 → 26% (peak F3, then reverts) — mild and non-monotone.
- **Genome-wide, nothing usable moves.** Pseudobulk edgeR, cirrhotic F4 vs F1: 64 of ~21,000 genes pass FDR (mostly biliary/ductular); zonation genes are flat (**`GLUL` FDR 0.80**).
- **A 10-confounder audit clears it.** Tissue source, procurement stress, sequencing batch, lobe, depth, ambient RNA, cholangiocyte mis-annotation, ploidy/complexity, depth-match discard, and clinical covariates — none manufactures the result.

> ➡️ **No transcriptional de-zonation signal across matched biopsies.** A large collapse (> ±19 pp shift, TOST) is excluded; a subtle ≤ 10 pp drift is not (F4 has only 4 donors).

---

## 💡 5 · The one real change: detox dimming

There is **one** real biopsy-internal change. Within pericentral nuclei, the **detox program's level falls** with fibrosis:

- Within-PC detox output (depth-matched transcripts per PC nucleus) declines from ~11.9 at F1 to ~8.8 at F4; donor-level Spearman **ρ = −0.48, p = 0.003**.
- Gene-set tests (CAMERA / ROAST) agree: PC detox (CYP) FDR 2×10⁻⁶, PC identity 1.5×10⁻⁴, both **down**; biliary + fibrogenesis + inflammation controls **up**; ER-stress flat (validating controls behaved).
- Measured on detox genes (`CYP2E1`, `CYP1A2`, `ADH4`…) **disjoint** from the `GLUL` / `CYP3A4` identity anchors — so the anchor fraction stays flat while the module dims.

> Like a radio: **the genre held** (cells keep their zonal identity); **the volume dropped** (the program dims). This is **functional dimming, NOT de-zonation or transdifferentiation.**

**Careful framing (load-bearing):** the dimming is a *relative* decline (transcripts within a fixed 1,500-UMI budget), **not proven absolute molecule loss**; it is a **donor-level trend**; it could partly reflect a shift among pericentral subzones; and no single detox gene clears per-gene FDR — only the coordinated gene set plus the per-cell trend.

---

## 🧪 6 · Where the biliary signal comes from

The biliary / cholangiocyte-marker signal is **most likely compositional** — a **lead, not a closed verdict**.

| Evidence | Reading |
|---|---|
| 🟢 **Strong** | Biliary genes are cholangiocyte genes (5–78× more abundant there); per-cell hepatocyte co-expression is only ~0.4%. |
| 🟠 **Suggestive** | `decontX` ambient-RNA removal halves the hits — an ambient contribution, not proof. |
| 🔴 **Open** | `EPCAM` / `SPINT2` / `B3GNT3` survive — a rare intrinsic state is **not** excluded; `CXCL10` is a separate inflammatory lead. |

The dominant evidence points to composition / ambient RNA most likely tracking the **F4 ductular reaction** — but we do not overstate it.

---

## 🎯 7 · Conclusion

**Zonal identity holds — and the pericentral detox program dims.**

1. **Cells keep their zonal identity** across matched biopsies — *no transcriptional de-zonation signal* (a large shift is excluded).
2. **The one real change** is that the pericentral detox program *dims* — relative, donor-level, functional; not de-zonation.
3. **The dramatic published trajectory tracks acquisition, not disease** — the full healthy→end-stage arc is source-confounded.

We **do not** claim to overturn the paper. We re-test **only** the snRNA-seq transcriptional evidence — we correct **one evidence leg** (the marker-correlation reading). The paper's **imaging, protein staining, and organoid** evidence are untouched, and we agree the strong end-stage phenomenon is real *at end stage*. The biliary signal is a separate compositional lead.

---

## 🗂️ Repository structure

| Path | What's inside |
|---|---|
| [`src/`](src/README.md) | All current analysis code, grouped by analysis leg: `prep/` (raw→processed extraction + sanity), `confound/` (provenance/source/lobe/stress/batch/power/equivalence), `census/` (count-based PC/PP/dual/null anchor classification + scenario taxonomy), `dge/` (genome-wide + compositional + gene-set differential expression), `legacy/`, `plotting/`. Paths centralized in `config.py`. |
| [`findings/`](findings/README.md) | The findings store — one folder per finding, each with its data file(s) and a README of numbers / method / caveats, ordered by the story. Includes the `DETOX_DIMMING_dossier.md` and `geneset_tests/`. |
| [`results/`](results/) | Generated outputs: `figures/`, donor-level / per-gene `tables/`, `reports/`, and provenance (`object_schema.txt`). |
| [`presentation/`](presentation/) | The talk: the final deck `MASLD_stages_computational_analysis_roee_shira.pptx` (+ PDF), the methods/concepts reference (PDF/HTML), `make_figures.py`, and `assets/` (figures). The pptxgenjs build scripts and earlier rendered deck live in [`presentation/build/`](presentation/build/). |
| [`reports/`](reports/) | Written outputs: `FULL_STORY.txt`, `SYNTHESIS.md`, `finding_stories.md`, `DGE.md`, and LaTeX/PDF reports. |
| [`data/`](data/) | Local raw + processed data and gene-set `signatures/` (large files gitignored — each machine downloads its own; see `scripts/`). |
| [`papers/`](papers/) | Source papers (gitignored — copyrighted). |
| [`scripts/`](scripts/) | `download_data.sh` — fetch the raw data locally. |
| [`archive/`](archive/) | Stale / legacy material: the pre-reanalysis pipeline, old figures, prior code backups. Not part of the current story. |
| `FINDINGS.md` · `CLAIMS_LEDGER.md` | Story-ordered finding summary, and the audited claim-by-claim trail with decisions + future-work queue. |

---

## 🧫 Data

| | |
|---|---|
| **Source** | Gribben et al., *Nature* 2024 — GEO accession **[GSE202379](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE202379)** |
| **Scale** | ~**99,809** nuclei · **69,426** hepatocytes · **47** donors |
| **Cohort used** | Biopsy-only **F1–F4** (16-gauge needle biopsies); deceased-donor / explant ends excluded as acquisition-confounded |
| **Unit of inference** | The **donor** (~47), never the cell |

Raw and processed data are **gitignored** — fetch them locally (see [`scripts/download_data.sh`](scripts/download_data.sh) and [`data/data_urls.md`](data/data_urls.md)).

---

## ⚙️ Reproduce

**Dependencies**

```bash
# Python
pip install numpy scipy pandas scikit-learn statsmodels matplotlib h5py openpyxl

# R
#   Seurat · Matrix · edgeR · limma · celda (decontX)
```

**Pipeline entry points** (every count/DGE script is standalone — it reads the raw panel / pseudobulk via `config.py`):

```bash
# 0 · fetch data locally
bash scripts/download_data.sh

# 1 · extract raw RNA-assay UMIs for the marker panel  (raw, not SCT)
Rscript src/prep/05_extract_raw_panel.R
python  src/prep/06_sanity_raw.py            # 9/9 sanity checks

# 2 · count-based anchor classification (PC/PP/dual/null), depth-matched + sensitivity grid
python  src/census/census_v2.py
python  src/census/load_bearing.py           # integrated donor-level table

# 3 · confound / provenance leg (source, stress, batch, lobe, equivalence bound)
python  src/confound/raw_counts.py
python  src/confound/equivalence_bound.py    # affirmative TOST bound

# 4 · genome-wide + gene-set differential expression
Rscript src/dge/plan_a_genomewide.R          # edgeR pseudobulk, TMM + NB-QL, F4 vs F1
Rscript src/dge/geneset_camera.R             # CAMERA / ROAST gene-set tests (detox dimming)
Rscript src/dge/decontX_replan_a.R           # ambient-RNA removal, re-test (biliary lead)

# 5 · rebuild the deck figures + slides
python  presentation/make_figures.py
node    presentation/build/build_deck.js
```

See [`src/README.md`](src/README.md) for the full **script → finding** map.

---

## 🔒 Scope & honesty

- We re-test **only** the single-nucleus RNA-seq **transcriptional** zonation/plasticity evidence. Imaging, protein staining, organoid, and 3D-architecture evidence are **not** re-analyzed.
- **"No transcriptional de-zonation signal"** — never bare "no de-zonation," and we do **not** claim zonation is "preserved." A large collapse is excluded; a subtle drift is not.
- The detox **dimming** is a **relative**, donor-level decline (not proven absolute molecule loss); it is **not** de-zonation or transdifferentiation.
- The **biliary** signal is **a lead, not closed** — compositional / ambient RNA most likely, a rare real state not excluded.
- All quantitative claims are on **raw RNA UMI counts**; the unit of inference is the **donor** (~47).
- We measure a **"PC-like program," not lobular location** — counts cannot see spatial position.

---

## 👥 Authors

<div align="center">

**Roee Tekoah** · **Shira Gelbstein**

Computational Genomics (76553) · The Hebrew University of Jerusalem · Hackathon

</div>
