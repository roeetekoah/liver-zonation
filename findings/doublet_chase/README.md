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

## Conclusion
This **resolves the "residual unresolved" caveat in F18 in the ambient/compositional direction, and adds a
concrete QC gap in Paper 1.** The decontX survivors are **not** evidence of hepatocyte-intrinsic
transdifferentiation: most is diffuse ambient, the remainder is genuine hepatocyte–cholangiocyte doublets
that (i) accumulate with fibrosis and (ii) sit entirely below Paper 1's 50,000-count doublet threshold, so
their pipeline could not have removed them. Both sources are compositional consequences of the ductular
reaction (more cholangiocytes at F4 → richer soup + more co-capture), not a hepatocyte program.

**Caveats:** small-number analysis (only 16 suspects across all biopsy; F4 EPCAM totals are single-digit
molecule counts — directional, not a precise fraction). KRT19/KRT7 ≥2 is a deliberately strict, high-
confidence doublet definition; looser thresholds would label more nuclei but blur the doublet/ambient line.
This tests the **snRNA** leg only; it says nothing about Paper 1's imaging/co-staining evidence.
