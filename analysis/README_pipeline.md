# Prep-day pipeline — how to run

All paths are relative to the **Hackathon folder**. Run scripts from there.

## Order
1. **`01_extract_paper1_hepatocytes.R`** *(already run)* — pulls hepatocytes + metadata out of the Seurat `.rds` into `analysis/paper1/` (`counts.mtx`, `genes.txt`, `barcodes.txt`, `cell_metadata.csv`). Needs R + Seurat.
2. **`pipeline.py`** — Steps 2–8 baseline (signature-scoring track):
   - load → normalize → signature score (pseudo-zonation coordinate)
   - Step 5 validation on healthy donors (positive control)
   - Step 5b ruler-validity (PC–PP correlation per stage)
   - Step 6 collapse curve + trend test → `out/collapse.{csv,png}`
   - Step 7 zone-binned differential expression + BH-FDR → `out/de_portal.csv`, `out/de_central.csv`
   - Step 8 de-zonation ↔ plasticity link
   - writes `out/coordinates.csv`, `out/RESULTS`-style stdout.
3. **`classifier_step.py`** — Step 4b headline upgrade: trains a zone classifier on Paper 2's snRNA hepatocytes, applies to Paper 1, and reports **prediction entropy per stage** (the principled de-zonation metric) → `out/classifier_entropy.csv`.

## Requirements
```
pip install numpy scipy pandas scikit-learn statsmodels matplotlib h5py
```
R side: `Seurat`, `Matrix`.

## Memory / runtime notes
- `pipeline.py` loads the full `counts.mtx` via `scipy.io.mmread` (~8–12 GB RAM for the real file; close other apps). Steps 2–6 are fast; **Step 7 (DE) is the slow part** (a few minutes) because it touches all genes.
- `classifier_step.py` restricts to a shared feature-gene set, so it stays light.

## The two things to firm up *during* the hackathon (by design)
- **Step 5b puzzle:** in the quick feasibility run the periportal arm behaved but the **pericentral arm was weak** in Paper 1 snRNA. Diagnosing this (dropout vs snRNA nascent-bias vs genuine early pericentral collapse) is core hackathon work — widen the pericentral signature, try rank-based scoring, and read the ruler diagnostics.
- **Classifier labels:** `classifier_step.py` currently derives Paper 2 zone labels from the signature terciles (Option A, quick). Upgrade to Paper 2's Visium-HD→snRNA zonation mapping (their repo `parse_snRNAseq_combined_atlas.m`) for ground-truth labels (Option B) if time allows.

## Validation status
`pipeline.py` was smoke-tested end-to-end on synthetic data with a known, decaying zonation signal: validation-marker signs correct, ruler weakening reproduced, collapse trend monotonic, DE recovers significant genes, plasticity test runs. The scoring track was also confirmed on real Paper 2 hepatocytes (coordinate recovers zonation: CYP2E1 ρ≈+0.29, ASS1 ρ≈−0.48).
