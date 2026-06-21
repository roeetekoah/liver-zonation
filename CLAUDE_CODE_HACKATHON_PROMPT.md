# Prompt for Claude Code — HACKATHON build (the live analysis)

Paste into Claude Code at the repo root once prep is done (data cached, env ready — see
`CLAUDE_CODE_PREP_PROMPT.md`). This is the *substantive* work: turn the scaffold into defensible
results. Work in stages; **stop at each acceptance check and report** before moving on. Commit per stage.

**Read first:** `CLAUDE.md`, `docs/plan/IMPLEMENTATION_PLAN.pdf`, `signatures/README.md`,
`src/config.py`, `src/pipeline.py`, `src/classifier.py`.

**Non-negotiable constraints (every stage):**
- The **donor** (~47) is the unit of inference, never the cell (~69k). No cell-level p-values as headline.
- Run the coordinate + gate + H1 for **both** sets in `config.SETS_TO_COMPARE` (`full` primary, `paper2_landmark` audit).
- The **classifier is integral**, and must be **non-circular** (see Stage 2).

These five gaps (vs the current monolith) are the priority — fix them in order:

### Stage 1 — Step 5 must be a real GATE (not just logging)
`pipeline.validate()` currently only prints marker correlations. Make it:
- compute, on Paper-1 **healthy** donors, ρ(coord, marker) for pericentral (CYP2E1, CYP1A2, GLUL, PCK2)
  and periportal (ASS1, ALDOB, PCK1, HAL);
- **return a PASS/FAIL** (pass = pericentral ρ>0 AND periportal ρ<0) and **write `validation_<set>.csv`**;
- in `run_all`, **block Step 6 if it fails** (per set).
*Acceptance:* returns a boolean per set; `validation_<set>.csv` exists; pipeline halts H1 on FAIL.

### Stage 2 — Classifier + entropy done right (Step 4b)
First rebuild `paper2_train.npz` (it now uses Paper 2's eta labels). Then in `classifier.py`:
- **Exclude the 20+20 landmark genes from the feature set** (train on the other zonated genes / shared
  HVGs) — labels come from those genes, so keeping them is circular. (Or run exclusion as a sensitivity.)
- **Calibrated** multinomial logistic (`CalibratedClassifierCV`), not raw `LogisticRegression`.
- **Held-out Paper-2 split, stratified by donor**: report accuracy + confusion matrix; must beat chance (1/3).
- Apply to Paper 1; write per-cell entropy **with `donor` and `stage` columns** (currently missing donor).
- Delete/curate the slow-path tercile `derive_labels` fallback so it can't silently reintroduce circular labels.
*Acceptance:* held-out accuracy printed and > 1/3; `classifier_entropy.csv` has `donor`; healthy entropy low.

### Stage 3 — H1 collapse consumes entropy too (Step 6)
`pipeline.collapse()` uses spread + PC–PP anticorrelation. Add **per-donor mean entropy** as a third
metric. Keep: Spearman + Jonckheere–Terpstra, donor bootstrap CI, label-shuffle null. Run for both sets.
*Acceptance:* `collapse_per_donor_<set>.csv` has spread, anticorr, **entropy**, plus ρ/CI/p/perm-p per metric.

### Stage 4 — H2 as zonal-slope loss, not just DE (Step 7)
The current donor×zone pseudobulk DE is fine as a *secondary* view. Add the **primary** H2:
- per donor, per gene, fit the **zonal slope** β_d (expression ~ coordinate within that donor's hepatocytes);
- test whether β_d **weakens with stage** across donors (e.g. Spearman β_d vs stage rank, or the
  `expression ~ coord + stage + coord×stage` interaction);
- guard circularity with the **repeated held-out gene split** (build coord on half the genes, test the
  other half, K≈20–50×); BH-FDR across genes.
*Acceptance:* a per-gene "zonal-slope-vs-stage" table with q-values; held-out split repeated; signature
genes excluded or flagged.

### Stage 5 — H3 with honest donor-level inference (Step 8)
Keep the within-donor dez~plast correlations (good). For the pooled model:
- `plast ~ dez + C(stage) + C(donor)` with **donor-clustered standard errors** (or a mixed model),
  OR explicitly treat the cell-level OLS p-value as **descriptive only**;
- headline inference = the **distribution of per-donor rhos** (sign test / Wilcoxon vs 0).
*Acceptance:* donor-level rho summary + clustered/permutation p; any cell-level p clearly labeled descriptive.

### Stage 6 — figures + write-up
Make `src/plotting/artefacts.py` render every artefact (A4, A5, A5b, A6, A7, A8) from real outputs;
assemble the results into the deck/primer figures.

**At the end:** report per hypothesis — the effect size, CI, and negative-control result — and which
signature set led on the validation battery. Flag anything that did **not** pass its acceptance check.
