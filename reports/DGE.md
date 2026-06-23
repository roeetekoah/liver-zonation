# DGE plans — differential expression across MASLD (v3)

_Planning doc, to be run with edgeR. v1/v2 archived → `archive/DGE_v1v2_archived.md`._

## Rationale (the corrected framing)
The DGE leg is **DISCOVERY, not another de-zonation test.** Zonation preservation is **already established
and treated here as settled input** — not re-tested (F1 all-sets, F8 sensitivity-grid, F9 gradient, F15
zonation-genes-flat). The DGE asks a different question: **given that zonation holds, what ELSE changes as
MASLD progresses — genome-wide (Plan A) and within each zonal population (Plan B)?** Let the data speak; we do
not pre-impose what to find. (The tools for *proving* preservation — affirmative equivalence bound,
gradient-spread — belong to the zonation leg / F9 / D3, and are queued there, not here.)

## Two different analyses, two different normalizations — "anchor-classification" vs "pseudobulk DGE"
These answer different questions and must be normalized differently. This distinction is the crux.

| | **Anchor-classification** (our term) | **Pseudobulk DGE** |
|---|---|---|
| Question | *Which* cells / how many — what fraction of hepatocytes are PC-like / PP-like / null / dual, and does that **proportion** change with disease? | *How much* — does a **gene's expression level** change with disease? |
| Unit shown | nucleus → donor-level **proportions** | gene → donor-level **counts** |
| Depth control | **binomial down-thinning to a common budget B** (per-cell): deeper cells detect more genes for free, so we equalize depth by *throwing molecules away* to make detection fair across cells | **library-size scaling (TMM)**: keep all counts, divide by a per-donor size+composition factor — throwing data away would cost power |
| Why thinning is wrong for DGE | — | thinning discards counts → loses the precision/power the count model needs; it's a per-cell detection control, not a per-donor expression normalizer |

- **"Anchor-classification" is OUR coined term**, not a field-standard one. The standard name for this is **cell-state
  composition / differential-abundance analysis** (cf. tools like miloR, scCODA, propeller). We should define
  "anchor-classification" on first use in the write-up (or use the standard phrase) so a referee isn't confused.
- **Glossary:** **TMM** = edgeR's per-donor scaling factor correcting depth **and** composition (the proper
  fix for the UMIs/10k denominator problem). **NB-GLM** = negative-binomial generalized linear model, the
  standard RNA-seq count model (counts over-disperse relative to Poisson; NB captures the extra spread).

## Plain-language glossary (every term + number gets its referent)
- **pseudobulk (the "gold-standard")** = sum each donor's hepatocyte raw UMIs into one count profile, then
  test donor-vs-donor. Field best practice (Squair et al., *Nat Commun* 2021): controls false positives that
  cell-level tests inflate. NOT magic — just the recommended method.
- **log2 fold-change (logFC)** = log base 2 of (expression in group A ÷ group B). Ratios because biology is
  multiplicative (10→20 and 1000→2000 are both "doubling"); log base 2 makes up/down **symmetric** (+1 = 2×
  up, −1 = halved) and each unit = one doubling. **logFC +3.1 = 2³·¹ ≈ 8.5× up; 0 = no change.**
- **FDR (false-discovery rate)** = among the genes you call "significant" at a threshold, the expected
  fraction that are false. We test ~21,000 genes, so some look significant by chance; FDR adjusts the raw
  p-value for that. **Example (verbose, as required): the zonation gene GLUL has FDR = 0.80 in F4-vs-F1
  (from `dge_planA_F4vsF1.csv`) — i.e. if we set the bar at GLUL's level, ~80% of "changed" calls would be
  false; far above the 0.05 cut, so GLUL shows NO detectable change.**
- **TMM** = edgeR per-donor scaling factor (depth + composition); the proper fix for the UMIs/10k denominator.
- **NB-GLM** = negative-binomial model for counts (over-disperse vs Poisson); how the change is tested.
- **burden (UMIs/10k)** = a gene's share of a cell type's transcriptome ×10⁴ — used to compare a gene's
  level **across cell types** (is it more a cholangiocyte or hepatocyte gene?). Simple metric; fine here
  because the cross-lineage differences are huge (5–65×) and robust to depth-matching.
- **decontX / SoupX** = standard ambient-RNA removal tools (SoupX: Young & Behjati 2020; decontX: Yang et
  al. 2020, celda). They estimate the ambient "soup" profile and subtract the estimated contamination per
  cell. Estimates, not ground truth — imperfect, but the recommended check for an ambient-vs-real question.
- **Cramér's V** = association of two categorical variables (0 = independent, 1 = perfectly confounded). The
  right check for "are sequencing batches randomized vs disease stage?" Ours: V(run,stage)=0.84 (NOT
  randomized; 9/13 runs single-stage); V(run,F)=0.40 within biopsies (partial). MDS-by-donor is a SECONDARY
  "did batch leak into expression" picture, not the design-level randomization check.
- **"preserved" vs "no detectable change":** a null DGE (every zonation gene non-significant; GLUL FDR 0.80,
  lowest of the set ADH4 FDR 0.43) = **no detectable change**,
  NOT proven preservation. The affirmative bound (F16: exclude shifts > ~±0.12–0.19) only rules out LARGE
  shifts. We do NOT claim tight quantitative preservation.

## Non-negotiable foundation (the missteps we will not repeat)
| past misstep | fix |
|---|---|
| SCT matrix for molecule inference | **raw RNA UMIs only** |
| UMIs/10k denominator drift | **TMM** (composition-aware), never per-10k |
| pseudoreplication (cells as *n*) | **pseudobulk per donor** (Squair et al., *Nat Commun* 12:5692, 2021 — verify) |
| pooling across the sampling confound | **biopsy F0–F4 only** is the disease axis; end-stage separate + descriptive |
| medians-as-final | **edgeR NB-GLM (quasi-likelihood, `robust=TRUE`)**, BH-FDR, log2FC + p |
| ≥1-UMI detection (ambient) | **≥2 (ambient-robust)** for cell labels; **compositional audit on every hit** |

**Engine:** edgeR (R/Bioconductor) — chosen for small-*n* calibration (F0=2, F4=4 barely estimate dispersion;
QLF `robust=TRUE` handles it). One-time BiocManager install. **Test:** omnibus factor test (does anything
change?) primary + F1-vs-F4 contrast; `filterByExpr` before BH-FDR.

## Built-in controls & sanity checks (run on every plan)
1. **Housekeeping negative-control panel** (ACTB, GAPDH, B2M, MALAT1, …): tracked across all stages/plans — must
   stay **flat**. Movement = a normalization artifact, not biology. The honesty check.
2. **Thinning cross-check** (ties to our trusted method): re-run after thinning each donor-pseudobulk to a
   common total; hits should survive both TMM and thinning.
3. **Leave-one-donor-out** on every hit (esp. F0 n=2, F4 n=4 — no single donor should drive a hit).
4. **Compositional audit** (`dge_compositional.py`): is the hit hepatocyte-intrinsic or stromal/immune ambient?
   For standout hits (e.g. A2M), a decontX sensitivity pass before promoting it.
5. **Curated modules annotated IN PARALLEL** (secondary, not primary): zonation (Wnt-core vs CYP, separately —
   cytokine CYP-suppression mimics pericentral loss, advances O5), urea-cycle, fibrogenic, acute-phase,
   cholangiocyte. Used to *interpret* the data-driven result, not to pre-decide it.
6. **DE-gene count sanity:** not thousands (over-loose) nor zero (over-strict); direction coherent.

---

## PLAN A — Genome-wide discovery across biopsy fibrosis (F0→F4)
- **Q:** Given preserved zonation, **what else** changes in hepatocyte expression across the acquisition-matched
  biopsy disease axis? (Data-driven, panel-free.)
- **How:** pseudobulk per donor over all hepatocyte nuclei (38 biopsy donors, raw UMIs); edgeR TMM + QLF;
  omnibus fibrosis test + F1-vs-F4; report all FDR<0.05 hits with effect sizes; run all 6 controls above.
- **Reproduces/replaces F15** (which used CPM+Spearman) on the proper edgeR normalization — expect the
  zonation/xenobiotic genes flat and the fibrosis-associated/A2M program; re-derive those numbers here.

## PLAN B — Within-class discovery (inside PC / PP / null / dual), across fibrosis
- **Q:** Given preserved zonation, do **specific programs shift inside a stable zonal population** — e.g. do
  still-PC cells turn on injury/stress programs as disease progresses, even while staying PC? (Exploratory; NOT
  a de-zonation test.)
- **How:** classify each nucleus PC/PP/null/dual by the ambient-robust (≥2 UMI) anchor classification; pseudobulk per
  donor **within each class**; edgeR within each class; exclude classifier genes; ≥30 nuclei/donor-class.
- **Read-alongside caveat (not a blocker):** the class label is a thresholded function of the cells' own
  expression, so a within-class result must be read **jointly with the class proportions** (Plan A / the
  anchor-classification) — a flat within-class program is interpreted together with whether the class *count* moved. Sensitivity
  at ≥3 UMI. (Under the discovery rationale this is a caveat, not a structural problem.)

## PLAN C — End-stage explants (descriptive only)
- **Q:** What does the end-stage explant gene program look like — per organ and across the 5?
- **How:** per-explant profiles (n=1 each, descriptive) + cross-explant heterogeneity (F14 extended
  genome-wide). Optional explant-vs-biopsy contrast for description only — **no inferential p-value** (it is
  perfectly confounded with tissue source + ischemia). **Mask the IEG/HSP stress module** (it otherwise tops
  the list). Lead the description with **ductular/transdifferentiation markers** (KRT7/KRT19/SOX9/SOX4/EPCAM/
  SPP1) and run the queued **O1** test (housekeeping-retained vs identity-lost — is the explant phenotype a
  program or just ischemic RNA degradation?). No disease claim from end-stage.

---
## Locked before running (from the tight v3 review)
1. **Primary inference = F1-vs-F4 contrast** (n=8 vs 4); the 5-level omnibus factor test is a **secondary
   screen only** (F0=2 is too thin to anchor an ANODEV). State the F4=4/F0=2 power limit next to the test.
2. **Batch CHECKED (F17 / `batch_qc.py`):** sequencing batch is NOT randomized — V(run,source)=0.84 (9/13
   runs single-stage; healthy/end-stage on dedicated runs). BUT within the 38 biopsy donors V(run,F)=0.40 and
   the 4 F4 donors share 2 runs (SLX-20270, SLX-20290) that also carry F0–F3 → **F1-vs-F4 is estimable
   within-batch, not collinear with run.** Handling: single-factor fibrosis model (13-level run can't be a
   fixed factor at n=38) + **MDS colored by run** pre-flight + **per-hit within-run sensitivity** (effect must
   appear inside SLX-20270/20290) + leave-one-donor-out. edgeR: `estimateDisp(design)` →
   `glmQLFit(..., robust=TRUE)` → `glmQLFTest`/`glmTreat`.
2b. **`filterByExpr` with the design matrix** (not just `group=`), so filtering respects the unequal group sizes.
3. **Min-nuclei-per-donor LOCKED:** Plan A **≥50**/donor, Plan B **≥30**/donor-class; report donor survival per
   stage per plan (a dropped F0/F4 donor can take a group to n=1 — check first).
4. **Pre-flight QC:** MDS + BCV/dispersion plot — catch an outlier donor or non-separating stages before LOO.
5. **Within-class (Plan B) p-values are descriptive/exploratory** — same donors recur across the 4 classes, so
   do NOT BH-correct across classes as if independent.
6. **Plan C:** disclose the masked IEG/HSP gene list explicitly (not cherry-picking); ensure no FDR table from
   the optional explant-vs-biopsy contrast leaks into the inferential results.
- verify **Squair et al., Nat Commun 12:5692 (2021)** before write-up; one-time edgeR/Bioconductor install.

**The affirmative equivalence bound is DONE on the preservation leg** (O12 → finding `equivalence_bound`,
not part of this DGE leg): across biopsy F1→cirrhotic-F4 we **exclude a coordinated PC-anchor shift larger
than ≈ ±0.15–0.19** (interior F1→F3 tightens to ≈ ±0.12); a *modest* ≤±0.10 drift is NOT excluded. Supports D3.
