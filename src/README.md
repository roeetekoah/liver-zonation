# src/ — code

All analysis code. Paths are centralised in **`config.py`** (import it, don't hard-code).
For a verbose, plain-English walkthrough of every step see **`STEPS.md`**; for the build
order + acceptance checks see **`CODING_PLAN.md`**; for the **full implementation spec**
(exact inputs, algorithms, formulas, data shapes per step) see **`IMPLEMENTATION_PLAN.md`**.

## Layout
```
src/
├── config.py            central paths (data/, signatures/, results/)
├── prep/                one-time conversions (raw → processed)  ── "Step 1"
│   ├── 01_extract_paper1_hepatocytes.R     .rds → data/processed/paper1/
│   ├── 02_convert_paper2_mat.py            .mat → data/processed/paper2_train.npz
│   └── 03_build_expanded_signatures.py     supp table → signatures/*_expanded.txt
├── pipeline.py          integrated donor-level analysis, Steps 2–8 (the reference impl)
├── classifier.py        Step 4b: zone classifier → entropy
├── steps/               per-step stubs (step2…step9) — the modular hackathon scaffold
├── plotting/            artefacts.py — one plotting function per artefact (A1,A4,A5,A5b,A6,A7,A8)
├── run_all.py           driver — runs the whole analysis end to end
├── run_p2_validation.py standalone positive control on Paper 2 (already run)
└── tools/               non-analysis utilities (deck builders)
```

## What `run_all.py` and `run_p2_validation.py` are (they confuse people)

**`run_all.py` = the "do the whole analysis" driver.** During the hackathon you run this
one file; it executes Steps 2 → 8 of `pipeline.py` in order on the **disease** data
(`data/processed/paper1/`), optionally turning on the classifier (Step 4b), and writes all
outputs to `results/`. Think of it as the orchestrator / entry point — it doesn't contain
new science, it just wires the steps together and checks the required inputs exist.

**`run_p2_validation.py` = a one-off sanity check on the REFERENCE data, not the disease
data.** It rebuilds the zonation coordinate on Paper 2's *own healthy* hepatocytes and
checks the method recovers known zonation (CYP2E1 rises with the coordinate, ASS1 falls).
It is **separate** from `run_all.py` on purpose: it answers *"does our ruler even work?"*
before we ever trust it on Paper 1. It already ran and produced
`results/figures/p2_validation.png` (the positive-control slide). You normally run it once,
not every time.

So: `run_p2_validation.py` validates the *method* on the reference; `run_all.py` applies the
validated method to the *disease cohort*.

## Run order
```bash
# Step 1 (prep) — once per machine, needs raw data:
Rscript src/prep/01_extract_paper1_hepatocytes.R
python  src/prep/02_convert_paper2_mat.py
python  src/prep/03_build_expanded_signatures.py
# method positive control — once:
python  src/run_p2_validation.py            # -> results/figures/p2_validation.png
# the analysis (hackathon):
python  src/run_all.py                      # Steps 2–8 -> results/
```

## Requirements
```
pip install numpy scipy pandas scikit-learn statsmodels matplotlib h5py openpyxl
```
R side: `Seurat`, `Matrix`.

## Memory / runtime
- `pipeline.py` loads the full `counts.mtx` (~8–12 GB RAM for the real file). Steps 2–6 are
  fast; **Step 7 (pseudobulk DE) is the heavy part** (a few minutes).
- `classifier.py` restricts to the shared landmark feature genes, so it stays light.

## Validation status
`pipeline.py` was smoke-tested end-to-end on synthetic donor data (donor-level collapse,
pseudobulk DE, within-donor plasticity all run with the expected shapes). The scoring track
was confirmed on real Paper 2 hepatocytes — the coordinate recovers zonation
(`results/figures/p2_validation.png`).
