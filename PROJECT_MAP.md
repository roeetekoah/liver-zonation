# Project map — Spatial Degradation of Hepatocyte Zonation

The index to this folder: what we have (data, code, signatures, results, deliverables) and what's left.

---

## Folder layout (top level)

```
Hackathon/
├── PROJECT_MAP.md       ← this file (the index)
├── GIT_SETUP.md         ← uni↔home + 2-person git workflow
├── papers/              ← the two source paper PDFs
├── data/
│   ├── raw/             ← original downloads (.rds, .mat, supp tables, P2 repo) — large, git-ignored
│   └── processed/       ← Python-native conversions the pipeline actually reads
├── signatures/          ← pericentral/periportal gene lists (core / expanded / sensitivity) + README
├── src/                 ← ALL code (was "analysis/")
│   ├── prep/            ← one-time conversions (R + .mat→.npz)
│   ├── steps/           ← per-step stubs (step2…step9) — the hackathon scaffold
│   ├── plotting/        ← plotting machinery, one function per artefact
│   ├── pipeline.py      ← integrated donor-level reference (smoke-tested)
│   ├── classifier.py, run_all.py, run_p2_validation.py, config.py
│   └── CODING_PLAN.md, README.md, build_deck_final.js
├── results/             ← figures/ + tables/ (pipeline output target) + feasibility logs
├── docs/                ← deliverables & write-ups (primer, proposal deck, email, work-division)
├── presentation/        ← final-talk plan + starter .pptx + figure assets
└── _archive_DELETE_ME/  ← junk — safe to delete (OneDrive blocks deletion from outside)
```

> Why the rename: `analysis/` had become a "god directory" (code + data + results mixed).
> Code now lives in `src/`, derived data in `data/processed/`, outputs in `results/`.

---

## data/
**`data/raw/`** (keep, git-ignored, large):
| File | What it is |
|---|---|
| `GSE202379_SeuratObject_AllCells.rds(.gz)` | Paper 1 Seurat object (disease cohort) |
| `combined_scRNAseq_atlas_M5M6M7M8.mat` | Paper 2 snRNA-seq atlas → classifier training |
| `zon_struct_all_full.mat` | Paper 2 zonation reconstruction (positive control) |
| `41586_2026_10377_MOESM1_ESM.zip`, `2025-01-01424E-s1/` | Paper 2 supplementary tables |
| `Human-liver/` | Paper 2 GitHub repo (landmark CSVs + MATLAB zonation scripts) |

**`data/processed/`** (what the pipeline reads — built by `src/prep/`):
- `paper1/` — `counts.mtx` (30,117 genes × 69,426 hepatocytes), `genes.txt`, `barcodes.txt`, `cell_metadata.csv`, `metadata_all_cells.csv`.
- `paper2_train.npz` — zone-labelled Paper 2 nuclei (classifier training set).

`data/README.md` explains the raw→processed mapping in detail.

## signatures/  (artifact A1)
Four families per zone (see `signatures/README.md`):
- `*_paper2_landmark.txt` — **the EXACT Paper 2 landmark set (extracted verbatim) → the pipeline's default baseline.**
- `*_core.txt` — curated, biology-informed anchors (derived).
- `*_expanded.txt` — landmark ∪ core ∪ top-ranked genes from Paper 2's snRNA table (≈100).
- `periportal_sensitivity.txt` — inflammation-linked genes removed (H1 robustness check).
PCK2 is placed **pericentrally** (human-specific, per Paper 2). `config.py` defaults to `paper2_landmark`.

## src/  (code)
| Path | Purpose | Status |
|---|---|---|
| `config.py` | central paths (data/processed, signatures, results) | ✅ |
| `prep/01_extract_paper1_hepatocytes.R` | Seurat `.rds` → `data/processed/paper1/` | ✅ run |
| `prep/02_convert_paper2_mat.py` | Paper 2 `.mat` → `paper2_train.npz` | ✅ ready (run once) |
| `pipeline.py` | integrated Steps 2–8, donor-level | ✅ smoke-tested |
| `classifier.py` | Step 4b zone classifier → entropy | scaffold |
| `steps/step2…step9_*.py` | per-step stubs (signature + algorithm + acceptance) | scaffold |
| `plotting/artefacts.py` | one plotting fn per artefact (A1,A4,A5,A5b,A6,A7,A8) | scaffold |
| `run_all.py` | driver (Steps 2–8 + classifier) | ✅ ready |
| `run_p2_validation.py` | Paper-2 positive control | ✅ run |
| `CODING_PLAN.md` | build order, Phases 0–10, acceptance checks | — |

## results/
`figures/` (`p2_validation.png` = positive control, `feasibility_fig.png`), `tables/` (pipeline output target), `RESULTS.txt`, `meta_preview.txt`.

## docs/  (deliverables)
| File | What it is |
|---|---|
| `Spatial_Degradation_of_Hepatocyte_Zonation.pdf` | **the primer / proposal** — read first |
| `zonation_v8.html` | current source of the primer (edit → re-render) |
| `WORK_DIVISION.md` | who does what (Roee / Shira) |
| `Zonation_Hackathon_Deck.pptx` (+ `.pdf`) | the slide deck |
| `email_to_professor.md`, `research_question_options.md`, `ORIGINAL_PLAN_AND_CHANGES.md` | email + history |

## presentation/  (the final ~15-min talk)
| File | What it is |
|---|---|
| `PRESENTATION_PLAN.md` | slide map: pre-made vs stub, 15-min arc, post-hackathon fill checklist |
| `Zonation_Final_Presentation.pptx` (+ `.pdf`) | **starter deck** — green slides done; results slides (9–11), conclusions, some backups are labeled placeholders to fill after the hackathon |
| `assets/` | figure PNGs (rendered from the primer) + the real `p2_validation.png` |

---

## STATUS — done vs. left

### Done (prep) — see the primer's "What we've already built" page
- ✅ Question locked + motivated; primer, deck, email, work-division written.
- ✅ Data downloaded **and converted** to `data/processed/` (Paper 1 hepatocytes; Paper 2 training nuclei).
- ✅ Signatures built (3 tiers, revised).
- ✅ Pipeline written + smoke-tested (donor-level); method validated on real Paper 2 (positive control).
- ✅ Repo restructured; per-step stubs + plotting machinery + `run_all` driver in place.

### Left — prep before Sunday
1. Run `python src/prep/02_convert_paper2_mat.py` once (if `paper2_train.npz` not present).
2. Send the green-light email (`docs/email_to_professor.md`).

### Left — the hackathon itself (do live)
3. Step 3 harmonize → Step 4 score + classifier.
4. Steps 5 / 5b validate + ruler battery — resolve the weak pericentral arm.
5. Step 6 collapse (H1); Step 7 zone DE + FDR (H2); Step 8 plasticity (H3).
6. Optional bonus (Paper 3 enrichment); figures, write-up, presentation.

Full detail + acceptance checks: `src/CODING_PLAN.md`. Split of labour: `docs/WORK_DIVISION.md`.
