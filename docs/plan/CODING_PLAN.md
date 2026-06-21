# Coding plan — input → results → artefacts

A step-by-step build order. Each phase lists: **inputs** (with shapes), **what to code**, **outputs**,
the **artefact** it produces (A1–A9 from the primer), and an **acceptance check** (how you know it's right).
Most of this is already scaffolded in `pipeline.py` and `classifier.py`; this plan says exactly what to
flesh out and in what order. Two people: **A = reference + stats**, **B = disease data + modelling**.

Data-flow in one line:
`raw → [convert] → ruler(A1) + clean P1(A2) → harmonize(A3) → place cells(A4) → validate(A5,A5b) → collapse(A6) → DE(A7) → plasticity(A8) → report(A9)`

---

## Phase 0 — Environment & one-time conversions  *(prep; B)*
**Code**
- `pip install numpy scipy pandas scikit-learn statsmodels matplotlib h5py` (+ `scanpy` optional).
- `convert_paper2_mat.py` (new, ~30 lines): read `combined_scRNAseq_atlas_M5M6M7M8.mat` with `h5py`
  (the chunked CSC reader already in `run_p2_validation.py`), keep hepatocytes, save
  `paper2_hep.npz` = `{expr (cells×genes, float32), genes (str[]), donor (str[])}`.
**Output:** `paper2_hep.npz`. **Acceptance:** `npz` loads in <5 s; shape ≈ (50979, 18129); gene list non-empty.
*(Baseline scoring needs only the signature CSVs — skip this if classifier is deferred.)*

---

## Phase 1 — Build the ruler  *(Step 1 → A1; A)*
**Inputs:** Paper 2 supplementary zonated-gene table (CSV) **or** `Human-liver/Matlab_scripts/Hepatocyte-PC-LM.csv` / `-PP-LM.csv` (already present); for 1c, `paper2_hep.npz`.
**What to code**
1. `load_signatures()` — read the PC/PP gene lists; (optional) extend to top ~50–100 per end by |zone score| from the supplementary table; write `pericentral_genes.txt` / `periportal_genes.txt`. *(done: 20+20 present.)*
2. `plot_reference_profiles()` — for top ~10 genes/end, plot mean expression vs zone index from Paper 2 → confirm opposite monotone gradients.
3. `make_training_labels(paper2_hep)` — assign each Paper 2 nucleus a zone label: either propagate Paper 2's zone index (their repo) **or** the signature-tercile fallback (`derive_labels()` in `classifier.py`). Save `paper2_train.npz = {expr, zone_label}`.
**Output / Artefact A1:** signature lists + profile figure + `paper2_train.npz`.
**Acceptance:** PC and PP gene sets disjoint; profile plot shows PC rising / PP falling along zone; ≥3 zone classes present with reasonable counts.

---

## Phase 2 — Load & QC Paper 1 hepatocytes  *(Step 2 → A2; B)*
**Input:** `paper1/counts.mtx` (genes×cells, 30117×69426), `genes.txt`, `barcodes.txt`, `cell_metadata.csv`, `metadata_all_cells.csv`.
**What to code** (functions already in `pipeline.py: load()`)
1. `load()` — `scipy.io.mmread(...).tocsc()`; attach `stage` (from `cell_metadata`) and `libsize` (`nCount_RNA` from `metadata_all_cells`, aligned by `cell_id`).
2. `qc_sanity()` — confirm kept cells are ALB⁺ (mean ALB > threshold); print per-stage & per-donor counts. (Cell-level QC is inherited; this is a check, not re-filtering.)
3. `normalize_for_scoring()` — for the signature/marker genes only: CP10k → `log1p` → per-gene z (`zrows()` in `pipeline.py`).
**Output / Artefact A2:** in-memory matrix + per-stage/per-donor count table + a QC plot (UMIs/cell, %mito if available, ALB by stage).
**Acceptance:** 69,426 hepatocytes; 5 stages with the known counts (3750/7073/31903/3603/23097); ALB clearly expressed.

---

## Phase 3 — Harmonize genes & batch axis  *(Step 3 → A3; A)*
**Inputs:** A1 signatures + A2 genes (+ `paper2_train` genes for the classifier).
**What to code**
1. `harmonize_ids()` — intersect gene symbols across Paper 1, Paper 2, and the signatures; report mapping rate; drop unmatched.
2. `finalize_features()` — restrict signatures (and classifier feature genes) to the shared set; if a signature drops below ~15 genes, widen top-N in Phase 1.
3. Choose batch-robust representation: z-scored (and/or rank-transformed) features.
**Output / Artefact A3:** harmonization report (CSV/MD: mapping rate, surviving signature sizes) + frozen final gene sets.
**Acceptance:** ≥80% of signature genes survive the intersection; report saved.

---

## Phase 4 — Place every cell  *(Step 4 → A4; A scoring, B classifier)*
**Inputs:** A2 matrix + A3 gene sets (+ `paper2_train.npz` for 4b).
**What to code**
- **4a scoring** (`score()` in `pipeline.py`): `pc = mean_z(PC)`, `pp = mean_z(PP)`, `zonation_coord = pc − pp`. Also compute `plasticity = mean_z(KRT7,KRT19,SOX9,…)`.
- **4b classifier** (`classifier.py`): `StandardScaler` → `LogisticRegression(multinomial)` trained on `paper2_train`; **evaluate on a held-out Paper 2 split first** (confusion matrix); then `predict_proba` on Paper 1 → per-cell `zone_probs` + `entropy = −Σ p·log p`.
- **4c agreement:** correlate the scoring coordinate with the classifier's expected-zone on Paper 1.
**Output / Artefact A4:** `coordinates.csv = [cell_id, donor, stage, zonation_coord, pc, pp, plasticity, zone_probs…, entropy]` + a UMAP coloured by coordinate.
**Acceptance:** Paper 2 held-out classifier accuracy clearly > chance; scoring vs classifier agree (Spearman > ~0.5) on Paper 1.

---

## Phase 5 — Validate on healthy  *(Step 5 → A5; A)*
**Input:** A4 restricted to Paper 1 healthy donors.
**Code** (`validate()` in `pipeline.py`): Spearman(`coord`, marker) for GLUL/CYP2E1 (expect +) and ASS1/HAL (expect −); classifier entropy should be low in healthy.
**Output / Artefact A5:** validation figure + correlation/concordance values.
**Acceptance (gate):** pericentral markers ρ>0, periportal ρ<0 in healthy. **Do not proceed to Phase 6 until this passes** — if it fails, fix scoring (widen signatures, rank-based, revisit normalization). *(In the feasibility run the periportal arm passed but pericentral was weak — this is the first thing to fix.)*

---

## Phase 5b — Is the ruler still a ruler?  *(→ A5b; A)*
**Input:** A4 across all stages.
**Code** (4 diagnostics, per stage):
1. internal coherence — mean pairwise corr within PC genes (and within PP).
2. cross-program anti-correlation — corr(pc, pp) across cells.
3. split-half reproducibility — corr of two coordinates from random half-signatures.
4. program-off vs restriction-lost — track each module's mean magnitude vs the co-expression rate.
**Output / Artefact A5b:** per-stage curves for (1)–(4).
**Acceptance:** all four computed and plotted per stage; you can state *whether* and *how* the ruler degrades.

---

## Phase 6 — Collapse curve (headline)  *(Step 6 → A6; A)*
> **Unit of inference = the DONOR (47 biopsies), not the cell (~69k).** Cell-level
> p-values here are pseudoreplication and are invalid. Compute ONE number per donor,
> then test the trend across stages on those ~47 donor values.

**Input:** A4 + A5/A5b.
**Code** (`collapse()` in `pipeline.py`):
1. **per-donor metrics** — for each donor (≥30 cells): coord **spread** (`std`), marker **anti-correlation** (`spearman(pc,pp)`); optionally classifier-**entropy** mean and axis separability (silhouette/AUC). One row per donor → `collapse_per_donor.csv`.
2. **trend across stages** — Spearman of the per-donor metric vs stage-rank (+ optional **Jonckheere–Terpstra** on the donor values).
3. **donor bootstrap CI** — resample DONORS (not cells) B≈2000× → 95% CI on the trend ρ.
4. **donor-level negative control** — permute the per-donor stage labels B≈2000× → permutation p; the trend must vanish under shuffling.
**Output / Artefact A6:** `collapse_per_donor.csv` + the collapse curve PNG (donor points + per-stage mean, two panels: spread, anti-corr) + ρ, 95% CI, perm-p.
**Acceptance:** trend tested on ~47 donor values (not cells); bootstrap CI excludes 0; shuffled-label perm-p is null (≈0.5). *(Smoke-tested on synthetic donor data: spread↓ ρ≈−0.98, anti-corr→0 ρ≈+0.98, perm-p<0.001.)*

---

## Phase 7 — Zone-resolved DE + FDR (pseudobulk)  *(Step 7 → A7; B)*
> **Pseudobulk, donor-level again.** Aggregate cells to one profile per **donor × zone**,
> then test the stage effect on those aggregates — never per-cell. This is the standard
> fix for the inflated p-values you'd get treating 69k cells as independent.

**Input:** full A2 matrix + A4 coordinate.
**Code** (`de()` in `pipeline.py`):
1. bin cells into portal/mid/central terciles of `coord`.
2. **pseudobulk**: for each zone, build a donor × gene matrix of mean log1p-CP10k (donors with ≥20 cells in that zone; need ≥6 donors).
3. per gene, test the stage effect on the donor aggregates — Spearman vs stage-rank (MVP) **or** the **interaction model** `expression ~ coord + stage + coord×stage` (the cleaner H2 test: does the *gradient itself* change with stage?).
4. `statsmodels.multipletests(method='fdr_bh')` → q; threshold q<0.05; keep effect sizes.
5. **circularity guard**: flag `is_signature` genes (the ones that *built* the ruler) and report the significant count BOTH including and EXCLUDING them; "driver" claims use only non-signature genes; optionally a held-out gene split.
**Output / Artefact A7:** `de_portal.csv`, `de_central.csv` (gene, rho/effect, p, q, is_signature) + volcano plots + shortlist of collapsing programs (signature genes marked).
**Acceptance:** q-distribution sensible; significant set survives EXCLUDING signature genes; counts reported per zone with donor n. *(Smoke-tested: ~16–17 non-signature genes q<0.05 per zone on synthetic data.)*
**Runtime note:** pseudobulk collapses to ~47×G — fast; the per-donor matrix build over all genes is the only heavy part (chunk if needed).

---

## Phase 8 — De-zonation ↔ plasticity  *(Step 8 → A8; A)*
> **Confound warning:** both de-zonation and plasticity rise with disease stage, so a
> pooled cell-level correlation is guaranteed to look positive for the wrong reason
> (stage drives both). Test **within donor/stage**, or regress stage+donor out.

**Input:** A4 (`coord`, `entropy`, `plasticity`).
**Code** (`plasticity()` in `pipeline.py`):
1. de-zonation proxy = distance of `coord` from the middle (or high classifier entropy).
2. **within-donor** Spearman(de-zonation, plasticity) per donor → report the mean and the % of donors with ρ>0 (this is the confound-free version).
3. **regression** `plast ~ dez + C(stage) + C(donor)` (OLS); the `dez` coefficient is the effect after removing stage and donor — report its sign and p.
4. FDR if several plasticity signatures are tested.
**Output / Artefact A8:** figure + within-donor statistic + the regression coefficient linking lost zonal identity to gained plasticity.
**Acceptance:** within-donor (not pooled) test runs; effect direction + p reported honestly (positive or null); the stage confound is explicitly controlled. *(Smoke-tested: within-donor mean ρ and the `dez` coefficient both report cleanly.)*

---

## Phase 9 — Optional bonus (Paper 3)  *(stretch; A)*
**Input:** A7 significant gene list + Paper 3 risk-variant target-gene list (from its supplement).
**Code:** `scipy.stats.hypergeom` / Fisher exact on the overlap vs a matched background; BH-correct.
**Output:** enrichment p/q + a short table. **Acceptance:** background well-defined; result stated with caveats.

---

## Phase 10 — Results → artefacts (assembly)  *(→ A9; both)*
Turn the per-phase outputs into the final deliverables:
- **Figures:** A5 (validation), A5b (ruler diagnostics), A6 (collapse curve — the money figure), A7 (volcanoes), A8 (plasticity). Consistent palette/labels.
- **Tables:** A3 (harmonization), A4 (`coordinates.csv`), A7 (`de_*.csv`).
- **Code repo:** the scripts + a top `run_all.py`/Makefile that executes Phases 1–8 in order; `requirements.txt`; seed fixed for reproducibility.
- **Write-up / slides:** drop the real A6/A7/A8 figures into the deck and the report; state H1–H3 outcomes with their stats.
**Artefact A9:** reproducible repo + methods write-up + final figures.
**Acceptance:** `run_all` reproduces every figure from raw inputs on a clean checkout.

---

## Build order & ownership (quick reference)
| When | A (reference + stats) | B (disease data + modelling) |
|---|---|---|
| Prep | Phase 1 (ruler, A1) | Phase 0 convert; Phase 2 (QC, A2) |
| Day 1 AM | Phase 3 (harmonize, A3) | Phase 4 scaffold (scoring) |
| Day 1 PM | Phase 5 + 5b (validate, A5/A5b) | Phase 4 finish (classifier 4b, A4) |
| Day 2 AM | Phase 6 (collapse, A6) | Phase 7 (DE+FDR, A7) |
| Day 2 PM | Phase 8 (plasticity, A8) + figures | Phase 10 (assembly, A9) + Phase 9 if time |

**Critical path:** Phase 5 must pass before Phase 6. Everything after Phase 4 depends on a trustworthy coordinate.
