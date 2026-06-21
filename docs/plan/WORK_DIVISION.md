# Work division — Roee & Shira

Two people, two days. We split the project into two complementary tracks that run in
parallel and meet at the per-cell coordinate table (`A4`). Each track owns essential,
substantive parts of the result — the project only works if both land. The split follows
who's picking up which area, and keeps the two sets of files mostly separate so we can work
without stepping on each other. Everything maps to a numbered step, its stub file
(`src/steps/…`), and its acceptance check (`docs/plan/CODING_PLAN.md`).

> How we split it: one track carries the data → coordinate → validation foundation that
> every downstream result is built on; the other carries the donor-level statistics, the
> classifier, and the interpretation guards. The two halves meet at the `A4` coordinate
> table — agree its exact columns early.

---

## Ownership at a glance

| Step | Artefact | Owner | Area |
|---|---|---|---|
| 2 Load + QC sanity | A2 | **Shira** | data ingest, QC, per-donor counts |
| 3 Harmonize genes | A3 | **Shira** | gene-ID mapping, shared-gene set, batch-robust features |
| 4a Signature scoring | A4 | **Shira** | the coordinate itself — mean_z(PC) − mean_z(PP) |
| 4b Zone classifier + entropy | A4 | **Roee** | ML: calibration, OOD handling, entropy meter |
| 5 Healthy validation | A5 | **Shira** | positive control — the go/no-go gate the whole result rests on |
| 5b Ruler-validity battery | A5b | **Roee** | "is the ruler still a ruler" diagnostics |
| 6 Collapse curve (H1) | A6 | **Roee** | donor-level inference, bootstrap, permutation null — headline |
| 7 Zone-resolved DE (H2) | A7 | **Roee** | pseudobulk + interaction model + circularity guards |
| 8 Plasticity link (H3) | A8 | **Shira** (model design with Roee) | scoring + within-donor test; confound control reviewed together |
| 9 Bonus enrichment | A9 | **Roee** (if time) | hypergeometric test + background model |
| Integration / `run_all` / reproducibility | — | **Roee** | end-to-end reproducibility of every number |
| Figures (`src/plotting`), tables, deck, write-up | — | **Shira** | turns the artefacts into the deliverables |

The two tracks are mostly **separate files** (Shira: steps 2, 3, 4a, 5, 8 + plotting; Roee:
steps 4b, 5b, 6, 7, 9 + pipeline integration), so git conflicts are rare. They join at the
`A4` coordinate table — agree its exact columns early (`cell_id, donor, stage,
zonation_coord, pc, pp, plasticity, zone_probs…, entropy`).

---

## Timeline (half-days)

**Prep (already done):** data converted, signatures built, pipeline + stubs written,
positive control validated. See the primer's "What we've already built" page.

**Day 1 — AM**
- Shira: Step 2 (load, QC sanity, per-donor/stage counts) → Step 3 (harmonize). Deliver A2 + A3.
- Roee: stand up Step 4b classifier on `paper2_train.npz`; held-out confusion matrix on Paper 2; decide calibrated logistic vs alternatives.

**Day 1 — PM**
- Shira: Step 4a scoring → produce the `A4` coordinate table; Step 5 healthy validation (the **gate** — must pass before Step 6).
- Roee: apply classifier to Paper 1 (entropy per cell, merge into `A4`); Step 5b ruler-validity battery across stages. **Resolve the weak-pericentral arm seen in feasibility** (widen to `_expanded`, rank features).

**Gate:** do not start Day 2 analysis until Step 5 passes (markers correlate in healthy).

**Day 2 — AM**
- Roee: Step 6 collapse curve (per-donor metrics, ordered-trend test, donor bootstrap CI, label-shuffle null) → **H1**. Then start Step 7.
- Shira: begin figures from A5/A5b/A6 via `src/plotting`; assemble the methods write-up skeleton.

**Day 2 — PM**
- Roee: finish Step 7 pseudobulk DE + interaction + circularity guards → **H2**; review Step 8 confound control with Shira; Step 9 bonus if time; final reproducibility (`run_all`).
- Shira: Step 8 plasticity (within-donor / stage-stratified) → **H3**; final figures, tables, deck, presentation.

---

## Definition of done (per owner)

**Shira** — `A4` coordinate table is complete and documented; the healthy positive control
passes and is plotted; every artefact has a figure from `src/plotting`; the report and deck
carry the real A6/A7/A8 figures with correct captions.

**Roee** — each statistical claim is donor-level, has a CI and a negative control, and
survives the circularity guard (signature genes excluded / held-out split / interaction
test); classifier entropy is calibrated and cross-checked against QC; `run_all` reproduces
every figure from `data/processed` on a clean checkout.

---

## Fallback (if time runs short)

Build the **minimum viable result first, end-to-end**: Step 4a coordinate (Shira) +
Step 5 validation (Shira) + Step 6 donor-level collapse for H1 (Roee). That alone is a
complete, defensible story. The classifier (4b), H2 (7), H3 (8) and the bonus (9) are
layered on top in that order, each independently droppable.

## Logistics
- Git: short feature branches per step, merge to `main` when a step passes its check
  (see `GIT_SETUP.md`). Re-sync `main` after every merge.
- Daily 10-min sync at each half-day boundary; agree the `A4` schema on Day 1 AM.
