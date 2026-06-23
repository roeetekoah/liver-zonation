# Claims ledger — audited, one finding at a time

_Purpose: a single source of truth for every finding, so nothing relies on memory. We go through items
one by one (the lead raises an item; the assistant re-verifies it against the actual script/table/data —
not recall; we agree on a status and the grounding; it is written here). Started 2026-06-23._

## Status legend
- **LIVE** — current, grounded, holds as stated.
- **REVISED** — still holds but in a changed form; note what changed and why.
- **FALSIFIED** — turned out wrong / retracted; note what superseded it.
- **STALE** — from an old run or method we no longer use; superseded by the fresh pass.
- **OPEN** — raised, not yet resolved / needs an analysis to settle.

## Entry format
Each entry records: the claim (as stated), STATUS, the grounding (script + table/data + key numbers,
re-verified live), and notes from the discussion (incl. what changed if REVISED/FALSIFIED/STALE).

---

<!-- Entries are appended below as we go through them, in the order raised. -->

## Item 1 — The alternative-explanations framework (count / condition / define, not regress)
**STATUS: LIVE (framework); per-row verdicts below.** Born from the professor critique; reframed the
confounder section as structural, not correlational. Re-verified per row against the files:

| row | alternative | status | grounding (verified) |
|---|---|---|---|
| 1a | PC cells **depleted**, not turned off | LIVE | PC-anchor % by stage flat/non-monotone 36/19/23/22/21 (F0–F4). `load_bearing.py` |
| 1b | …condition on still-PC cells, check **level** (dimming) | **FALSIFIED** | within-PC detox 12.7→8.9 first, then overturned genome-wide (all detox FDR>0.79). `dge_genomewide.py` |
| 2 | **Explant ischemia degrades zone-3 RNA** (housekeeping vs identity) | **OPEN — queued** | the specific housekeeping-retained-vs-identity-lost test was never run; handled structurally instead. See OPEN queue. |
| 3 | **Batch**: end-stage = one run | LIVE | `manuscript.expt`="CG" for all 47 donors; `orig.ident` per-sample, nested in donor → not separable. `raw_counts.py` (F) |
| 4 | **Cell-count imbalance** inflates spread | LIVE | depth-match downsampling B∈{1000,1500,3000} + per-donor N; pattern holds, MC SD 0.006–0.010. `census*.py`, `load_bearing.py` |
| 5 | **Ruler broke → fake de-zonation** (ruler-free anti-corr) | REVISED | anti-corr measured (`legacy_simpson.py`) but is itself aggregation-confounded (Simpson); clean ruler = depth-matched counts. |
| 6 | **"End-stage" ≠ F4** | LIVE | end-stage = 5 explant donors (Disease.status), distinct from 4 NASH-cirrhosis biopsies, though **both carry fibrosis score F4**. Our "biopsy F4 (n=4)" = the NASH-cirrhosis needle biopsies. metadata crosstab. |

## Item 2 — Lobe sampling: zonation pattern is lobe-invariant; primary analysis is right-lobe-only
**STATUS: LIVE (caveated).** Full write-up + numbers: [`findings/lobe_invariance/`](findings/lobe_invariance/README.md)
(data `findings/lobe_invariance/lobe_invariance.csv`, reproduced by `src/analysis/lobe_invariance.py`).
- Within end-stage explants the zonation **detection** pattern is lobe-invariant (R/C/L); e.g. GLUL frac
  0.350/0.343/0.297, ALDOB 0.821/0.837/0.838. The pattern is fully present in **Right-lobe-only** cells →
  caudate/multi-lobe sampling does **not** manufacture the de-zonation signal.
- **Caveat:** absolute burden has moderate per-lobe spread (median ≈0.36) — "invariant" applies to
  detection/pattern, not exact level.
- **Scope:** clears only the *lobe* sub-confound, NOT the explant-vs-biopsy sampling-mode confound.
- **Right-lobe-only restriction CONFIRMED:** `raw_counts.py:78` builds the right-lobe-only primary result;
  downstream anchor-classification/DE use needle-biopsy donors = right-lobe by construction.
- **Provenance note:** the earlier inline lobe table (GLUL 0.43/0.43/0.33 …) used an unsaved, ambiguous
  metric and is **not reproducible** — discarded for the defined frac/UMIs-per-10k table above.
- **Caudate documented** (anatomy + sampling relevance) in the finding README.

## Item 3 — Stress-by-sampling confound (IEG+HSP), robust + exact per-donor
**STATUS: LIVE.** Write-up + numbers: [`findings/stress_and_panel_by_stage/`](findings/stress_and_panel_by_stage/README.md)
(`stress_per_donor_alllobe.csv`, `per_group.csv`; scripts `panel_by_stage.py`, `stress_exact.py`).
- Stress module (8 IEG+HSP genes), **depth-matched mean UMIs/nucleus, mean across donors**: needle biopsy
  **0.074** (38 d), healthy deceased-donor **0.282** (~3.8×, 4 d), end-stage explant **1.675** (~22.6× biopsy,
  ~6× healthy, 5 d). Ambient-robust det2: 0.053 / 0.247 / 0.770. Exact per-donor in the CSV (no medians).
- **Correction:** all 4 healthy = deceased-donor organ tissue; the old "2 surgical + 2 atlas" was WRONG (no
  atlas). Provenance of old FOS/JUN by-stage table: it was **raw** (not SCT) but used deprecated metrics
  (raw mean + ≥1 detection). **The genes are KEPT — only the metric was upgraded** (det2 + depth-matched);
  nothing about FOS/JUN/HSP was discarded. Per-program (IEG/HSP/HIF) breakdown across cell types in Item 6.

## Item 4 — End-stage gene SHAPE is selective, not a "turn-off" (same data as Item 3)
**STATUS: LIVE (descriptive of the explant phenotype; confounded — not disease).**
- Ambient-robust det2 by stage (right-lobe): CYP2E1 0.81→**0.33** & SLCO1B3 0.57→**0.28** (detox DOWN);
  GLUL 0.07→**0.14**, CYP3A4 0.31→**0.41** (PC identity RETAINED/up); PCK1 0.15→**0.58**, ALDOB 0.55→**0.70**
  (periportal INDUCED) — all the movement is the end-stage jump; flat across biopsy stages. The legacy
  "pericentral turns off" reading is **wrong**. Lobe-invariant (Item 2), so not a caudate artifact.
- **IMPORTANT CAVEAT (to cover later):** this is a **group-MEAN shape that masks total per-donor
  heterogeneity** — the 5 explants go in different directions (CL104 retains PC ~50%; CL16 collapses to PP,
  PP:PC≈20; CL18 co-expression explosion 22%). The "selective shape" is a pooled average; the per-explant
  reality is 5 discordant phenotypes (see `load_bearing_donor_table.csv`, `review_checks.py`).

## Item 6 — Cross-lineage stress, segmented IEG/HSP/HIF (robust)
**STATUS: LIVE.** [`findings/stress_celltype_segmented/`](findings/stress_celltype_segmented/README.md)
(`per_donor.csv`, `by_lineage.csv`; `stress_celltype_segmented.py`). Depth-matched mean UMIs/cell,
explant/biopsy fold: **IEG** hep 18.5× ≈ **endothelial 18.2×** (organ-wide, no-zonation cell equally
stressed); **HSP** 66× hep (also high in healthy endo/stellate); **HIF** only 1.7–2.6× → signal is **acute
handling, not chronic hypoxia**. Stress = IEG+HSP (acute); HIF held separate by design.

## Item 7 — NAS components vs detox: the cytokine-CYP-suppression mechanism test
**STATUS: QUARANTINED (lead flagged not-understood; talk-down queued O6 — DO NOT CITE).**
[`findings/nas_components_detox/`](findings/nas_components_detox/README.md) (`nas_components_detox.py`).
Numbers (reproducible, held out of conclusions): within 38 biopsy donors, detox (depth-matched UMIs/cell)
vs NAS components — Inflammation ρ=−0.19 (p=0.26, n.s.); Ballooning ρ=−0.42 (p=0.008); Steatosis −0.30;
Fibrosis −0.32; partial(detox, infl|fibrosis)=−0.10. The inflammation-n.s./ballooning-significant split is
confusing → discuss before any use.

## Item 8 — Integrated donor-level PC-anchor classification (screenshot 1), scales documented
**STATUS: LIVE.** [`findings/integrated_census/`](findings/integrated_census/README.md) →
`load_bearing_donor_table.csv` (`load_bearing.py`). Folds depletion (PC_n), co-expression (dual2_n, ≥2
ambient-robust), turn-off (null_n), stress, source, F, NAS — counts out of depth-matched N_thin (B=1500).
Biopsy PC-anchor% 36/19/23/22/21 (F0–F4), flat/non-monotone; explants heterogeneous. The screenshot's
"detox within PC" column = early `census.py`/`v2` **relative metric (DEPRECATED)**, not part of this
count-based canonical anchor-classification.

## Item 9 — UMIs/10k denominator concern (screenshot 4), closed
**STATUS: LIVE (concern addressed).** `src/analysis/umi10k_validation.py`. The worry (ALB/dominant-gene
share drift inflates per-10k of everything else) is **empirically minor here**: ALB share ≈ 0.004 (0.4% of
nuclear UMIs) and FLAT across F0–F4 (Spearman +0.16, p=0.34 n.s.); TTR ns; APOA1 drifts but share ≈ 0.0003
(negligible). And the robust fix is already used everywhere: **depth-matched ABSOLUTE counts** (binomial
thinning, no denominator). So the claim wasn't lost — it was superseded by method and is now closed.

## Decision D1 — End-stage is analyzed SEPARATELY from the F0–F4 biopsy axis (screenshots 2–3)
**STATUS: LIVE (standing methodological decision).** End-stage = procurement artifact, excluded from the
disease axis and treated as a separate, caveated contrast. For the F0–F4 biopsy axis, the real conclusions
come from the **later in-depth analyses** (depth-matched anchor-classification, all-sets anchor-classification, genome-wide DE) — the
early screenshot tables are HIGH-LEVEL only; do not draw final F0–F4 conclusions from them.

## Note N1 — On the screenshot-5 "relaxations" (flat vs mild attenuation; GLUL caution)
Reasonable, **not panicky**, and to be presented with the data not as hedges: (a) "flat vs mild detox
attenuation" — report donor-level RANGES and let them speak; the honest read is a subtle dim within
donor-to-donor noise (and see the quarantined ballooning link, F6). (b) GLUL is dropout-prone in snRNA —
already handled by anchoring on CYP3A4 too and the 1-of-2 / sensitivity-grid rule; no independent
"identity-preserved" claim rests on GLUL alone.

## Note N2 — Binomial-thinning budget
The B-sweep WAS run for the headline co-expression endpoint: `review_checks.py:75` loops
`B ∈ {1000,1500,3000}` (conclusion B-robust). Newer descriptive tables (panel_by_stage, stress_*) use a
fixed **B=1500**; a B-sweep on those is optional (queue O7 if wanted).

## Item 5 — Right-lobe-only raw-panel tables (provenance)
**STATUS: LIVE (superseded for conclusions by the robust rebuild, Items 3–4).** `src/analysis/raw_counts.py`
→ `results/tables/analysis/rawA_donor_lobe_stage_gene.csv`, `rawA_donor_stage_{alllobe,right}.csv`,
`rawF_qc_source.csv`. Metrics = `frac_raw_pos` (≥1 detection) and `UMIs_per_10k` — **both deprecated**; kept
for provenance. Note F1 (lobe) was computed from `rawA` and inherits the pre-robust metric caveat.

---

## Decision D2 — DROP the detox-module story (lead call, screenshot 2)
**STATUS: standing decision.** The "biopsy-internal detox attenuation" is **dropped as a finding** — it is
confounded, not genome-wide robust (Item 1b FALSIFIED), tied to ballooning (Item 7 QUARANTINED), and not
interesting. How it slipped in: when the structural anchor-classification came up flat, the within-PC detox dip was the
only thing that twitched and got over-promoted into a §4 story. **Detox genes (CYP2E1/CYP1A2/ADH4/AKR1D1/
SLCO1B3) are kept ONLY as pericentral markers** (in the anchor-classification and the end-stage descriptive shape, where
detox-down is part of the explant phenotype). Remove the standalone detox-attenuation narrative from the
write-up. (Affects MANUSCRIPT §4 — doc-debt.)

## Decision D3 — Claim: "hepatocyte GENE-EXPRESSION zonation signal is preserved across biopsy MASLD F1→cirrhotic F4" (lead call, screenshots 2 & 5)
**STATUS: standing decision.** We DO make the positive claim, scoped to **gene-expression (transcriptional)
zonation** — grounded in converging positives, NOT the MDE: sensitivity-grid-robust flat anchor-classification (F8),
all-sets invariance 2→1,637 genes (F1), genome-wide flatness (FDR>0.79), retained GLUL/CYP3A4 identity,
dual = ambient soup collapsing at ≥2 UMI (F8), and the depth-matched donor-balanced polarization figure
(F9: poles retained, no collapse to a single pole as in explants).
The three objections to "preserved" (screenshot 5), weighed:
- **(1) Pseudoreplication** (F4 donor #22 = 59% of cells) — **DEFUSED**: inference is donor-level (n=4
  donors at F4, not 10k cells); the F9 figure is donor-balanced (≤300/donor). Cell counts are visualization only.
- **(2) MDE / power** — **QUESTIONED / demoted**: it bounds only the thin extremes (F0 n=2, F4 n=4); the
  well-populated interior F1–F3 (n=8/12/12) is flat and adequately powered. MDE is a footnote-bound, not a
  reason to retract the positive claim.
- **(3) Biopsy can't see lobule architecture** — **REAL, KEEP as the caveat**: snRNA measures per-cell
  transcriptional balance, not lobule geometry; needle cores miss septa/perivenular zones. So we claim the
  **gene-expression** signal is preserved; we do **not** claim spatial/architectural preservation.
So: keep "gene-expression zonation signal preserved" + the explicit architecture caveat; drop the
over-cautious "no detectable change / never say preserved." (Affects MANUSCRIPT abstract/§2/Discussion — doc-debt.)

## Item 10 — Anchor-classification sensitivity-grid robustness (screenshot 1) → F8
**STATUS: LIVE.** [`findings/census_robustness/`](findings/census_robustness/README.md). PC-anchor flat in
every variant (GLUL-only/CYP3A4-only/both, k∈{1,2}, 2-of-4/3-of-4, ALDOB in/out, CPS1, strict-identity);
**dual co-expression = ambient soup**: k=1 ≈ 0.07–0.10 → k≥2 ≈ 0.002–0.006 (collapses), real co-expression
~0; null flat. This is the positive backbone of D3. Reproducible: census*.py, review_checks.py.

## Item 11 — Scenario-enumeration taxonomy (screenshot 3) — the systematic-coverage leg
**STATUS: LIVE (framework); coverage complete.** Enumerate the full de-zonation space, map each to a
count signature, check coverage (the discipline that stops ad-hoc metric-fishing). Coverage now:
depletion ✔ flat; dimming ✔ (detox — DROPPED per D2); co-expression ✔ flat every B/threshold; **gradient
compression ✔ FILLED** (polar/zonal-extreme fraction flat across F — `all_sets_census.csv`, was the open
GAP in SS3); turn-off ✔ flat; composition ✔ PP:PC ~flat; induction ✔ PP induced explant-only; preserved
✔ = the null. (Manuscript Table 2 is this taxonomy.)

## Item 12 — The null extends THROUGH cirrhotic biopsy tissue, not just pre-cirrhosis (screenshot 4)
**STATUS: LIVE (important clarification).** Our biopsy axis F4 = **NASH-with-cirrhosis needle biopsies
(n=4)** — i.e. we tested into ESTABLISHED cirrhosis (biopsy-sampled, not explant). So the accurate claim is
"no detectable structural change through F4 / cirrhotic biopsy tissue" — NOT "only pre-cirrhotic livers
stay zonated." (Caveat: F4-biopsy n=4.) This makes the null more informative: if zonation broke with
cirrhosis, F4-biopsy is where it would show, and it doesn't. Do not let "pre-cirrhotic only" into the write-up.

## Item 13 — Why the relative z-ruler is abandoned even biopsy-only (meta-analysis) → F12
**STATUS: LIVE.** [`findings/relative_ruler_postmortem/`](findings/relative_ruler_postmortem/README.md). Two
separate reasons: (1) tissue-source confound (fixed by excluding healthy+end-stage — the biggest fix; a
Simpson/aggregation effect, `legacy_simpson.py`); (2) INTRINSIC — even biopsy-only the z-ruler is
depth/cell-number-sensitive AND conflates mechanisms (turn-off/de-zonation/noise all shrink spread). The
weak biopsy "detox drift" 66→49 was within-donor spread noise, didn't survive the count anchor-classification. → the count
anchor-classification, not the ruler, is the trustworthy instrument.

## Item 14 — 2D joint-count "amount" view: correction → F13
**STATUS: LIVE (with correction).** [`findings/joint_count_2d/`](findings/joint_count_2d/README.md). The
broad-program 2D (`census_2d.py`) is a **pole-collapse** visual, NOT a co-expression test: both broad
programs are on in normal hepatocytes (both-high ~83% biopsy vs 43% explant — explant LOWER because it
collapsed to PP-pole). The screenshot's "both-high corner fills in explant" reading is **wrong** for these
genes. The clean high-amount co-expression conviction is the **anchor ≥2 dual (F8): 0.4% biopsy vs 2.9%
explant**. (Manuscript Fig-2 caption "collapses to PP-pole" is correct.)

## Note N3 — End-stage stress-literature + the honesty boundary (re-affirmed, important)
The end-stage exclusion's literature grounding (F2, memory `stress-exclusion-literature`): dissociation/
warm-ischemia IEG+HSP artifact [van den Brink 2017; O'Flanagan 2019; Denisenko 2020]; zonation = O2 +
Wnt/Rspo gradient from central-vein endothelium, pericentral CYP/ADH most perfusion-sensitive [Kietzmann
2017]. **Honesty boundary (keep):** there is **no single-cell paper showing IEG induction directly switches
off GLUL** — so frame as *general artifact [1–3] + perfusion-zonation plausibility [4] + our suggestive
within-explant dose-response (3/5 donors, `review_checks.py`)*, **never as proven causation**. The exclusion
does **not** need the causal claim — the perfect stage⟂tissue-source **collinearity carries it**.

## OPEN queue (raised, not yet run — do NOT treat as findings)
- **O1 — Explant ischemia: housekeeping-retained vs identity-lost test** (alt-explanation row 2). Within
  explant PC cells, do housekeeping genes stay while identity genes drop (selective loss = biology) or do
  both drop together (global degradation = technical)? Never executed; flagged "killer, definitional."
- **O2 — Why is stress high in both deceased-donor groups but ~6× higher in end-stage than healthy?**
  Both are deceased-donor procurement (ischemia/dissociation) → baseline stress; end-stage sicker/longer
  ischemia → much higher. Needs procurement-time data (absent here) or ischemic-time↔IEG/HSP literature.
- **O3 — Optional robust re-run of the full per-gene fraction-by-stage table** with det2 + depth-matching
  across ALL panel genes (partly done in Items 3–4 for key genes; extend if we want the complete table).
- **O4 — NAS as a disease axis (recover what it was for).** Inflammation→detox done (Item 7). Still to do:
  run the zonation/anchor-classification endpoints (PC-anchor, dual, null, gradient) against NAS and its components within
  biopsies, as the histology-graded second axis (orthogonal to fibrosis), per the screenshot-1 pivot.
- **O5 — VERIFY + EXPAND the strong claim "end-stage isn't zonation, it's cytokine/cholestatic CYP-
  suppression."** Argument: GLUL (β-catenin master) retained while bystander CYPs/ADHs fall; the collapsing
  set = classic cytokine-suppressed drug-metabolism module (HNF4A/PXR/CAR/RXRα; IL-6/TNF). This is a strong,
  potentially major finding ("not de-zonation but X" >> "could be non-zonation"). Needs: biological-reviewer
  vetting; check nuclear-receptor/cytokine genes (HNF4A, NR1I2/PXR, NR1I3/CAR, RXRA, IL6, TNF) — extract if
  absent from panel; expand beyond the 5-gene detox set. NOTE Item 7 (biopsy inflammation n.s.) already
  argues against the inflammation version — weigh it. Do NOT assert until vetted.
- **O6 — Talk-down on the detox↔NAS result (Item 7 / F6), which is QUARANTINED.** Walk through why
  inflammation is n.s. but ballooning is significant (collinearity? n=38? metric? real injury signal?),
  and decide if/how to use it. Until then it is not a finding.
- **O7 — RESOLVED for stress** (fold B-robust 21–22.6× across B=1000/1500/3000; documented in F2). Other
  descriptive tables: not needed unless a specific conclusion looks B-sensitive.
- **O8 — DONE (F10):** Paper 1's de-zonation snRNA leg = marker-correlation + Welch's t-test over all 47
  donors (confounded); claimed at transcriptional + protein level; headline is plasticity. We correct only
  the snRNA/transcriptional leg.
- **O9 — Confounder-literature review (queue).** Curate + verify the on-point citations for the confound
  hazard: **Leek et al., "Tackling the widespread and critical impact of batch effects," Nat Rev Genet
  11:733 (2010)** (the strongest, most direct — technical-variable-confounded-with-biology → spurious
  findings); **Simpson's paradox** (conceptual root: conditioning on a confounder can create/invert/erase an
  association); **Hicks et al., Biostatistics 2018** (scRNA-specific: detection rate depends on depth —
  supporting). For the Methods/Discussion.
- **O10 — (optional) clean anchor-based 2D joint-count figure** (F13): rebuild on strict anchors at ≥2 UMI
  so the high-amount co-expression corner (empty in biopsy, fills in explant) is shown directly, replacing
  the misleading broad-program 2D as a co-expression visual.
- **O11 — Deepen the per-donor END-STAGE analysis** (F14 is not exhausted). Build a per-explant INTEGRATED
  profile (anchors + stress + biliary/transdiff + QC/depth + within-explant dose-response in one view); test
  the **between-explant** question — does each organ's collapse magnitude track its procurement-stress
  severity (CL16 most-collapsed = most-stressed? CL104 retains-PC = least?); per-explant biliary/transdiff.
- **O12 — DONE → F16** ([`findings/equivalence_bound/`](findings/equivalence_bound/README.md),
  `src/confound/equivalence_bound.py`). Affirmative equivalence (TOST, 90% CI, donor-level anchor fractions):
  across biopsy F1→cirrhotic-F4 we **EXCLUDE a coordinated PC-anchor shift larger than ≈ ±0.15–0.19** (interior
  F1→F3 tightens to **≈ ±0.12**). **Honest limit:** a *modest* ≤±0.10 drift is NOT excluded (donor SD too large
  at n=4); we rule out *large/dramatic* re-zonation (explant-collapse scale), not subtle change. This converts
  D3 from "nothing significant" into a quantified exclusion bound; it bounds donor-level STRUCTURE, not per-gene.

## Item 15 — Affirmative equivalence bound for "zonation preserved" → F16
**STATUS: LIVE.** See O12 (done). Strengthens **D3**: the preservation claim now has an affirmative form
("we exclude a coordinated re-zonation larger than ±0.12–0.19 across biopsy F1→cirrhotic F4"), honestly
bounded (modest ≤10% drift not excluded). The companion to the descriptive null (F8/F1/F9/F15).

## Item 16 — Plan A genome-wide discovery DGE (edgeR pseudobulk) → F18
**STATUS: LIVE.** [`findings/dge_plan_a/`](findings/dge_plan_a/README.md). Pseudobulk per donor (raw UMIs,
hepatocytes) → edgeR TMM + negative-binomial quasi-likelihood (robust), 38 biopsy donors, 21,022 genes;
primary F4-vs-F1. **Zonation flat** (GLUL FDR 0.43, all detox FDR>0.79 → reproduces D3 with edgeR);
**housekeeping flat** (normalization sound). **64 hits = a biliary/ductular program** (EPCAM/GRHL2/SPINT2/
SOX4/SOX9 + CXCL10). Cross-lineage burden: every headline gene 7–78× cholangiocyte-dominant; cholangiocyte
fraction rises to ~8.3% at F4 (ductular reaction) → the F4 "rise" is compositional spillover, not hepatocyte
transdifferentiation. decontX: hits 64→34, SOX4/SOX9 drop below significance (ambient), EPCAM/B3GNT3/SPINT2/
CXCL10 survive. **Not hepatocyte-intrinsic; not a refutation of their imaging.** Paper 1 used NO ambient tool
and only a crude >50,000-count doublet filter.

## Item 17 — Plan B within-class DGE → F20
**STATUS: LIVE.** [`findings/dge_plan_b/`](findings/dge_plan_b/README.md). Classify each biopsy hepatocyte
PC/PP/null/dual by ≥2-UMI anchors, pseudobulk within class, edgeR F4-vs-F1. **0/13 zonation genes significant
in every class.** The only program is the same biliary set (GRHL2/EPCAM/SPINT2) across ALL four classes =
**class-agnostic**. Honest logic (corrected after adversarial review): class-agnosticism rules out a
*zone-specific* program but does NOT by itself separate "uniform ambient" from a "uniform pan-zonal program"
— **corroborating, not decisive**; the decisive weight is the cross-lineage burden (F18) + per-cell
co-expression ≤0.4% (F8).

## Item 18 — Doublet chase: residual decontX survivors are not hepatocyte-intrinsic → F21
**STATUS: LIVE.** [`findings/doublet_chase/`](findings/doublet_chase/README.md). Resolves F18's "residual
unresolved." Hepatocyte–cholangiocyte doublet-suspects (KRT19 or KRT7 ≥2 UMI) **rise ~17× with fibrosis**
(0.01%→0.167% F1→F4) and carry the doublet signature of **inflated total counts** (F4 median 14,065 vs 3,096,
~4.5×) — genuine co-capture, not ambient. **Paper 1's >50,000-count filter catches NONE: 0 of 42,579 biopsy
hepatocyte nuclei exceed 50,000.** But they are too rare to dominate — only ~2.9% of F4 EPCAM; the other ~97%
is the diffuse ambient smear. So the residual = **mostly ambient + a small fibrosis-rising doublet
contribution Paper 1 could not have removed — neither hepatocyte-intrinsic.** Small-number caveat (16 suspects).

## Known doc-debt (to fix when un-freezing the report) — confirmed by cross-check agent 2026-06-23
Agent compared findings/ + ledger vs writeup/. Two real problems repeat; everything else is consistent.
- **(A) "surgical / atlas" healthy source — WRONG (4 spots):** `MANUSCRIPT.md` Table 1 (:48), Methods (:158),
  abstract (:16); `build_deck.js` (:116). Fix → "deceased-donor organ cube (mixed; one biliary-stone)".
  (SYNTHESIS.md §1a already correct.)
- **(B) Over-cautious "no detectable change / not preserved" with MDE as headline — contradicts D3:**
  `MANUSCRIPT.md` abstract (:7), title (:1), Discussion A (:134), Limitations (:144); `build_deck.js`
  slide 9 (:275 "Not 'zonation preserved'") which also contradicts its own slide 8 (:254 "zonation intact").
  Fix → assert the scoped positive claim "gene-expression zonation preserved across biopsy F1→cirrhotic F4"
  (grounded F8/F1/F15/F9), keep ONLY the lobule-architecture caveat, demote MDE to a footnote-bound.
  SYNTHESIS.md §2/§4 headers lag D3 slightly (minor).
- **CONSISTENT (verified, no change):** detox-attenuation correctly retired (D2) in §4 + deck slide 11; NAS/
  ballooning (F6/Item 7) not cited anywhere; DGE counts 31,257→17,572 match; stress folds, co-expression
  dual, PC-anchor fractions all match; depth-matched/binomial-thinning usage correct (no deprecated metric).
