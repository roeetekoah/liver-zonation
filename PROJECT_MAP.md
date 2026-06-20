# Project map — Spatial Degradation of Hepatocyte Zonation

The index to this folder: what we have (data, code, results, deliverables) and what's left.

---

## Folder layout (top level)

```
Hackathon/
├── PROJECT_MAP.md            ← this file (the index)
├── papers/                   ← the source paper PDFs
├── data/                     ← all raw inputs (large)
├── docs/                     ← deliverables & write-ups (primer, deck, email, …)
├── analysis/                 ← all working code + signatures + derived data + results
└── _archive_DELETE_ME/       ← intermediates & old drafts — safe to delete
```

> OneDrive blocks file *deletion* from outside, so junk was moved into **`_archive_DELETE_ME/`** rather than deleted. **Delete that whole folder yourself whenever you like.**

---

## papers/
- `s41586-024-07465-2.pdf` — Paper 1 (Gribben/Vallier 2024, the disease cohort)
- `s41586-026-10377-y.pdf` — Paper 2 (Yakubovsky/Itzkovitz 2026, the healthy ruler)

## data/  (raw inputs — keep)
| File | What it is |
|---|---|
| `GSE202379_SeuratObject_AllCells.rds(.gz)` | Paper 1 Seurat object — source of the hepatocytes |
| `combined_scRNAseq_atlas_M5M6M7M8.mat` | Paper 2 snRNA-seq atlas — classifier training cells |
| `zon_struct_all_full.mat` | Paper 2 zonation reconstruction |
| `41586_2026_10377_MOESM1_ESM.zip`, `2025-01-01424E-s1/` | Paper 2 supplementary tables (zonated genes) |
| `Human-liver/` | Paper 2 GitHub repo (landmark CSVs + zonation scripts) |

## docs/  (deliverables & write-ups)
| File | What it is |
|---|---|
| `Spatial_Degradation_of_Hepatocyte_Zonation.pdf` | **the primer / proposal** (22 pp) — read this first |
| `zonation_v4.html` | source of the primer PDF (edit → re-render) |
| `Zonation_Hackathon_Deck.pptx` (+ `.pdf`) | the slide deck |
| `email_to_professor.md` | green-light request (fill in `[names]`) |
| `research_question_options.md` | the original 6 candidate questions (history) |

---

## analysis/  (code + derived data + results)

### Derived data — `analysis/paper1/`
`counts.mtx` (30,117 genes × 69,426 hepatocytes), `genes.txt`, `barcodes.txt`,
`cell_metadata.csv` (cell_type + stage), `metadata_all_cells.csv` (incl. library sizes).

### Signatures (artifact A1)
`pericentral_genes.txt`, `periportal_genes.txt` — 20 + 20 landmark genes.

### Code
| Script | Purpose | Status |
|---|---|---|
| `01_extract_paper1_hepatocytes.R` | R: Seurat `.rds` → `paper1/` (auto-finds the `.rds` under `data/`) | ✅ run |
| `convert_paper2_mat.py` | **Phase 0**: Paper 2 `.mat` → `paper2_train.npz` (Python cache for the classifier) | ready (run once) |
| `pipeline.py` | **Main** Steps 2–8: load→normalize→score→validate→ruler→collapse→DE+FDR→plasticity | ✅ smoke-tested |
| `classifier_step.py` | Step 4b: zone classifier → entropy de-zonation metric (uses `paper2_train.npz` if present) | scaffold |
| `run_p2_validation.py` | Paper-2 positive control | ✅ run |
| `run_all.py` | driver — runs Steps 2–8 in order (+ classifier if `RUN_CLASSIFIER=True`) | ready |
| `build_deck_final.js` | regenerates the slide deck | ✅ |
| `CODING_PLAN.md` | step-by-step build order (Phases 0–10) with acceptance checks | — |
| `README_pipeline.md` | how to run, order, memory notes | — |

### Results so far (feasibility only)
`p2_validation.png` (Paper 2 control), `feasibility_fig.png` (Paper 1 collapse), `RESULTS.txt`, `meta_preview.txt`.
These are sanity checks — the real analysis happens during the hackathon. `out/` is the pipeline's output target.

---

## STATUS — done vs. left

### Done (prep)
- ✅ Question locked + motivated; primer, deck, email written.
- ✅ All data downloaded; Paper 1 hepatocytes extracted; signatures built.
- ✅ Pipeline written + smoke-tested; method validated on real Paper 2 data.
- ✅ **Plumbing complete**: `run_all.py` driver + `convert_paper2_mat.py` (Phase 0).

### Left — prep before Sunday
1. Run `python analysis/convert_paper2_mat.py` once → `paper2_train.npz`.
2. Send the green-light email (`docs/email_to_professor.md`, fill in names).

### Left — the hackathon itself (do live)
3. Step 3 harmonize → Step 4 score + classifier (set `RUN_CLASSIFIER=True`).
4. Steps 5 / 5b validate + ruler battery — **resolve the weak pericentral arm** seen in feasibility.
5. Step 6 collapse curve (donor bootstrap + ordered-trend test, H1).
6. Step 7 zone DE + BH-FDR (H2); Step 8 plasticity link (H3).
7. Optional bonus (Paper 3 enrichment); figures, write-up, presentation.

Full detail + acceptance checks: `analysis/CODING_PLAN.md`. Recommendation: do the *science* live; only the (now-finished) plumbing was worth pre-building.
