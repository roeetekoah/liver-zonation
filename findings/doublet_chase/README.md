# F21 — Doublet chase: do the decontX-surviving biliary genes come from hepatocyte–cholangiocyte doublets?

**Status: LIVE.** Script `src/dge/doublet_chase.py` → `results/tables/analysis/doublet_chase.csv`.
Follow-up to F18: after decontX, EPCAM/B3GNT3/SPINT2/CXCL10 still tested significant F4-vs-F1 and we
listed three possible sources of that residual — (a) residual ambient decontX under-corrected, (b)
**hepatocyte–cholangiocyte doublets** (which decontX does not model and which plausibly rise in cirrhosis),
or (c) genuine low-level hepatocyte expression. This finding tests (b) directly.

## The test (and why it discriminates doublet from ambient)
A real hepatocyte–cholangiocyte **doublet** co-captures a whole cholangiocyte transcriptome, so it shows
**two** things at once: (a) it co-detects cholangiocyte **structural** markers (KRT19 or KRT7) that a true
hepatocyte does not express, AND (b) its **total UMI count is inflated** (two cells' worth of RNA in one
barcode). **Ambient** contamination produces (a) **without** (b): ambient sprinkles a few stray molecules
into a nucleus, it does not double its library size. So **total-count elevation is the discriminator** —
doublet vs ambient — and Paper 1's only doublet control was a count threshold, which makes this exactly
the right axis to probe.

"Doublet-suspect" = a biopsy hepatocyte-annotated nucleus with **KRT19 ≥ 2 UMI OR KRT7 ≥ 2 UMI**.
Numbers per fibrosis stage (biopsy only; deceased-donor CL* explants + healthy controls excluded):

| F | n hepatocyte nuclei | % doublet-suspect | median total UMI: suspect vs rest | EPCAM share in suspects |
|---|---|---|---|---|
| F0 | 2,024 | 0.000% | — vs 3,857 | 0% |
| F1 | 10,429 | 0.010% | 1,126 vs 6,812 | 0% |
| F2 | 12,106 | 0.025% | 4,839 vs 6,720 | 0% |
| F3 | 14,417 | 0.042% | 13,833 vs 5,631 | 0% |
| F4 | 3,603 | **0.167%** | **14,065 vs 3,096** | **2.9%** |

## Results — three things, stated plainly
1. **Doublet-suspects DO exist and DO rise with fibrosis.** Their fraction climbs monotonically
   **0.00% → 0.01% → 0.025% → 0.042% → 0.167%** across F0→F4 — a **~17× rise** from F1 to cirrhotic F4,
   exactly where the biliary pseudobulk signal (F18) appears.
2. **They carry the doublet signature — inflated total counts.** At cirrhotic F4 the suspects have a
   **median 14,065 total UMIs vs 3,096 for ordinary F4 hepatocytes (~4.5×)**. Because ambient does not
   inflate a nucleus's total count, this points to genuine **co-capture of a second (cholangiocyte) cell**,
   not ambient-soaked singlets. (At F3 the gap is even larger, 13,833 vs 5,631.)
3. **Paper 1's filter provably misses them.** Their only doublet control was *"nuclei with more than 50,000
   counts were removed."* **0 of 42,579 biopsy hepatocyte nuclei exceed 50,000 counts** — so **every** one
   of these doublet-suspects (all below 50,000) **survived their filter**. The crude count cut is set far
   above where these doublets actually sit and removes none of them.

## The honest limit — doublets are real but NOT the main driver
The suspects are **too rare to explain the bulk** of the surviving biliary signal. At F4 they carry only
**~2.9% of all F4-hepatocyte EPCAM UMIs** (a handful of molecules in 6 nuclei = 0.17% of F4 hepatocytes).
The other **~97%** of the EPCAM signal is a thin, diffuse smear spread across thousands of ordinary nuclei
— the signature of **ambient**, not doublets. So the residual that survived decontX is **two non-intrinsic
sources, not one**: a *dominant diffuse ambient smear* + a *small, fibrosis-rising doublet contribution*.

## Conclusion (illustrative, not decisive — softened after adversarial review)
This **shifts the "residual unresolved" caveat in F18 toward the ambient/compositional direction, and
surfaces a concrete QC gap in Paper 1.** The decontX survivors are **not** evidence of hepatocyte-intrinsic
transdifferentiation: most is a diffuse ambient smear; the remainder is a small fraction of
**co-capture/biphenotypic nuclei** that (i) accumulate with fibrosis and (ii) sit entirely below Paper 1's
50,000-count doublet threshold, so their pipeline could not have removed them. Either way it is a
compositional consequence of the ductular reaction, not a coordinated hepatocyte program.

**Two reviewers flagged that this leg is illustrative, not decisive — keep it that way:**
1. **The KRT19/KRT7 ≥2-UMI flag cannot tell a doublet from a genuine *transdifferentiating* hepatocyte.** A
   hepatocyte converting toward biliary fate is *expected* to switch on KRT19/KRT7 — those are the exact
   markers Paper 1 stains for its biphenotypic cells. So this flag labels "doublet-suspect" and "the cell the
   paper calls transdifferentiating" identically. Inflated total count is **necessary but not sufficient** for
   a doublet (a cell co-expressing two full programs also carries more RNA). The honest statement is therefore
   *"rare co-capture OR rare biphenotypic cells — indistinguishable at this n,"* not "genuine doublets."
2. **The "inflated total count" is partly a selection artifact.** A nucleus must clear a ≥2-UMI gate on
   KRT19/KRT7 to be flagged, and higher-total-UMI nuclei mechanically clear any ≥2-UMI gate more often — so
   "suspects have higher median total UMI" is confounded with the definition. Also the F4 contrast is inflated
   on **both ends**: the "rest" median total UMI *falls* to 3,096 at F4 (lower-depth nuclei), so the "4.5×"
   gap is as much a denominator collapse as a numerator rise.
3. **The counts are tiny.** ~6 suspect nuclei at F4, 16 across all biopsy, single-digit EPCAM molecules — the
   "~17× rise" (0.01%→0.167%) is a ratio of 1 vs 6 noisy nuclei, and "2.9% of EPCAM" has no real CI. This is
   **directional/illustrative**, not a statistical estimate. A real doublet caller (e.g. scDblFinder) would be
   needed to quantify; the OR-gate here is a deliberately strict but arbitrary and self-confirming heuristic.

**What survives regardless:** the model-independent fact that **0 of 42,579 biopsy hepatocyte nuclei exceed
Paper 1's 50,000-count filter**, so whatever these co-capture nuclei are, that filter removed none of them;
and the genes are cholangiocyte-ambient by the cross-lineage burden audit (F18) independent of this leg.
This tests the **snRNA** leg only; it says nothing about Paper 1's imaging/co-staining evidence.
