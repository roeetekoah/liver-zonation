# FINDINGS — MASLD hepatocyte zonation re-analysis (intermediate summary)

_Status: complete analysis, pre-write-up. For adversarial review before drafting. All quantitative
claims are on RAW RNA UMI counts (SCT abandoned); unit of inference = donor (~47), never the cell._

## The arc (what changed and why)
We began with the project's standing headline — **"hepatocyte zonation collapses / the pericentral
program turns off in MASLD, strongest at end-stage."** Rigorous re-analysis dismantled it and replaced
it with a defensible negative. The turning points:

1. **Metric discipline.** Stopped using relative/normalized summaries (z-scores, correlations, slopes,
   log2FC, "spread/IQR/anti-correlation") as headline evidence — they hide who-moved-how-many. Switched
   to absolute, countable quantities: number of nuclei, fraction of nuclei with raw UMI>0
   (detection), raw UMIs-per-10k (burden), and depth-matched cell counts.
2. **The data are SCT, not raw.** `counts.npz`/`counts.mtx` equal `nCount_SCT` exactly (depth squeezed
   to 3–5.7k); raw UMIs live only in the Seurat RNA assay. We extracted raw counts for a ~45-gene panel
   (`src/prep/05_extract_raw_panel.R` → `raw_panel_counts.csv`; verified raw: integer, library 920–49,854).

## The confound (the central, decisive finding)
**Disease stage is perfectly collinear with tissue source.** Per-donor provenance:
- end-stage = **5/5 transplant EXPLANTS**, multi-lobe (Caudate+Left+Right), donor IDs `CL*`;
- NAFLD / NASH / NASH-cirrhosis = **100% right-lobe NEEDLE BIOPSIES**, numeric IDs;
- healthy = 4 donors, surgical (`HL*`) + atlas, mixed provenance, depth outliers, one with "Biliary
  stone disease" → **unusable as a baseline**.
- Single experiment label (`CG`); NAS is unscored (NaN) for all explants; fibrosis F4 mixes
  biopsy-cirrhosis (n=4) with explant-end-stage (n=5).

**End-stage is a procurement/ischemia artifact, proven tissue-wide.** "Stress" (raw UMIs of immediate-
early FOS/JUN/JUNB/JUND/ATF3/DUSP1 + heat-shock HSPA1A/HSPA1B) is elevated **5–21× in EVERY cell
lineage** in explants vs biopsies (hepatocytes 21×, endothelial 20×, stellate 13×, macrophage 9×,
cholangiocyte 9×, lymphocyte 4×). Endothelial cells — irrelevant to hepatocyte zonation — are as
stressed as hepatocytes ⇒ organ-level handling/ischemia, not a hepatocyte disease program. End-stage
depth is NOT low (median nCount_RNA ~5.5k), so it is active stress transcription, not shallow dropout.
**⇒ end-stage cannot be a disease endpoint; the only identifiable disease axis is biopsy-only
fibrosis F0–F4 / NAS.**

## The corrected biology (raw counts, right-lobe biopsy, donor-level)
The original "pericentral turn-off" was wrong on the gene pattern itself:
- The genes that crash at end-stage are a **xenobiotic/detox subset** (CYP2E1, CYP1A2, ADH4, AKR1D1,
  SLCO1B3), NOT the whole pericentral program.
- **Pericentral IDENTITY is retained/induced** (GLUL up, CYP3A4 up) — and GLUL is the master β-catenin
  pericentral gene, so its retention while bystanders fall is evidence **against** a Wnt/zonation
  collapse and consistent with selective program suppression.
- Periportal metabolic genes (PCK1, ALDOB, HAL) are induced at end-stage — but this is confounded with
  fasting/glucagon physiology in NPO transplant donors; not oversold.

## H1 scenario coverage (complete — every mechanism by which zonation could collapse)
Explicit taxonomy, each mapped to a count-based signature, depth-matched, donor=unit, run along BOTH
fibrosis (F0–F4) AND NAS activity (`src/analysis/census.py`, `census_2d.py`, `gapfill.py`):

| scenario | signature | Fibrosis | NAS | Explant |
|---|---|---|---|---|
| Depletion | PC-anchor ↓ | flat | flat | 0.13 (↓) |
| Within-cell dimming | within-PC burden ↓ | mild, heterogeneous | mild | crash |
| De-zonation: co-expression | dual ↑ | flat (all B/thresh) | flat | 0.23 (↑) |
| De-zonation: gradient compression | per-cell PC/(PC+PP) → 0.5 | no (broad, stable) | no (flat) | collapse to PP-pole |
| Turn-off | null ↑ | flat | flat | flat |
| Composition shift | PP:PC anchor ratio | ~1.0 stable | ~stable | 3.4 (↑↑) |
| Induction | program ↑ | no | no | PP induced |

Every collapse mechanism is flat across biopsy disease (both axes); every one moves — in the same
artifact direction (PC lost → cells flipped PP-dominant) — only in explants. The polarization figure
(`results/figures/h2/gapfill_polarization.png`) shows the per-cell zonal balance staying broad/spread
across F0→F4 and collapsing to a PP-pole spike only in explants.

## Population-structure tests (the zonation question, count-based)
Per-donor anchor census: classify each hepatocyte nucleus PC-anchor / PP-anchor / dual / null on raw
counts, depth-matched (downsample every nucleus to 1500 UMIs), donor = unit.

**Across biopsy F0→F4, structure is FLAT — robust to every threshold variant:**
- PC-anchor fraction: flat / non-monotone (~0.11–0.34 depending on variant) → **no pericentral depletion**.
- dual (co-expression): flat, and **collapses to ~0 at ≥2-UMI threshold** → the ~20% "dual" at 1 UMI is
  ambient soup (CPS1/ALB) → **no de-zonation**.
- null: flat → **no turn-off**.
- Robust to: k=1 vs 2, PC 1-of-2 vs 2-of-2, PP 2-of-4 vs 3-of-4, ALDOB in/out, CPS1-based PP.

**2D joint distribution (final structural check):** the joint pericentral-vs-periportal program density
is the same shape across biopsy F1→F4 and collapses (pericentral program → 0) only in explants.
(Caveat: markers/depth give a PC-gradient band, not a clean two-pole anti-diagonal; the valid read is
"distribution unchanged across biopsy fibrosis, collapsed only in explants.")

## The one real disease signal — mild, heterogeneous, mechanism uncertain
Within retained pericentral cells, a SUBSET of detox genes attenuates modestly with fibrosis (F1→F4;
the decline is monotone only from F1 — F0 is n=2 and straddles the whole range, do NOT anchor at F0):
- **Heterogeneous, not a coordinated module** (F1→F4 donor-level UMIs/10k): ADH4 **−33%**, SLCO1B3
  **−26%**, CYP1A2 **−16%**, CYP2E1 **−12%** (the headline gene barely moves), AKR1D1 **+6%** (wrong
  way). Module-mean ≈ −19 to −27% hides this 6× spread.
- **Real, not a normalization artifact:** LODO-robust (F1−F4 gap stable 12.5–13.9 dropping any donor);
  depth-confound-clean (within-biopsy corr(detox, donor depth) = −0.11; F4 biopsies run shallower but it
  survives depth-matching: absolute count/cell F1=8.8→F4=7.1); ALB library share stable.
- **Mechanism is UNRESOLVED** — cannot distinguish cell-autonomous downregulation from paracrine/
  inflammatory CYP-suppression in this data. The "inflammation score weakest" argument is too weak. NOT
  shown: HNF4A/PXR/CAR-axis movement, cytokine signature, progenitor markers (SOX9/KRT19 ≈0.001, which
  argues AGAINST frank dedifferentiation). These genes are also exposure-sensitive (alcohol→CYP2E1,
  smoking→CYP1A2) and bile-acid-linked (SLCO1B3/AKR1D1→FXR), with zero etiology/drug covariates recorded.
  ⇒ describe as "attenuation of several xenobiotic genes, uncertain mechanism." Do NOT claim
  "dedifferentiation" or "tracks ballooning."

## Conclusions we can defend (hardened after adversarial review)
1. **End-stage explants are a tissue-procurement artifact** (organ-wide stress, all lineages); not a
   disease endpoint. Airtight — even the least-stressed explant cells have ~3.4× lower detox than
   F4-biopsy, so it cannot be subtracted out. STRONGEST claim.
2. Across acquisition-matched biopsy MASLD (F1→F4), there is **NO DETECTABLE change in hepatocyte
   zonation structure** — PC-anchor / dual / null fractions flat (robust to thresholds and depth budget),
   2D joint distribution unchanged, dual co-expression flat across fibrosis at every B/threshold. CAVEAT
   (load-bearing): the design is **underpowered** — minimum detectable effect ≈ 0.21 in PC-anchor
   fraction ≈ 85% of its mean (F0 n=2, F4 n=4, donor=unit). So the honest claim is "no detectable change,
   powered only to exclude near-total loss," NOT "preserved."
3. Pericentral identity markers GLUL/CYP3A4 do not fall — but GLUL is at the snRNA detection floor
   (~0.7 UMIs/10k) so its "retention" is **uninformative**, and GLUL/CYP3A4 covary with the detox genes
   across donors (+0.53), so this is NOT clean evidence of "identity preserved while sub-program down."
   Do not lead with GLUL.
4. The only disease-associated change is a **mild, heterogeneous attenuation of several pericentral
   xenobiotic genes** (above), of uncertain mechanism — not a structural zonation change.
5. The original "zonation collapses" headline is **not supported** in biopsy tissue. The bounded
   contribution corrects the snRNA evidence leg only (see FINAL + SIGN-OFF sections). [Literature-source
   ACTION ITEM is CLOSED — verified directly from papers/s41586-024-07465-2.pdf: disease = 16g biopsy,
   healthy + end-stage = explant; de-zonation legs all on explant tissue.]

## Honest limitations / what this cannot claim
- **No real spatial position** — snRNA, not spatial; "PC-like program," not lobule location.
- **GLUL is a dropout-prone anchor in human snRNA** (~0.21 detection); the census leans on CYP3A4.
- **Thin/unusable ends** — F0 biopsy n=2, F4 biopsy n=4; healthy baseline unusable (mixed source, one
  with biliary disease) → the disease axis is effectively F1→F4 and a NEGATIVE/retention story, not a
  healthy-vs-disease contrast.
- **Right-lobe biopsy ≠ whole-liver** — local microanatomical sampling could differ.
- **Etiology/clinical covariates unmeasured** (alcohol, medication, fasting, ICU) — blank for explants;
  CYP genes are exposure-sensitive.
- **Nuclei ≠ cells** (hepatocyte ploidy/binucleation); detection partly tracks ploidy.
- **RNA, not function** — supports expression retention/attenuation, not enzyme activity.
- Single cohort; no independent biopsy replication; no protein/IHC validation.

## Code / artifacts
`src/prep/05_extract_raw_panel.R`, `src/analysis/raw_counts.py`, `src/analysis/census.py`,
`src/analysis/census_2d.py` → `results/tables/analysis/raw*.csv, census_*.csv`,
`results/figures/h2/census_2d_joint.png`.

---
## FINAL — verified against the paper, hardened against review (supersedes the above where they differ)

**Paper 1's claim, verified by probing `papers/s41586-024-07465-2.pdf` directly (GROUND_TRUTH.md deleted; always probe papers/):**
- Abstract: "Hepatocytes lose their zonation." Their snRNA method: "Loss of zonation … assessed by comparing the CORRELATION between pairs of periportal and pericentral markers" (a relative-summary stat).
- Methods confirm tissue source: disease = 16g needle biopsy; healthy + ALL end-stage = deceased-transplant EXPLANT, multi-lobe (left/right/caudate). No ischemia times; QC removed mito/ribo-high cells but NOT IEG/HSP stress.
- De-zonation is backed by 3 evidence legs, all on end-stage explant: (1) snRNA marker-correlation, (2) immunofluorescence GLUL+ASS1 co-staining, (3) FLASH 3D whole-organ imaging. The paper's HEADLINE is hepatocyte↔cholangiocyte plasticity; de-zonation is a supporting observation.

**Bounded contribution (honest):** our re-analysis corrects evidence-leg #1 — the snRNA/transcriptional de-zonation is a confounded correlation stat on explant tissue with uncontrolled organ-wide procurement stress, and there is NO de-zonation across the acquisition-matched biopsy disease axis (F0–F4) by any count-based mechanism. We CANNOT refute the protein/imaging legs (#2–3), and end-stage cirrhotic architectural disruption is real pathology. So: a valid correction of the snRNA evidence + the progressive-disease framing — NOT an overturning of the whole zonation claim or the paper.

**Hardened robustness (src/analysis/census_v2.py):** census flatness across F0–F4 is robust to multi-draw depth-matching (M=8), B∈{1000,1500,3000}, and anchor = GLUL-only / CYP3A4-only / both. Gradient-compression as absolute count-bins (floor q∈{2,3,5}): poles stable, middle ~flat, informative denominator ~99%, only a mild PC-lean→PP-lean rebalance — no flattening. within-PC detox 12.7→8.9 (F1→F4), PC anchor excludes detox.

**Why we CANNOT say "zonation preserved" (documented per reviewers):** (1) pseudoreplication — at F4 one donor supplies 59% of cells; cell-n is not inferential n. (2) Power — donor-level MDE ≈ 0.21 ≈ 85% of the PC-anchor mean; only near-total loss is excludable. (3) Biopsy blindness — a needle core samples nodule parenchyma and snRNA measures per-cell transcriptional balance, NOT lobular architecture; it can detect collapse-to-a-pole (explants) but not lobule-scale spatial de-zonation. So the ceiling is "no detectable transcriptional de-zonation across biopsy MASLD; gradient present, not single-pole-collapsed; near-total loss excluded" — NOT "preserved."

**Language/scope fixes:** say "nuclei" (not cells) for depletion; "no detectable donor-level change" (not "flat"); "marker-count scenarios accessible to snRNA" (not "complete coverage"); "uninterpretable as a disease endpoint" (not "artifact") for explants; "attenuation of selected xenobiotic transcripts" (not "detox module"); no "dedifferentiation/ballooning-driven." Untestable here: true spatial relocation, focal peri-fibrotic remodeling, PC-substate replacement, functional/enzyme zonation, end-stage disease independent of explant.

---
## SIGN-OFF PASS — resolved (two final-review agents; this section is authoritative)

**Status: sign-off ready for write-up.** Two soft blockers + reporting fixes, all resolved here.

**Imaging (IF/FLASH), sharpened — our data DO bear on it, via STAGING not stress.** If de-zonation were
progressive, cells would drift toward GLUL+ASS1 co-expression by cirrhotic F4 biopsy. They do not: dual
co-expression at ≥2 UMI = 0.003 (F1) → 0.0 (F4); PP:PC composition flat. So our data REMOVE the
"progressive de-zonation" reading the snRNA leg supplied. They are silent on whether the end-stage
explant co-expression is genuine late cirrhotic architectural remodeling OR explant confound — this
dataset cannot adjudicate (disease stage perfectly collinear with explant source). We do NOT claim the
protein imaging is artifact. (When citing GLUL+ASS1 protein, say "pericentral/periportal PROGRAMS"; note
GLUL is a dropout-prone anchor here.)

**"Pericentral identity retained" — DROPPED as a standalone claim.** The panel has no well-detected,
detox-independent PC-identity marker: LGR5 (det 0.05–0.09) and AXIN2 (0.05) are at the snRNA floor like
GLUL (~0.18); CYP3A4 is the only well-detected non-detox PC marker and it covaries with the detox genes
(+0.53). So identity-retention is NOT independently established. The standing claim is the structural
null only (census flat, robust to GLUL-only / CYP3A4-only / both). To positively claim identity-retention
would require re-extracting RHBG / OAT / CYP2A6 (not done; deemed unnecessary).

**HIF/hypoxia check (closes the "ischemia = real zonal change" loophole).** Unlike IEG/HSP stress (5–21×
all lineages), the HIF panel (VEGFA/SLC2A1/LDHA/CA9/ENO1/PGK1) is modest and non-uniform in explants:
hepatocytes only 1.2×, endothelial 2.9×, cholangiocytes 0.7×. ⇒ the explant artifact is ACUTE
handling/dissociation stress, NOT a chronic hypoxic zonal program; no strong hepatocyte HIF program.

**Xenobiotic attenuation — DEMOTED to a caveat, not a named finding.** Not a coordinated module (ADH4
−33%, SLCO1B3 −26%, CYP1A2 −16%, CYP2E1 −12% marginal, AKR1D1 +6% wrong way); three uncontrolled
exposure axes with zero covariates (CYP2E1↔alcohol, CYP1A2↔smoking, SLCO1B3/AKR1D1↔bile-acid/FXR). Report
as "an exposure-confounded observation, not a zonation finding." Keep SOX9/KRT19/SOX4 ≈0.001–0.005 as a
reassuring control AGAINST dedifferentiation.

**Reporting additions for the write-up (numbers in hand):** (a) thinning Monte-Carlo noise = SD 0.006–0.010
across the 8 draws (immaterial vs MDE); (b) per-donor informative-denominator range 0.980–1.000 (no
selection hiding); (c) F0 AND F4 are each ~single-donor (largest donor = 59% of nuclei) → the negative
rests on the F1–F3 interior (8/12/12 donors), not the endpoints; (d) dual co-expression is entirely
ambient (vanishes at k≥2) — state as a positive soup control.

**Two clean claims for the paper (keep them separate, do not merge into one hedge):**
- A (strong): no detectable de-zonation by any count mechanism across acquisition-matched biopsy MASLD
  F0–F4, robust to depth budget / draws / anchor / thresholds; powered only to exclude near-total loss.
- B (explicit non-claim): end-stage explant co-expression (snRNA + IF + FLASH) is real-cirrhotic-remodeling
  OR explant-confound; this dataset cannot tell which; the protein/imaging legs are left uncorrected.

---
## POST-REVIEW REVISION (two professor-style passes) — src/analysis/review_checks.py

Folded into the manuscript + deck:
- **Dual co-expression, k=2 (ambient-robust):** biopsy ~0.003–0.006 at every F-stage vs **explant 0.029 (~7×)** — now the headline co-expression result. F0→F4 dual slope near-zero & non-monotone at B=1,000/1,500/3,000 (level scales with B, trend doesn't) → null is depth-budget-robust.
- **Explant is HETEROGENEOUS, not a concordant collapse:** per-donor PC-anchor 0.03–0.50, PP:PC 0.15–20 — CL104 *retains* PC (0.50 > biopsy mean), CL16 extreme PP-pole (PP:PC 20), CL18 dual-explosion (0.56). "Concordant collapse" removed; reframed as heterogeneous procurement damage; explant demoted from "positive control" to "contrast."
- **Within-explant dose-response (collapse vs stress):** pooled PC-anchor 0.20→0.14, PP-pole 0.23→0.31 low→high stress; within-donor only 3/5 → reported as supporting, NOT a clean cell-autonomous dose-response (procurement damage is multi-factorial).
- **Confounders TESTED in counts (not just listed) — all cleared:** ambient corr(ALB, dual)=+0.03; biliary KRT19/EPCAM not enriched in dual/PP nuclei (~0.0007, = PC) → not mis-annotated cholangiocytes; nFeat non-monotone with F (depth-matching handles it).
- **§4 now leads with absolute counts** (12.7→8.9 molecules/PC-nucleus F1→F4), not %change.
- **Positive mechanism added:** standing central-vein Wnt/Rspo gradient survives in nodular biopsy → predicts no de-zonation; explantation shocks the source → predicts the heterogeneous explant collapse. Null is now *predicted*, not just defended.
- **Framing fixes:** batch = "untestable, not absent"; transdifferentiation clause = "unanswerable," not "no"; unweighted program-sum caveat added.

Both reviewers' verdict: thinking is publication-grade; this revision closes the execution gaps they named.

---
## SECOND-REVIEW FIXES (both professors → sign-off) — src/analysis/supplementary_checks.py
- **Recorded-covariate test (the one analysis send-back):** Age/Sex/T2D ARE in the metadata (38/38 biopsy donors); Age tracks fibrosis (ρ=+0.43). The §4 detox dip is NOT explained by Age — detox–Age ρ=−0.09 (ns); detox–fibrosis survives Age adjustment (partial ρ=−0.32). §4 + Limitations wording corrected (recorded covariates tested & cleared; unrecorded alcohol/smoking remain untestable).
- **Committed the §1 cross-lineage stress/HIF script** (was uncommitted); estimator = donor-median (pooled-sum gives smaller ratios — noted in Methods).
- **Text fixes:** "dual → 0.0" → "≈0.003–0.005, non-monotone" (our two pipelines disagreed on exact F4; don't quote the prettier); ambient corr → "≈0"; bare ratios anchored to absolute counts (≈2 vs ≈7 molecules/nucleus); GLUL invoked as established gradient biology, not our evidence; nuclei-discarded "~4–8%, highest in F4".
- **SCT framing corrected** (prior turn): SCT = authors' legitimate normalization; the error was our extraction pulling the SCT default assay (01_extract_paper1_hepatocytes.R: GetAssayData default=SCT); corrected to raw RNA assay (05). Circularity resolved — downsampling is on raw molecules, never on SCT.
- Manuscript delivered as PDF (writeup/MANUSCRIPT.pdf, via build_pdf.py → Chrome print).

---
## DATA-PROVENANCE VERIFICATION (3 agents + authoritative schema dump)
- **Object schema (results/object_schema.txt, src/prep/07_dump_object_schema.R):** the GSE202379 Seurat object ships BOTH a raw RNA assay (31,257 genes; counts=integer molecules 920–49,854; data=log-norm) AND a processed SCT assay (30,117 genes; counts/data/scale.data; corrected 2,908–6,292), DEFAULT=SCT, + 52 metadata cols + SCT/Harmony clusters.
- **This extraction (prep/05) VERIFIED = raw RNA `counts` layer.** 9 committed sanity checks (src/prep/06_sanity_raw.py) all PASS: integer; E_raw==nCount_RNA; raw library range; differs from SCT matrix (565/800 cell,gene differ); ALB-dominant; panel⊆transcriptome; n=69,426 hep; plausible detection; no silent gene drop. RPLP0 legitimately absent (authors removed ribosomal genes at QC). 47 dropped metadata cols recoverable from metadata_all_cells.csv.
- **Old run (prep/01) = SCT default-assay counts** (corrected, not molecules) + own z-score normalization + circular SCT-thinning depth control. CONFIRMED by 3 agents.
- **Post-mortem (verified accurate):** two errors on two layers — (i) the relative z-scored-coordinate/marker-correlation APPROACH is confounded regardless of substrate (erases absolute level; absorbs depth/cell-number/tissue-source); (ii) SCT became the wrong substrate only when we pivoted to counting molecules. SCT was a defensible input for a signature SCORE — do NOT overstate "SCT broke it."
- **Paper 2 = NOT a data dependency of the final result** (fresh census uses canonical markers GLUL/CYP3A4 vs ASS1/CPS1/PCK1, not a Paper-2 ruler). Provenance section added to the manuscript/PDF.

---
## REVISION 3 (ChatGPT review → framing + load-bearing supplements) — src/analysis/load_bearing.py
- **Framing fixes (causal → inseparable), manuscript + deck:** "not disease / predicted artifact" → "inseparable from procurement stress / biologically plausible / consistent with"; "every mechanism" → "every snRNA marker-count mechanism"; deck title subtitle, formal-Q ("NO*" with per-clause footnote), scenario/result slide titles, picture caption ("abnormal, heterogeneous"); HIF → "argues against a sustained canonical HIF program, does not exclude ischemia"; MDE noted as PC-anchor-specific.
- **Load-bearing donor-level absolute-count table** added to §2 (per-donor PC/dual≥2/null n/N + stress/10k; biopsy flat, 5 explants heterogeneous: CL104 PC 50%, CL16 PC 3%, CL18 dual 22%). load_bearing_donor_table.csv.
- **Supplements:** full 8-gene biliary panel by anchor class (no enrichment, all ≤0.004); donor-stratified dose-response (deltas −0.03/−0.05/+0.00/+0.03/−0.03 → 3/5, "suggestive not mechanism"); discard profile (3.5–7.8%, depth-driven, consistent across stages, not PC-biased).
- **Caveats reworded:** ambient = diagnostic not full kill (no SoupX); "ploidy" → "depth/complexity proxy, true ploidy unmeasured"; thinning = panel-gene on full-library denominator (marginal approximation).
- **Deck stress slide** now shows raw donor-median UMIs/10k (biopsy vs explant), fold as annotation (was fold bars); xenobiotic slide leads with counts (12.7→8.9), not %.

---
## REVISION 4 (ChatGPT pass 2 → minor-moderate, framing)
- **MDE/power centered** (abstract + deck conclusion): "excludes near-total marker-count collapse but underpowered for moderate/focal/spatial de-zonation; no detectable change ≠ quantified preservation."
- **Non-identifiability wording** replaces causal: "not disease" → "not identifiable as progressive disease" (abstract, conclusion, deck formal-Q card + conclusion).
- **"every mechanism"** scoped to "every marker-count mechanism detectable in spatially-blind snRNA."
- **Deck formal-Q**: punchy "NO" → "Answer, clause by clause:" with per-clause cards (coordinate computable-not-reliable / no detectable biopsy-stage change / link unanswerable).
- Donor-level absolute-count table remains the lead evidence (rev 3). Ambient still labeled diagnostic-not-kill; ploidy = depth/complexity proxy; HIF softened. Conceptual Q&A (why depth is a confounder normalization can't fix; binary vs amounts; ≥2-UMI/ambient; how the null was solidified vs the old pass) recorded for the session.

---
## MDE SOLIDIFIED (src/analysis/mde.py -> mde_table.csv)
Explicit MDE = 2.80 * pooled_donor_SD * sqrt(1/n1+1/n2) (alpha .05, 80% power, donor unit), per endpoint:
- PC-anchor F1vsF4: SD .128, MDE .219, mean .260 = 85% (this IS the "0.21~85%"); F1vsF3 interior: 53%.
- PP .163/71%; null .302/73%; dual(>=2) abs MDE .016 (near-zero endpoint -> excludes a LARGE co-expr rise, not subtle); within-PC detox MDE 2.35 = 22% (better powered -> the observed ~30% dip IS detectable).
- Conclusion: excludes near-total marker-count collapse; cannot quantify preservation or rule out moderate/focal/spatial change. Table embedded in manuscript.

---
## GENOME-WIDE & ALL-SETS PASS (2026-06-22) — closing the "panel-only" gaps. STILL INTERMEDIATE; NO FINAL REPORT YET.
Three gaps were flagged: (1) "no change" cells had no numbers; (2) "the ONLY biopsy-internal change is the detox dip" was never tested transcriptome-wide (panel only); (3) only 3 marker sets shown. Closed all three from RAW counts, donor unit. New extractions: `src/prep/08_extract_paper2_landmark_raw.R` (Paper-2 40 landmark genes) and `src/prep/09_extract_full_and_union.R` (FULL 31,257-gene donor pseudobulk over hepatocytes + per-cell raw for the 1,645-gene curated union).

### (A) GENOME-WIDE donor-level DGE across biopsy F0-F4 — `src/analysis/dge_genomewide.py` -> dge_genomewide.csv  ** FORCES A CLAIM CHANGE **
Pseudobulk = sum raw UMIs over each donor's hepatocyte nuclei; 38 biopsy donors (F0..F4 = 2/8/12/12/4); 17,572 genes expressed (CPM>=1 in >=19 donors); Spearman(log2CPM vs F), BH-FDR.
- **23 genes trend at FDR<0.05** — so the detox dip is NOT "the only" biopsy-internal change. Top movers (mostly UP with fibrosis): A2M (CPM 219->718, rho+.69), ESRRG (33->204), DTNA (74->267), GUCY1A1 (9->38), ADAMTS9 (8->29), FREM2, EPB41L4A; DOWN: DOK6 (101->16), ENPP3 (22->8), LINC01205 (34->7). Profile = a fibrosis/injury/ECM-associated program (A2M, ADAMTS9 are classic stromal/acute-phase) — likely PARTLY COMPOSITIONAL/ambient from the expanding fibrotic stroma; not disentangled (no deconvolution). Several top hits are low-CPM (noisy); the higher-expression ones (A2M, ESRRG, DTNA, DOK6) are credible.
- **The detox/zonation panel is NOT significant genome-wide:** CYP2E1 fdr .98, CYP1A2 .91, ADH4 .97, AKR1D1 .95, SLCO1B3 .80, CYP3A4 .97, GLUL .85; PP genes ASS1/CPS1/PCK1/HAL/ALDOB/ARG1 all fdr>.79, |log2FC|<=0.4. So the zonation markers are flat genome-wide (STRENGTHENS the no-de-zonation null), and **the §4 detox attenuation does NOT survive a genome-wide donor-level test** (it was a within-PC-conditioned, borderline ~30% effect at MDE~26%; not robust in pseudobulk).
- **=> TWO claims must change before any final report:** (i) abstract+§4 "the only biopsy-internal change is a mild xenobiotic attenuation" is FALSE on both counts — not the only, and the detox change itself is not genome-wide-robust; (ii) reframe: biopsy hepatocyte transcriptome is broadly stable across F0-F4; the genes that DO move are a fibrosis-associated (likely partly compositional) program, NOT the zonation or xenobiotic genes; the targeted within-PC detox dip is at most a weak, non-robust signal, not a headline.

### (B) ALL-SETS CENSUS across the breadth ladder (2 -> 1,637 genes) — `src/analysis/all_sets_census.py` -> all_sets_census.csv
Same depth-matched (B=1500) donor-level census, 40,303 biopsy hep nuclei, per-nucleus PC-share = PCsum/(PCsum+PPsum). F0..F4 PC-share, all FLAT/non-monotone:
- canonical(2/4):   .375/.200/.262/.223/.265   (F1-F4 -.065)
- core(20/20):      .564/.543/.514/.473/.491   (+.052)
- program(7/6):     .662/.648/.611/.576/.597   (+.051)
- expanded(94/86):  .565/.548/.534/.495/.494   (+.054)
- paper2_landmark:  .565/.542/.511/.471/.497   (+.045)   [Paper 2's OWN ruler genes; no GLUL in their PC set]
- full(1273/364):   .820/.816/.815/.803/.805   (+.011)
=> the de-zonation null is **marker-set invariant across the entire curated ladder**, incl. Paper 2's landmarks and the 1,637-gene full set. The LEARNED/fitted signatures were deliberately NOT re-run (they are the relative-ruler class we reject). See memory [[markerset-invariance]].

### (C) EXPLICIT per-stage numbers behind every Table-2 "no change" (biopsy; donor-median [IQR]) — from load_bearing_donor_table.csv
- PC-anchor% (depletion):   F0 36.0[32-40]  F1 18.7[17-35]  F2 23.2[20-30]  F3 21.9[16-23]  F4 21.4[19-29]  (non-monotone; F1 floor)
- PP-anchor%:               F0 19.6        F1 20.9        F2 22.3        F3 24.2        F4 24.1
- dual2% (co-expression):   F0 0.05        F1 0.23        F2 0.45        F3 0.21        F4 0.24  (all <0.5%; explants 1-22%)
- null% (turn-off):         F0 34.2        F1 43.5        F2 35.6        F3 38.7        F4 39.4
- PP:PC ratio (composition):F0 0.62        F1 1.16        F2 1.01        F3 1.10        F4 1.18  (no monotone drift)
=> these replace the bare "no change" cells; every endpoint is flat/non-monotone across F0-F4 with overlapping IQRs.

### STATUS / WORKFLOW
- Per the lead: ACCUMULATE here in FINDINGS.md; do NOT regenerate the manuscript PDF or deck until everything is locked and the §4/abstract correction is settled.
- Open items before a final report: (1) decide final wording for the retired "only change" claim using (A); (2) optionally test whether the (A) fibrosis-program genes are compositional (ambient/stromal) vs hepatocyte-intrinsic; (3) propagate (B)/(C) numbers into the report; (4) re-run adversarial reviewers on the corrected draft.

### (D) COMPOSITIONAL/AMBIENT check on the 23 DGE hits — src/prep/10 + src/analysis/dge_compositional.py -> dge_compositional.csv
Question: are the fibrosis-trending genes hepatocyte-intrinsic or stromal/immune ambient? Two diagnostics on RAW counts (all 99,809 cells).
- **Non-hep nuclei fraction does NOT rise with fibrosis** (Spearman rho=-0.07; median 0.27) — so this is NOT a gross compositional-fraction artifact; and hep-pseudobulk CPM does not track the donor non-hep fraction for any gene (|corr|<=0.19).
- **Cross-lineage burden (UMIs/10k):** 15/23 hits are >=3x more highly expressed in a NON-hepatocyte lineage than in hepatocytes (cholangiocyte/stellate/endothelial/immune) -> most consistent with low-level AMBIENT contamination of hepatocyte nuclei, not a hepatocyte program. Examples: ADAMTS9 (Stellate 17x), GUCY1A1 (Stellate 15x), EPB41L4A (Endothelial 7.5x), PAQR5/EVC/EVC2/FREM2/GABRB3/FAM83F (Cholangiocyte-dominated).
- **Genuinely hepatocyte-intrinsic (5):** notably **A2M** (hep burden 8.1, hepatocyte-dominant; CPM 219->718) — a classic hepatocyte acute-phase/injury gene; plus ENPP3 (down), PTCHD1-AS, LINC01205, LINC02762. 3 mixed (ESRRG, DOK6, C6orf99).
- **Synthesis for the correction:** transcriptome-wide, the hepatocyte ZONATION and XENOBIOTIC programs are unchanged across F0-F4 (all FDR>0.79) — the null holds genome-wide. The genes that DO trend are mostly ambient stromal/immune contamination (15/23) plus a SMALL genuine hepatocyte acute-phase response led by A2M. The earlier within-PC detox dip does NOT survive the genome-wide test. => retire "the only biopsy-internal change is a xenobiotic attenuation"; replace with "the biopsy hepatocyte transcriptome is broadly stable; no robust zonation/xenobiotic change; the only hepatocyte-intrinsic disease signal is a modest acute-phase response (A2M), not de-zonation."
