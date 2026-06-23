# Synthesis — where we stand, integrated and grounded

_2026-06-23. Consolidation of the re-analysis around four claims the professor agreed we can make if
(and only if) they are grounded in the data/processing that supports them. Every number below was
re-verified this session against the raw-count tables; the script that produces it is named in line.
Unit of inference = donor, on raw RNA UMI counts (SCT abandoned). `FINDINGS.md` remains the raw log._

---

## 1. The sampling anomaly is real, structural, and decisive

The single most important fact about this cohort is **how the tissue was obtained**, and it is perfectly
aligned with disease stage.

### 1a. Sampling method by group — from Paper 1's own Methods (Gribben et al. 2024)
- **Disease spectrum F0–F4** (NAFLD/NASH/cirrhosis): *"Liver biopsies were done with ultrasound guidance
  using a 16 g end-cut needle (Biopince)… two ultrasound-guided needle core liver biopsies of ~2 cm,"*
  flash-frozen. Ethics REC 18/WM/0397.
- **Healthy controls AND end-stage**: *"Healthy deceased transplant organ tissue and explants… a cube of
  approximately 1 cm³ was cut and frozen."* Ethics REC 15/EE/152. *"For two healthy donors (HL1 and HL3)
  and all end-stage patients, samples were taken from each of the three liver lobes (left, right and
  caudate)."*
- **Correction to our earlier note:** there is **no published "atlas" source** for the healthy tissue —
  "atlas" appears in Paper 1 only as a cited reference. Both ends of the spectrum (healthy + end-stage)
  are **deceased-donor organ cubes**; only the F0–F4 disease spectrum is needle biopsy.

So the comparison that looks like a disease axis is actually **needle-biopsy parenchyma (F0–F4) vs
whole-organ cube tissue (healthy + end-stage)** — two different procurement modes, with the organ-cube
mode at both ends.

### 1b. The stress programs we measured, and what they actually mean
We summed raw UMIs of three curated programs per nucleus (`raw_panel_counts.csv`):
- **Immediate-early genes (IEG):** *FOS, JUN, JUNB, JUND, ATF3, DUSP1.* These are rapidly **inducible**
  transcription factors — but "immediate-early" is induction *kinetics*, not a momentary snapshot. In
  single-**nucleus** RNA they are detected as **active nascent/ongoing transcription**; their elevation
  across an entire dissociated/ischemic organ reflects a **sustained, prolonged stress response during
  procurement and handling**, not a clean transient pulse. This is the documented dissociation/ischemia
  artifact (van den Brink 2017; O'Flanagan 2019; Denisenko 2020).
- **Heat-shock chaperones:** *HSPA1A, HSPA1B* — proteotoxic / thermal / ischemic stress.
- **HIF/hypoxia targets:** *VEGFA, SLC2A1, LDHA, CA9, ENO1, PGK1* — used as a *contrast* (see 1d).

### 1c. Stress tracks sampling mode, not disease (donor-median hepatocyte UMIs/10⁴; `load_bearing.py`)
| group | sampling | nDonors | stress /10⁴ (median) | [min–max] |
|---|---|---|---|---|
| biopsy F0 | needle | 2 | 0.26 | 0.25–0.26 |
| biopsy F1 | needle | 8 | 0.41 | 0.19–0.87 |
| biopsy F2 | needle | 12 | 0.49 | 0.29–1.55 |
| biopsy F3 | needle | 12 | 0.39 | 0.21–0.78 |
| biopsy F4 | needle | 4 | 0.53 | 0.35–0.85 |
| **healthy** | organ cube | 4 | **1.16** | **0.17–5.07** |
| **end-stage** | organ cube | 5 | **10.15** | **6.12–20.16** |

The disease spectrum (all needle biopsies) is **uniformly low and flat** (0.26–0.53). The two organ-cube
groups are elevated and — for healthy — **wildly heterogeneous**.

### 1d. The end-stage stress is organ-level handling, not a hepatocyte disease program
Explant-vs-biopsy stress fold, **by lineage** (`supplementary_checks.py`):

| lineage | stress fold (ex/bx) | HIF fold |
|---|---|---|
| Hepatocytes | **21.0×** | 1.2× |
| Endothelial | **20.2×** | 2.9× |
| Stellate | 12.7× | 1.6× |
| Macrophages | 9.5× | 1.1× |
| Cholangiocytes | 8.7× | 0.7× |
| Lymphocytes | 4.5× | 1.2× |

**Endothelial cells — which carry no hepatocyte zonation — are as stressed (20.2×) as hepatocytes
(21.0×).** A signal that is identical in a cell type with no zonation cannot be a hepatocyte zonation
phenomenon; it is whole-organ procurement/ischemia. The HIF panel is only modestly raised in hepatocyte
nuclei (1.2×), arguing against a *sustained canonical hypoxia program*, though endothelial HIF (2.9×)
does not exclude acute ischemia. **Why this specifically threatens the zonation readout:** hepatocyte
metabolic zonation is maintained by an oxygen + Wnt/R-spondin gradient from central-vein endothelium,
and the pericentral detox axis (CYP/ADH) is the most perfusion-sensitive part (Kietzmann 2017) — so
ischemic whole-organ procurement is expected to perturb exactly the program the de-zonation claim rests on.

### 1e. "Healthy" is not a clean baseline (`metadata_all_cells.csv`)
| donor | library | recorded condition | lobe(s) | stress /10⁴ |
|---|---|---|---|---|
| 30 | SLX-21151-SITTB7 | — | (single) | 0.17 |
| 98 | SLX-21151-SITTF7 | **Biliary stone disease** (+CVD) | (single) | 0.46 |
| HL1 | SLX-20266-SITTC1 | — (+CVD) | **Caudate+Left+Right** | **5.07** |
| HL2 | SLX-20793-SITTD9 | — | Right | 1.86 |

The healthy group is four deceased-donor organs, **one with biliary-stone disease**, one multi-lobe and
high-stress (HL1, like the explants). It cannot serve as a matched control for the needle-biopsy disease
spectrum — different procurement, comorbidity, and a 30× internal stress spread.

### 1f. Inside end-stage there is no single phenotype — five organs, five directions (`load_bearing.py`, depth-matched)
| explant | nuclei | PC-anchor% | PP-anchor% | dual(≥2)% | null% | PP:PC | reading |
|---|---|---|---|---|---|---|---|
| CL104 | 1,908 | **49.7** | 6.7 | 1.1 | 17.7 | **0.13** | *retains* pericentral (more than the avg biopsy donor) |
| CL18 | 8,285 | 20.5 | 18.7 | **22.4** | 5.3 | 0.92 | co-expression *explosion* |
| CL103 | 1,960 | 14.2 | 41.7 | 2.7 | 25.5 | 2.93 | periportal-leaning |
| CL17 | 4,111 | 9.1 | 50.5 | 5.9 | 16.7 | 5.55 | periportal-leaning + dual |
| CL16 | 5,955 | **3.2** | 65.2 | 2.4 | 18.0 | **20.3** | near-total periportal collapse |

These are **not one end-stage program**: one organ keeps its pericentral pole (CL104), one collapses to
periportal (CL16, PP:PC ≈ 20), one floods into co-expression (CL18). This is the signature of
**heterogeneous, separately-handled organ procurement**, exactly what a single pooled marker-correlation
hides by collapsing five discordant organs into one number.

### 1g. Careful conclusion on the paper's claim
We do **not** assert the paper is wrong that end-stage liver looks de-zonated. We assert, and can ground,
that **the single-nucleus transcriptional leg of that claim cannot establish a progressive,
disease-driven de-zonation**, because: (i) it is measured across a needle-biopsy↔organ-cube sampling
discontinuity perfectly confounded with disease (1a–1c); (ii) the end-stage signal co-occurs with an
organ-wide acute stress program identical in non-zonated lineages (1d); and (iii) within end-stage it is
heterogeneous and non-reproducible across the five organs (1f). The protein-imaging and organoid legs of
the paper are **not addressed** by our data and are not refuted. *Speculatively* (clearly labelled as
such), the end-stage co-expression is some mix of genuine late-cirrhotic architectural remodelling and
procurement/ischemic artifact — **undecidable in this cohort**. To clarify it would require
**acquisition-matched end-stage tissue** (needle biopsies of end-stage livers, or non-end-stage
explants), or spatial/protein validation on biopsy-matched tissue.

---

## 2. Zonation-signal preservation across biopsy disease is real and confounder-checked

### 2a. The result (two independent, panel-free confirmations)
- **Marker-set invariant** (`all_sets_census.py`): the F0→F4 per-nucleus pericentral share is flat /
  non-monotone across **six gene sets spanning 2 → 1,637 genes** — canonical anchors, core, program,
  expanded, **Paper 2's own 20+20 landmarks**, and the 1,273/364-gene full set (F1–F4 deltas all within
  ±0.07). The null is not an artifact of marker choice.
- **Genome-wide** (`dge_genomewide.py`): in transcriptome-wide donor-level DE (38 donors, 17,572 genes),
  **every** pericentral/periportal/detox gene is non-significant (FDR > 0.79). Zonation markers are flat
  across the whole transcriptome.

### 2b. The confounder battery — every effort, with numbers and method (all on raw counts, donor unit)
This is the documentation the professor asked us to keep. Each row: the confounder, how it was tested,
the number, the verdict.

| # | Confounder | How tested | Result | Verdict |
|---|---|---|---|---|
| 1 | **Sequencing depth** | binomial down-thinning to common budget *B*; null re-checked at *B* = 1,000 / 1,500 / 3,000 (`census*.py`) | PC-share flat at every *B*; Monte-Carlo SD on donor-median 0.006–0.010 over 8 draws | not depth-driven |
| 2 | **Ambient RNA ("soup")** | per-donor *ALB* burden vs dual-fraction across 38 donors (`review_checks.py`) | *ALB* 17–102/10⁴; **corr(ALB, dual) = +0.04** | ambient does not drive co-expression |
| 3 | **Cholangiocyte mis-annotation** | biliary-marker detection by anchor class, biopsy (`review_checks.py`) | KRT19⁺ ≤ 0.001, EPCAM⁺ ≤ 0.003 in **all** classes; dual **not** enriched | not contaminating cholangiocytes |
| 4 | **Ploidy / complexity** | median nFeatures per nucleus by fibrosis (`review_checks.py`) | non-monotone 2,218 / 3,063 / 3,169 / 2,641 / 1,984 (F0–F4) | does not track stage |
| 5 | **Depth-matching discard** | fraction dropped below *B* and its PC-marker rate vs kept, per stage (`load_bearing.py` §4) | 3.5–7.8% dropped, uniformly lower-detection, not PC-biased | discard is depth-driven, not biasing F0→F4 |
| 6 | **Clinical covariates** | Spearman + partial corr, donor-level (`supplementary_checks.py`) | detox–Age ρ = −0.09; **partial(detox, F \| Age) = −0.32**; Age–F = +0.43; sex M24/F14; T2D recorded | demographics do not explain trends |
| 7 | **Technical batch** | cross-tab of experiment label vs stage | single label (`CG`) for all disease donors | **perfectly confounded — untestable, flagged (not "absent")** |
| 8 | **Stress dose (within-explant)** | per-donor PC-anchor in low- vs high-stress halves (`review_checks.py`) | deltas −0.03/−0.05/+0.00/+0.03/−0.03 → **3 of 5** donors in collapse-with-stress direction | suggestive only, not a clean mechanism |

Net: across eight raw-count confounder checks, **none manufactures the preserved-zonation result**, and
none is silently assumed away — #7 is explicitly flagged as unrecoverable here.

---

## 3. Next analysis (to run today): within-zone differential expression

Zonation **structure** is preserved (§2), but we have **not** asked whether the **expression program
within each zone** shifts with disease. Plan:
- From the depth-matched anchor classification, take **PC-anchor nuclei** and **PP-anchor nuclei** separately.
- Build **per-donor pseudobulk within each anchor class**, then run genome-wide donor-level DE across
  biopsy F0→F4 **within PC** and **within PP** (same method as `dge_genomewide.py`, conditioned on zone).
- Apply the **same compositional audit** (`dge_compositional.py`) to any hits, so within-zone changes are
  not ambient/stromal leakage.
- Question answered: *given that a cell is still pericentral (or periportal), does its program change with
  fibrosis?* — a within-zone disease signal that is orthogonal to the zonation-structure null.

This is the agreed next step; it is **not** yet run.

---

## 4. Statistical bounding (MDE) — kept, but held with a grain of salt

We keep the per-endpoint MDE table (`mde_table.csv`) but treat it as a **calibration of statistical
power, never a biological result**, for three reasons grounded in the data: the extreme strata are tiny
(F0 *n* = 2, F4 *n* = 4, each ~59% one donor); it bounds only **large** effects (structural endpoints
MDE ≈ 70–110% of the mean); and it is reported only to say *which large effects this cohort could have
detected* — never to claim zonation is "preserved." It is a limitation/bounding device, not a headline.

---

### Provenance of every number here
`load_bearing.py` (stress by stage, per-explant map, healthy), `supplementary_checks.py` (cross-lineage
stress/HIF, covariates), `review_checks.py` (ambient, biliary, ploidy, dose-response), `all_sets_census.py`
(marker-set invariance), `dge_genomewide.py` (genome-wide zonation flatness), Paper 1 Methods
(`papers/s41586-024-07465-2.pdf`) for sampling, `metadata_all_cells.csv` for healthy-donor characterization.

---
## One-story summary (all findings, 2026-06-23)
Gribben et al. (Nature 2024) reported, from single-nucleus RNA-seq across MASLD stages, that hepatocytes
**progressively lose their zonation** and **transdifferentiate** toward cholangiocytes; they tested de-zonation
by a marker–marker correlation (Welch's t-test) pooled over all 47 donors, and confirmed plasticity with
tissue imaging. Re-analysing the same data on **raw RNA UMI counts with the donor as the unit of inference**,
we find the dramatic signal is **confined to end-stage explant tissue, which is confounded on three collinear
technical axes**: tissue source (end-stage + healthy are deceased-donor ~1 cm³ organ cubes, while F0–F4 disease
is 16-gauge needle biopsy — Paper 1's own Methods); organ-wide procurement stress (immediate-early + heat-shock
genes elevated **5–21× in every lineage**, e.g. hepatocytes 21.0× ≈ **endothelial 20.2×**, a cell type with no
zonation — so it is whole-organ handling, not a hepatocyte program); and sequencing batch (**Cramér's V(run,
source) = 0.84**, near the maximum of 1, meaning run almost perfectly predicts tissue source — 9 of 13 runs carry
a single stage). The end-stage signal is also **not one phenotype** — across the five explants the pericentral-
anchor fraction ranges 3%→50% and the periportal:pericentral ratio 0.13→20 (CL104 *retains* pericentral, CL16
collapses to periportal, CL18 floods into co-expression) — the heterogeneous fingerprint of separately-procured
organs, which a pooled correlation hides in one number. **Across the acquisition-matched biopsy axis (fibrosis
F1 → cirrhotic F4), by contrast, hepatocyte gene-expression zonation is preserved**: the zonation marker genes
show no detectable change (pseudobulk + edgeR with TMM normalization and a negative-binomial test — e.g. GLUL
FDR = 0.43, far above the 0.05 cut → no detectable change); the zonal-anchor proportions are flat across every
threshold of the sensitivity grid (pericentral fraction 36/19/23/22/21% for F0–F4; the apparent ~10% "dual
co-expression" collapses to 0.2–0.6% once an ambient-robust ≥2-UMI cut is applied); and an equivalence test
**affirmatively excludes any coordinated re-zonation larger than ~±0.12 of the compartment** (90% CI on the
better-powered F1→F3 interior, n=8 vs 12; the least-powered F1-vs-F4 extreme, n=8 vs 4, only constrains to
~±0.15–0.19) — though a modest ≤10% drift and the lobule-scale spatial architecture are **not** excluded. A genome-wide discovery scan (Plan A) of "what else changes" found **only a biliary /
transdifferentiation program** rising into cirrhotic F4 (EPCAM, SOX4, SOX9, GRHL2; e.g. EPCAM log2FC +2.3,
FDR < 0.002). Because Paper 1 ran **no computational ambient-RNA removal** (no SoupX/decontX/CellBender) and
**no dedicated doublet-detection algorithm** (only a crude filter removing nuclei with >50,000 counts) — they
state QC "confirmed" the cells are not contamination but name no ambient tool, resting on their imaging — we ran
**decontX**: it removes a substantial part of this signal — the canonical transdifferentiation factors **SOX4
and SOX9 fall below significance** (FDR 0.131 and 0.118; decontX can over- as well as under-correct, so this
**demotes — it does not disprove** — these two) — but **EPCAM, B3GNT3, SPINT2 and CXCL10 survive**, so the
residual is unresolved (residual ambient, hepatocyte–cholangiocyte doublets — which their crude >50,000-count
filter would miss — or genuine low-level expression). Within-class testing (Plan B) shows this biliary program
appears **uniformly across pericentral, periportal, null and dual nuclei alike** (class-agnostic) — *consistent
with* ambient, though that inference rests on the cross-lineage burden (5–65× cholangiocyte-dominant) and the
≤0.4% per-cell co-expression, not on class-agnosticism alone — while the zonation genes are flat inside every
class. Notably, **the paper itself reserves the "full" transdifferentiation phenotype for end-stage** (*"acquired
only towards the end stage"*) and its one across-stage trend (Fig 3e, P = 0.03058) pools the procurement-
confounded healthy + end-stage groups. **Net:** in acquisition-matched biopsy MASLD, hepatocyte gene-expression
zonation is preserved against any large change, and there is no within-hepatocyte disease program except a
biliary signal that is at least partly ambient. We thereby **correct the transcriptional de-zonation leg** (which
the paper claimed *progressive across biopsy stages*) and **add that the modest biopsy-stage biliary rise is
largely ambient/ductular** — while **agreeing with the paper that the strong transdifferentiation is an
end-stage phenomenon**, and explicitly **not** addressing its end-stage protein / imaging / organoid evidence and
**not** claiming to overturn the paper.
