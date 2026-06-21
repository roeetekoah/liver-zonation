# CLAUDE.md — Spatial Degradation of Hepatocyte Zonation

Auto-loaded context for every Claude Code session in this repo. Read this first, then
the files under **Read order** before doing anything.

## Project in one paragraph
A 2-day Computational Genomics hackathon project (team: Roee + Shira). We use **Paper 2's
healthy human-liver spatial zonation atlas as a quantitative "ruler"** to assign a
pseudo-zonation coordinate to **Paper 1's spatially-blind disease snRNA-seq hepatocytes**,
then measure how zonation collapses across MASLD stages.
- **H1** — does zonation collapse with disease stage?
- **H2** — which gene programs collapse?
- **H3** — are de-zonated cells also plastic / biphenotypic (hepatocyte→cholangiocyte)?

Prep is done; the hackathon executes the pipeline live.

## Read order (canonical docs)
1. `PROJECT_MAP.md` — the index: folder layout, what's done vs left.
2. `src/IMPLEMENTATION_PLAN.md` — step-by-step build order + acceptance checks.
3. `src/config.py` — paths + signature-set config.
4. `signatures/README.md` — which gene sets, and why `full` is the default.
5. `docs/primers/*.pdf` — 4 method primers (stats H1/H3, DE+FDR, spatial genomics).
6. `docs/WORK_DIVISION.md` — who does what (Roee / Shira).

## Non-negotiable conventions
- **Donor is the unit of inference**, never the cell. ~47 donors (`Patient.ID`) vs ~69k
  cells. Cell-level p-values = pseudoreplication. Resample/bootstrap **donors**, not cells.
- **Signatures:** the `full` transcriptome-wide set (~1273 PC + 364 PP) is the
  **default/primary**. Report every result **both ways** — `full` AND `paper2_landmark`
  (20+20) — as a robustness comparison (`config.SETS_TO_COMPARE`). Agreement is evidence
  the signal is real, not a gene-set artefact.
- **De-zonation ≠ plasticity.** De-zonation = lost *position within* hepatocytes (the
  healthy coordinate is a single broad **unimodal** hump; prove zonation by marker
  *slopes*, not by bumpiness). Plasticity = lost *cell identity* (KRT7/KRT19/SOX9).
  H3 tests whether they co-occur within a donor.
- **H2 circularity guard:** the coordinate is built from these genes, so the "driver"
  test uses a **random held-out gene split, repeated K≈20–50×**, reporting the
  distribution across splits.
- **Multiple testing:** BH-FDR across families of tests; always report **effect size +
  CI** beside every p-value.
- Keep prep deliverables (primers, deck) intact; only build/run **analysis code** now.
- `PCK2` is **pericentral in humans** (human-specific, per Paper 2).

## Current status
**Done:** question locked; data downloaded + converted to `data/processed/`; signatures
built (4 tiers); `pipeline.py` written + smoke-tested (donor-level); positive control
validated on real Paper 2 data.

**Left before live work:**
1. Run `python src/prep/02_convert_paper2_mat.py` once if `data/processed/paper2_train.npz`
   is missing (must be rebuilt with the **full** feature set, not just the 40 landmarks).
2. Execute Steps 3–8 live: harmonize → score + classifier → validate / ruler battery
   (resolve the weak pericentral arm) → collapse (H1) → zone DE + FDR (H2) →
   plasticity (H3).

## Environment notes
- Run Python scripts from `src/` (or put `src/` on `sys.path`); `config.py` resolves all
  paths from the repo root.
- `data/raw/` is large and git-ignored; `data/processed/` is what the pipeline reads.
- Recompile primers with `pdflatex` (twice, for cross-refs); decks are built from JS in
  `src/tools/` with pptxgenjs.
- LaTeX/Python build artifacts (`*.aux/.log/.out/.toc`, `__pycache__`) are disposable;
  keep `.tex` and `.pdf`.

## House style
Be concise and direct (Roee's stated preference). Explanations should be **concrete** —
ground every abstract claim in a small worked example. Verify math/code before claiming
it works; prefer a quick test or rendered check over assertion.
