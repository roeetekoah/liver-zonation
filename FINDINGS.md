# FINDINGS — hepatocyte zonation & epithelial plasticity in MASLD snRNA-seq

Re-analysis of Gribben et al., Nature 2024 (GSE202379), single-nucleus transcriptomic component only.
This file is the **story-ordered summary**. The full narrative is [`reports/FULL_STORY.txt`](reports/FULL_STORY.txt);
each finding is documented with numbers + method + caveats under [`findings/`](findings/README.md); the audited
claim-by-claim trail with decisions and the future-work queue is [`CLAIMS_LEDGER.md`](CLAIMS_LEDGER.md).

All quantitative claims are on **raw RNA UMI counts** (not the paper's SCT matrix); the unit of inference is the
**donor** (~47), never the cell.

---

## Conclusion (narrow but firm)

In acquisition-matched MASLD **needle-biopsy** samples, hepatocyte transcriptional **zonation is preserved**
across the fibrosis axis (F1→cirrhotic-F4). The apparent progressive de-zonation in the original analysis is
largely a **sampling/source confound**: the healthy and end-stage groups are organ tissue, acquired differently
from the disease biopsies. A genome-wide differential-expression scan finds **no other large hepatocyte program**
changing across the biopsy axis except a small **biliary/ductular marker burden** at F4 that is most consistent
with **cholangiocyte ambient RNA + rare mixed/doublet nuclei** (the ductular reaction), not widespread
transdifferentiation — though that source attribution is **not closed**. We correct only the single-nucleus
transcriptomic leg; we do not touch the paper's imaging / protein / organoid / spatial evidence, and we agree
the strong signal is an end-stage phenomenon.

---

## The story, section by section (each maps to finding folders)

**1. The central confound: tissue source is tied to disease stage.** Disease F0–F4 = 16-gauge needle biopsies;
healthy = deceased-donor organ cubes; end-stage = explanted organs (multi-lobe). So "healthy → MASLD → end-stage"
is also "organ cube → needle → explant" — disease stage is collinear with acquisition method. This is the
load-bearing issue; it motivates excluding the ends and re-testing biopsy-only.
→ grounded in Paper 1 Methods; see [`reports/SYNTHESIS.md`](reports/SYNTHESIS.md) §1 and ledger Item 1 / Decision D1.

**2. Lobe invariance — one sub-confound cleared.** Within end-stage explants (sampled Right/Caudate/Left), the
zonation-marker **detection** pattern is lobe-invariant (e.g. GLUL 0.350/0.343/0.297; ALDOB 0.821/0.837/0.838).
So caudate/multi-lobe sampling is not what manufactures the signal. Clears only the lobe sub-confound, not the
bigger explant-vs-biopsy one.
→ [`findings/lobe_invariance/`](findings/lobe_invariance/README.md) (F1).

**3. Procurement stress is visible and source-collinear.** Stress module (8 immediate-early + heat-shock genes),
depth-normalized to a common 1,500-UMI budget, mean per nucleus: **biopsy 0.074, healthy 0.282, end-stage 1.675**
(~22× biopsy). The decisive control is cross-lineage: end-stage vs biopsy stress is ~18× in hepatocytes AND ~18×
in **endothelial cells** (no zonation program) — so this is organ-wide acute handling, not hepatocyte biology.
Hypoxia (HIF) is only ~1–3×, so it is acute dissociation stress, not chronic hypoxia. → justifies excluding the
ends from the disease axis.
→ [`findings/stress_and_panel_by_stage/`](findings/stress_and_panel_by_stage/README.md) (F2/F3),
[`findings/stress_celltype_segmented/`](findings/stress_celltype_segmented/README.md) (F5).

**4. The main zonation test — count-based anchor classification + scenario coverage.** On the clean biopsy axis,
classify each hepatocyte by strict mutually-exclusive anchors (pericentral GLUL/CYP3A4; periportal
ASS1/PCK1/HAL/ALDOB) at an ambient-robust ≥2-UMI threshold on depth-normalized counts, into PC / PP / dual / null.
Then test every way zonation could fail:
- **depletion** (PC-anchor fraction ↓): 36/19/23/22/21% F0–F4 — flat/non-monotone. No.
- **co-expression** (dual ↑): collapses from ~7–10% at 1 UMI to **0.2–0.6%** at ≥2 UMI, no trend — the 1-UMI
  signal was ambient soup. No.
- **turn-off** (null ↑): flat. No.
- **composition shift** (PP:PC ratio): 0.62/1.16/1.01/1.10/1.18 — flat/non-monotone. No.
- **gradient compression** (mass to the middle): at most a mild non-monotone middle-ward drift, poles stay
  dominant. Gradient present, not collapsed.
Robust across the whole sensitivity grid and marker-set ladder (2→1,637 genes). This is the positive case for
preserved zonation.
→ [`findings/census_robustness/`](findings/census_robustness/README.md) (F8),
[`findings/scenario_taxonomy/`](findings/scenario_taxonomy/README.md) (F9),
[`findings/integrated_census/`](findings/integrated_census/README.md) (F7).

**5. Why we changed the measurement — the relative-ruler postmortem.** The earlier z-scored relative ruler was
abandoned because (a) it was source-confounded, and (b) it is intrinsically depth-sensitive and mechanism-blind
(turn-off, co-expression, and noise all shrink its spread). The count anchor classification separates the
mechanisms; the ruler cannot.
→ [`findings/relative_ruler_postmortem/`](findings/relative_ruler_postmortem/README.md) (F12). The Simpson/
aggregation reversal that this produced is documented in [`reports/SYNTHESIS.md`](reports/SYNTHESIS.md).

**6. The 2D joint-count view — and its correction.** The broad-program 2D plot is a **pole-collapse**
visualization, not a co-expression test (the program sums include genes ON in most normal hepatocytes). The clean
high-amount co-expression conviction is the strict anchor dual at ≥2 UMI (~0.2–0.6% biopsy vs ~2.9% explant).
→ [`findings/joint_count_2d/`](findings/joint_count_2d/README.md) (F13).

**7. End-stage explants are heterogeneous, not one program (important).** The five explants go in opposite
directions: CL104 retains pericentral (PC 49.7%, PP:PC 0.13); CL16 nearly collapses to periportal (PC 3.2%,
PP:PC 20.3); CL18 floods into co-expression (dual 22.4%). PC-anchor 3%→50%, PP:PC 0.13→20. Pooling them into one
correlation manufactures a uniform "collapse." Signature of heterogeneous, separately-handled organ procurement.
→ [`findings/explant_heterogeneity/`](findings/explant_heterogeneity/README.md) (F14).

**8. Bounding the absence of a large shift — equivalence + batch honesty.** Across biopsy F1→F4 the
pericentral-anchor fraction changes by +2.4 percentage points; the data **exclude a large shift on the order of
20 percentage points** (interior F1→F3 tightens to ~12), but do **not** exclude a subtle drift below ~10. Batch is
not randomized (run predicts source, Cramér's V 0.84); within the biopsy axis the biliary hits survive a
run-covariate and a single-run test (effect persists, only significance attenuates), so they are not a batch
artifact.
→ [`findings/equivalence_bound/`](findings/equivalence_bound/README.md) (F16),
[`findings/batch_randomization/`](findings/batch_randomization/README.md) (F17).

**9. Genome-wide pseudobulk DGE — the discovery scan.** Pseudobulk per donor → edgeR (TMM + negative-binomial
quasi-likelihood). Two roles:
- *Independent count-based check on zonation:* zonation genes flat at the expression level (GLUL FDR 0.80),
  housekeeping flat — a sanity check agreeing with the anchor classification, **not** the primary proof.
- *Discovery:* of ~21,000 genes only **64** reach FDR<0.05 at F4-vs-F1, and they are a biliary/ductular marker
  set (EPCAM, GRHL2, SPINT2, SOX4, SOX9, B3GNT3) + CXCL10 — i.e. a **biliary-marker burden inside
  hepatocyte-labeled pseudobulk**, not proof of plasticity. Honest claim: **no large single-gene program outside
  that burden; gene-set testing still owed** to exclude weak coordinated pathways (future work O13).
Plan B (within-zone DGE) is a subordinate robustness check, confirmatory given flat proportions.
→ [`findings/genome_wide_dge/`](findings/genome_wide_dge/README.md) (F15),
[`findings/dge_plan_a/`](findings/dge_plan_a/README.md) (F18),
[`findings/dge_plan_b/`](findings/dge_plan_b/README.md) (F20, subordinate).

**10. Interpreting the biliary-marker burden (a side lead, not closed).** Evidence it is compositional: the
headline genes are 5–78× more abundant in cholangiocytes than hepatocytes; the cholangiocyte fraction rises to
~8% at F4 (ductular reaction); only ~0.4% of hepatocyte nuclei robustly co-express biliary markers; decontX cuts
hits 64→34 and drops SOX4/SOX9 below significance. But EPCAM/B3GNT3/SPINT2 survive (decontX is a consistency
check, not a verdict), and a crude doublet probe (KRT19/KRT7 ≥2 UMI; rises with fibrosis; all below the paper's
>50,000-count filter) is a **lead, not a finding** — it cannot separate a doublet from a rare transdifferentiating
cell. **CXCL10 is separate** — its hepatocyte expression does not track the cholangiocyte fraction (corr −0.09),
so it is a candidate real inflammatory signal, not ambient.
→ [`findings/dge_plan_a/`](findings/dge_plan_a/README.md) (F18, source-attribution section),
[`findings/doublet_chase/`](findings/doublet_chase/README.md) (F21, exploratory lead).

---

## What we explicitly do NOT claim
- Not an overturning of the paper — only the single-nucleus transcriptional de-zonation leg, in matched biopsy.
- Nothing about the paper's imaging / protein / organoid / spatial-architecture evidence.
- Not spatial/architectural preservation — snRNA measures per-cell transcriptional balance, not lobule geometry.
- Not "no hepatocyte program whatsoever" — only no single-gene and no large coordinated program detected; the
  gene-set test (O13) is still owed.
- Not that the biliary signal is definitively non-intrinsic — the source-attribution leg is a promising lead.
- We agree with the paper that the strong zonation/transdifferentiation signal is an end-stage phenomenon.

## Future work (designated, see CLAIMS_LEDGER OPEN queue)
- **O13** — gene-set / pathway test (CAMERA + ROAST) to exclude weak coordinated programs (highest priority).
- Leave-one-F4-donor-out DGE + per-donor biliary-gene plots (F4 robustness).
- Quantitative contamination accounting (does the ambient/doublet burden quantitatively explain the counts).
- **O1, O2, O4, O11** — explant ischemia test, stress dose-response, NAS second axis, deeper per-explant profile.

## Quarantined / not used in the story
- NAS↔detox component test (F6) — confusing result, quarantined, do not cite.
- The "xenobiotic detox attenuation" — demoted to an exposure-confounded caveat; did NOT survive the genome-wide
  test; not a finding (Decision D2).
- The z-scored relative ruler — abandoned (F12).
