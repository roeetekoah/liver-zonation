# The pipeline, step by step (plain English)

This explains **every step**, what it takes in and puts out, and — the common question —
**why `pipeline.py` starts at "Step 2".**

## Why does it start at Step 2? What is Step 1?

**Step 1 is the prep that is already done.** "Step 1 = build the ruler from Paper 2": turn
the reference paper into the things the analysis needs — the **signature gene lists** and the
**zone-labelled training nuclei**. That work lives in `src/prep/` and `signatures/`, and its
outputs are committed/regenerable. Because Step 1's outputs already exist before the
hackathon, the live analysis driver (`pipeline.py` / `run_all.py`) begins at **Step 2**
(loading the disease data). Nothing is missing — Step 1 just runs earlier, in prep.

The numbering is the same everywhere:
- **Step 1** → `src/prep/` (+ `signatures/`)  — prep, done.
- **Steps 2–8** → `src/pipeline.py` (reference) and `src/steps/step2…step8` (stubs) — the analysis.
- **Step 9** → `src/steps/step9_bonus_enrichment.py` — optional stretch.

`run_all.py` runs Steps 2–8; `run_p2_validation.py` is a separate positive control (see `README.md`).

---

## Step 1 — Build the ruler from Paper 2  *(prep — DONE)*
**Goal:** get a healthy zonation reference into usable form.
**In:** Paper 2 landmark CSVs + supplementary zonation table + the snRNA `.mat`.
**Out:** `signatures/*_{core,expanded,revised,sensitivity}.txt` and `data/processed/paper2_train.npz`.
**Code:** `prep/02_convert_paper2_mat.py`, `prep/03_build_expanded_signatures.py`; signatures in `signatures/` (+ its README).
**Artefact:** A1. **Why:** everything downstream needs (a) which genes mark each end and (b) labelled cells to train the classifier.

## Step 2 — Load & QC the Paper 1 hepatocytes
**Goal:** get the disease cells into memory with their stage and donor.
**In:** `data/processed/paper1/` (raw counts + metadata).
**Out:** the count matrix + per-cell `stage`, `donor` (= `Patient.ID`), library size; per-stage/per-donor counts.
**Code:** `steps/step2_load_qc.py` (ref: `pipeline.py:load`).
**Artefact:** A2. **Why:** QC is inherited (we sanity-check, not re-filter); we keep RAW counts and normalize later so Paper 1 and Paper 2 get identical preprocessing. Donor IDs are grabbed here because every later test is donor-level.

## Step 3 — Harmonize genes & fix the batch axis
**Goal:** make Paper 1 and Paper 2 speak the same gene language.
**In:** A2 genes + the signature gene sets.
**Out:** the shared gene set; a reported mapping rate; z-/rank-scaled features.
**Code:** `steps/step3_harmonize.py`. **Artefact:** A3.
**Why:** a score only transfers if the feature genes exist and are scaled the same on both sides; rank/z features stop the score from measuring "snRNA vs Visium" instead of "portal vs central".

## Step 4 — Place every cell (score + classifier)
**4a Score:** `coordinate = mean_z(pericentral) − mean_z(periportal)` per cell — a signed pseudo-zonation position. (`steps/step4_score.py`, ref `pipeline.py:score`.)
**4b Classifier:** train a calibrated multinomial logistic regression on `paper2_train.npz`, check held-out accuracy on Paper 2, then `predict_proba` on Paper 1 → per-cell zone probabilities and **entropy** (= confusion = de-zonation). (`steps/step4b_classifier.py`, ref `classifier.py`.)
**Out:** the `A4` per-cell table `[cell_id, donor, stage, coordinate, pc, pp, plasticity, zone_probs…, entropy]`.
**Why:** two independent readers of the same thing — the robust score and the confidence-aware classifier — that should agree on healthy cells.

## Step 5 — Validate on healthy (positive control)  *(GATE)*
**Goal:** prove the placement is real before trusting disease.
**In:** A4 restricted to Paper 1 healthy donors.
**Out:** Spearman(coordinate, marker) — GLUL/CYP2E1 > 0, ASS1/HAL < 0 — and low classifier entropy.
**Code:** `steps/step5_validate.py` (ref `pipeline.py:validate`). **Artefact:** A5.
**Why / gate:** if healthy cells don't recover zonation, stop and fix scoring — do not proceed to Step 6.

## Step 5b — Is the ruler still a ruler?
**Goal:** decide *which kind* of breakdown each stage shows, so collapse isn't read naively.
**Out (per stage):** internal coherence, cross-program anti-correlation, split-half reproducibility, program-off vs restriction-lost.
**Code:** `steps/step5b_ruler_diagnostics.py`. **Artefact:** A5b.

## Step 6 — Quantify the collapse  *(H1, headline)*
**Goal:** does zonation erode across stages?
**In:** A4 + A5/A5b.
**Out:** ONE metric **per donor** (coordinate spread, PC–PP anti-correlation, mean entropy) → ordered-trend test across stages + donor-bootstrap CI + donor-label-shuffle null.
**Code:** `steps/step6_collapse.py` (ref `pipeline.py:collapse`); plot `plot_a6_collapse`. **Artefact:** A6.
**Why:** unit of inference = donor (≈47), never cell — cell-level p-values are pseudoreplication.

## Step 7 — Which genes drive it  *(H2)*
**Goal:** which programs collapse first, and where.
**In:** A4 + the count matrix.
**Out:** **pseudobulk** per donor × zone → test the stage effect (interaction `expr ~ coord + stage + coord:stage`), BH-FDR; report hits **excluding** the signature genes (circularity guard) / held-out split.
**Code:** `steps/step7_de.py` (ref `pipeline.py:de`); plot `plot_a7_volcano`. **Artefact:** A7.

## Step 8 — De-zonation ↔ plasticity  *(H3)*
**Goal:** are the most de-zonated cells the ones gaining bile-duct identity?
**Out:** within-donor correlation (and OLS `plast ~ dez + C(stage) + C(donor)`) — never pooled across cells (stage confounds it).
**Code:** `steps/step8_plasticity.py` (ref `pipeline.py:plasticity`); plot `plot_a8_plasticity`. **Artefact:** A8.

## Step 9 — Bonus: collapse vs inherited risk (Paper 3)  *(optional)*
**Goal:** are Step-7 collapse-driver genes enriched for inherited MASLD risk-variant targets?
**Out:** hypergeometric/Fisher overlap vs an expression-matched background, BH-corrected.
**Code:** `steps/step9_bonus_enrichment.py`. **Artefact:** A9.
**Why optional:** gene-list only, ~30 min; the project stands fully on H1–H3 without it.
