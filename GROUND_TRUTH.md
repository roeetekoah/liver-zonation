# GROUND_TRUTH.md — verified facts for the Hepatocyte-Zonation project

**Status: authoritative.** Every claim here is tagged with its source and was checked against
the primary source, not prose:
- `[P1 p.N]` = Paper 1 PDF (`papers/s41586-024-07465-2.pdf`), page N.
- `[P2 p.N]` = Paper 2 PDF (`papers/s41586-026-10377-y.pdf`), page N.
- `[code]` / `[data]` = verified by opening the file in this repo.
- `[TO-VERIFY]` = not yet confirmed against a primary source; do not rely on it.

This file exists because the repo's narrative docs over-claimed and caused real confusion.
**If any other doc disagrees with this file, this file wins; if this file disagrees with the
papers/code/data, fix this file.** (See the quarantine rule at the top of `CLAUDE.md`.)

---

## 1. The two papers (identity)

**Paper 1 — the DISEASE cohort (what we score/classify).**
"Acquisition of epithelial plasticity in human chronic liver disease", Gribben, Galanakis,
… Mohorianu, Vallier. *Nature* 630:166-173 (2024). DOI 10.1038/s41586-024-07465-2. GEO
**GSE202379**. `[P1 p.166, p.12]`
- Human liver **single-nucleus** RNA-seq (10x 3′, GRCh38), **spatially BLIND** (dissociated
  nuclei; all spatial info in the paper is from separate IF/3D-imaging, not the sequencing). `[P1 p.166, p.10-11]`
- 47 biopsies; ~99,809 QC'd nuclei; enriched for **hepatocytes (n=69,426)** + cholangiocytes
  (5,412). `[P1 p.168, p.11]`
- Core finding we build on: **"Hepatocytes lose their zonation"** with disease, and undergo
  **hepatocyte↔cholangiocyte transdifferentiation** (no stem/progenitor). `[P1 p.166, p.168-169]`

**Paper 2 — the HEALTHY spatial RULER (where zonation is defined).**
"A spatial atlas of the healthy human liver from live donors", Yakubovsky, … Itzkovitz.
*Nature* 653:1148-1157 (2026). DOI 10.1038/s41586-026-10377-y. GitHub `OranYak/Human-liver`;
Zenodo 17735506. `[P2 p.1148, p.1155]`
- Healthy human liver via Visium, **Visium HD**, MERFISH, PhenoCycler + **snRNA-seq** (4 donors
  M5-M8, >67k nuclei). `[P2 p.1148, p.1152-1153]`
- Provides the zonation reference; does **not** itself transfer onto an external disease
  snRNA-seq cohort — that transfer is *our* project. `[P2 p.1155-1156]`

---

## 2. Zonation — the canonical definition (Paper 2) — READ THIS

- The lobule axis is **porto-central**. **Pericentral (PC)** = central-vein end; **Periportal
  (PP)** = portal-triad end. `[P2 p.1148]`
- **8 zones** for the human atlas (cross-species analyses use 6). `[P2 p.13-14]`
- **The zonation framework IS spatially grounded and cross-validated — not expression-only.**
  The axis and the landmark genes come from REAL spatial data: Visium / Visium HD spots have
  physical coordinates; CYP2E1's pericentral location was validated against a **certified
  pathologist's portal-triad annotation**; landmark genes were chosen by spatial correlation with
  CYP2E1 across spots; zones were **spatially median-smoothed** (re-assign each spot to the median
  zone of neighbours <150 μm); Visium HD ↔ Visium agree (Spearman R=0.7); PCK2/GLUT2 confirmed by
  **IHC**; MERFISH zonation uses physical **distance from NOTCH3+ cells**. So the ruler is anchored
  in spatial measurement and validated by it. `[P2 p.13-14, p.1150]`
- **Only the DISSOCIATED snRNA per-nucleus assignment lacks a physical coordinate.** Those nuclei
  "lacked spatial resolution owing to tissue dissociation", so each is given **one of 8
  pseudo-zones** via η over the *spatially-derived* landmark genes — i.e. spatially-INFORMED
  expression, not spatial-free, and not a micron coordinate. `[P2 p.1153, p.14]`
- **The assignment formula (verbatim):** zonation score =
  `sum(periportal LM expr) / (sum(periportal LM expr) + sum(pericentral LM expr))`, i.e.
  **η = ΣPP / (ΣPP + ΣPC)** over landmark genes, then binned into 8 equal-percentile zones. `[P2 p.14]`
  - **HIGH η = periportal, LOW η = pericentral.** `[P2 p.13-14]`
  - This is exactly what `src/prep/02_convert_paper2_mat.py` computes and what
    `parse_snRNAseq_combined_atlas.m` does. **Our cached `zone_label` IS Paper 2's own method.** `[code]`
- **Landmark genes — there are TWO schemes; know which you use:** `[P2 p.13-14]`
  1. *Primary Visium hepatocyte set*: top 20 genes most correlated / most anticorrelated with
     **CYP2E1** across spots (20 PC + 20 PP).
  2. *Cell-type-specific set (from Visium HD center-of-mass, used for the snRNA atlas)*: per cell
     type, top/bottom 20 genes by center-of-mass (20 PC + 20 PP).
  - **Our `signatures/*_paper2_landmark.txt` = scheme 2's hepatocyte set** (= the repo's
    `Hepatocyte-{PC,PP}-LM.csv`; e.g. PC: SLCO1B3, CYP3A4, CYP2E1, ADH1B, ADH4, AOX1…; PP: HAMP,
    ASS1, ALDOB, SERPINA1, APOA1, HAL…). This is the correct set for zonating snRNA cells. `[code]`
- **Center of mass (COM):** expression-weighted mean zone (1-8) of a gene; low COM = pericentral,
  high COM = periportal. Available per gene in `zon_struct_all_full.mat` / `supplementary_table_8`. `[P2 p.13][data]`
- **Zonated-gene count:** 1,141 of 1,724 hepatocyte genes are significantly zonated **at q<0.25**
  (NOT q<0.05). `[P2 p.1150]`  ⚠️ Our `full` set is **1273 PC + 364 PP = 1637** genes built from
  `supplementary_table_8` — the exact threshold/COM split used to get those counts is `[TO-VERIFY]`
  against the table (do not assume it equals the paper's 1,141/q<0.25 figure).
- **Human-specific zonation confirmed by Paper 2 (with IHC):** **PCK2 is pericentral in humans**
  (mitochondrial gluconeogenesis); GLUT2/SLC2A2, HNF4A, urea-cycle (NAGS/CPS1/OTC/ASL), and
  several lipid genes also pericentrally shifted vs mouse. `[P2 p.1150-1152]`

**Canonical hepatocyte markers + direction** (use for validation gates) `[P2 p.13, p.1150-1152]`:
- Pericentral (+): **CYP2E1, CYP1A2, GLUL, PCK2** (also CYP3A4, ADH1/4, SLCO1B3, FASN…).
- Periportal (−): **ASS1, ALDOB, PCK1, HAL** (also ALB, SERPINA1, SDS, HAMP…).
- ⚠️ **PCK1 (cytosolic) is periportal; PCK2 (mitochondrial) is pericentral** — do not confuse them.

---

## 3. Disease axis (Paper 1) — the ordered stages

Five-level, **histology-defined** ordinal axis (Healthy → … → End stage). `[P1 p.167]`

| order | stage label (new = old)            | snRNA donors n |
|------:|------------------------------------|---------------:|
| 0     | Healthy control                    | 4              |
| 1     | MASLD = **NAFLD**                   | 7              |
| 2     | MASH = **NASH** (w/ fibrosis F1-F4) | 27             |
| 3     | Cirrhosis                          | 4              |
| 4     | End stage                          | 5              |

`[P1 p.167 Fig.1c; p.170 Fig.3e]` (4+7+27+4+5 = 47).
- **MASLD≡NAFLD and MASH≡NASH** (old/new nomenclature used interchangeably in the paper); the
  GEO object may use either — handle both. `[P1 p.170]`
- ⚠️ A *different* cohort (serum-insulin, n≈101: 7/19/63/9/3) appears in ED Fig.9e — **NOT** the
  snRNA cohort. Only **4/7/27/4/5** applies to the sequencing data. `[P1 p.22]`
- Our code's `STAGE_ORDER` = `["Healthy control","NAFLD","NASH w/o cirrhosis","NASH with
  cirrhosis","end stage"]`, matching the data's actual `stage` strings (verified: counts
  3750/7073/31903/3603/23097 hepatocytes; donors 4/7/27/4/5). `[code][data]`
- SAF / NAS / explicit F0-F4 per-patient columns: **not found in the paper text** — if present they
  live in Supplementary Tables 1-2 / GEO metadata. `[TO-VERIFY]`

---

## 4. What the papers already establish about our hypotheses

- **H1 (zonation collapses with disease): already shown qualitatively by Paper 1** — healthy
  hepatocytes separate by PC/PP markers; end-stage hepatocytes **co-express** PC+PP markers; they
  quantified loss via degrading PC-PP marker correlation (Welch's t-test). Our contribution =
  quantify it donor-level with Paper 2's ruler. `[P1 p.168, ED Fig.5b]`
- **H3 (de-zonation ↔ plasticity): Paper 1's central theme.** Plasticity markers to use:
  **KRT7, KRT19, SOX9, SOX4, KRT23, NCAM1** (and KLF6, TNFRSF12A), rising toward end stage;
  transdifferentiation is hepatocyte↔cholangiocyte, **not** stem/progenitor. `[P1 p.169-170, ED Fig.8]`
- **De-zonation ≠ plasticity:** loss of zonal *position* (Fig.2b) is distinct from loss of
  *identity* (KRT/SOX markers, Fig.3). `[P1 p.168-169]`

---

## 5. Local data we actually have (verified)

`[data]` unless noted:
- `data/processed/paper1/` — Paper 1 hepatocytes: `counts.npz` (genes×cells, 30117 genes ×
  69426 cells), `genes.txt`, `barcodes.txt`, `cell_metadata.csv` (cell_id, cell_type, stage),
  `metadata_all_cells.csv` (incl. **Patient.ID** = donor, 47 donors, 0 NA).
- `data/processed/paper2_train.npz` — Paper 2 snRNA hepatocytes for the classifier: `X`
  (50979 cells × 1639 genes), `feats`, `zone_label` (η-over-landmark, 3 terciles), `donor`.
- `data/processed/paper2_zonation_reference.csv` + `paper2_zonation_profiles.npz` — Paper 2's
  **real gene-level spatial zonation** (healthy elem "M4-8"): `com`, `qval`, 8-layer `mn`
  (8×36601); 3220 genes qval<0.05. Extracted by `src/prep/04_extract_spatial_reference.py`.
- `data/raw/` (git-ignored): `combined_scRNAseq_atlas_M5M6M7M8.mat` (Paper 2 snRNA atlas; `t` has
  **no per-cell zone field** — `t.zone` is computed at runtime by `parse_snRNAseq_combined_atlas.m`),
  `zon_struct_all_full.mat` (gene-level zonation, 10 condition elements; elem1 = healthy M4-8),
  `Human-liver/` (Paper 2 code + LM CSVs), supplementary tables, both paper PDFs in `papers/`.

---

## 6. Our two inference methods (current code state)

1. **Scoring (signature mean).** coord = `mean_z(PC) − mean_z(PP)` per cell, computed for each set
   in `config.SETS_TO_COMPARE` (currently `["paper2_landmark","full"]`; `core`/`expanded` also
   exist). PC high = pericentral. `[code: steps/step4_score.py, pipeline.py]`
   - Verified result: `paper2_landmark` is a valid ruler (healthy PC-PP anticorr −0.45) and shows
     donor-level H1 collapse; the unweighted `full` set **dilutes** (healthy PC-PP corr +0.53) and
     is null. See memory `full-set-dilutes-zonation`.
2. **Classifier (learned over genes).** Calibrated multinomial logistic regression trained on
   Paper 2 zone labels, applied to Paper 1 → per-cell zone probabilities + **entropy**.
   `[code: steps/step4b_classifier.py]`
   - **It IS trained on every run** (train/test split on Paper 2; held-out accuracy **0.755** vs
     0.333 chance, with the 40 landmark genes EXCLUDED). Earlier runs only *looked* skipped because
     `RUN_CLASSIFIER` defaulted False; it is now True. `[code, classifier_eval.csv]`
   - ⚠️ **It is NOT yet over the whole transcriptome.** Features = the signature-tier union present
     in P1∩P2 (~1639 genes; 1599 after landmark exclusion), because `paper2_train.npz` was built
     from the signature union. Truly whole-transcriptome would mean rebuilding features from all
     ~P1∩P2 genes. `[code]` `[TO-VERIFY: rebuild for full transcriptome]`
   - **Labels are landmark/expression-derived**, so entropy is an **AUXILIARY** layer, never a
     headline (guardrail). Landmark exclusion reduces — not eliminates — circularity.

---

## 7. Non-negotiable conventions / guardrails

- **Unit of inference = DONOR**, never cell (~47 donors vs ~69k cells). Cell-level p-values =
  pseudoreplication. Aggregate per donor, then test the trend. `[project]`
- PC high in our coord; pericentral markers correlate **+**, periportal **−**, in healthy. `[P2]`
- **PCK2 pericentral (human-specific); PCK1 periportal.** `[P2 p.1150]`
- De-zonation (lost position) ≠ plasticity (lost identity). `[P1]`
- Entropy from the classifier is auxiliary unless trained on independent ground-truth labels.
- H2 driver test must guard circularity (held-out gene split), since the coordinate is built from
  the same genes. `[project]`

---

## 8. Open items to verify against primary sources (`[TO-VERIFY]`)

1. Exact threshold/COM rule that produced our `full` set (1273 PC + 364 PP) from
   `supplementary_table_8` — paper's headline zonation count is 1,141 at q<0.25.
2. Per-patient stage labels + any SAF/NAS/F0-4 columns (Paper 1 Supplementary Tables 1-2 / GEO).
3. Whether to make the classifier truly whole-transcriptome (rebuild `paper2_train.npz` features).
