# F18 — Plan A: genome-wide discovery DGE across biopsy fibrosis (edgeR)

**Status: LIVE.**
Script `src/dge/plan_a_genomewide.R`; data `results/tables/analysis/dge_planA_F4vsF1.csv` (+ omnibus).
Method: pseudobulk per donor (sum raw UMIs over each donor's hepatocytes) → **edgeR with TMM library-size
normalization + a negative-binomial quasi-likelihood gene-by-gene test (robust dispersion)**, the pseudobulk
approach Squair et al. (Nat Commun 2021) show avoids the false-positive inflation of per-cell tests. 38 biopsy
donors (all ≥50 hepatocyte nuclei; F0–F4 = 2/8/12/12/4 donors), 21,022 genes retained by `filterByExpr`,
common biological coefficient of variation 0.405. Primary contrast = **cirrhotic F4 vs F1**; an across-all-
stages omnibus is secondary.

## Purpose & framing — this is a DISCOVERY scan, NOT a zonation re-test
Zonation preservation is **already established** by the count-based instruments (anchor classification flat
across the whole sensitivity grid F8; set-invariance F1; donor-balanced gradient F9; equivalence bound F16)
and is treated here as a **settled premise.** This genome-wide DGE asks a *different* question: **given that
zonation is preserved, does ANY other coordinated program shift across the disease axis** — on some axis
other than zonation, or within a zone? Because a genome-wide test scans *all* ~21,000 genes, the zonation
genes are necessarily included — but their flatness here is a **built-in sanity / negative-control check**
(it shows the edgeR pipeline does not manufacture significance where the count instruments already found
none, and is internally consistent with the premise), **NOT the deliverable and NOT independent proof of
zonation.** The deliverable is the answer to "what else changes?" — see the headline below.

## Headline result — nothing changes beyond the (already-known, compositional) plasticity set
Across all ~21,000 genes, the **only** coordinated F1→F4 program that surfaces is the biliary/plasticity set
that **Paper 1 already described** — and our follow-up scans (below) show that set is **compositional
(cholangiocyte ambient + doublets), not a hepatocyte-intrinsic program.** Subtracting it, **no other
coherent hepatocyte program reaches significance** across the biopsy disease axis. We state that **with
confidence for moderate-to-large coordinated changes** (and note the honest power limit at F4 n=4 lower down).

## Results (detail)
- **Sanity / consistency check — zonation + housekeeping flat (NOT the deliverable).** Every zonation/detox
  gene is non-significant at F4-vs-F1 (FDR 0.43–0.96): GLUL, CYP2E1/3A4, CPS1, ASS1, ALDOB flat; detox genes
  small negative logFC (ADH4 −0.54, SLCO1B3 −0.64) but none survive FDR. No housekeeping gene is
  FDR-significant (ACTB mildly up +1.06 but FDR 0.33; GAPDH/MALAT1/PPIA/TBP flat). Together these confirm the
  pipeline is calibrated and consistent with the established premise — they do not re-prove zonation.
- **Discovery: 64 genes FDR<0.05 (62 up).** The program is **biliary / ductular / transdifferentiation**:
  **EPCAM +2.3, GRHL2 +3.1, SPINT2 +2.7, B3GNT3, SOX4, SOX9**, + inflammation **CXCL10 +5.4**. This is the
  ductular reaction of cirrhosis — and **SOX4/SOX9/EPCAM are exactly Paper 1's plasticity/transdifferentiation
  markers** (their actual headline).
- **MDS pre-flight (batch, F17):** neither SLX run nor fibrosis dominates the leading axis (run does not drive
  the main variance — reassuring); one outlier donor flagged for leave-one-donor-out.

## This REVISES an earlier claim (F10 / manuscript §C)
We previously said the transdifferentiation markers (KRT7/KRT19/EPCAM/SOX4) are "flat across biopsy F1–F4,
rising only in end-stage explants." **That was on a detection-fraction metric and is wrong at the expression
level:** proper edgeR pseudobulk shows EPCAM/SOX4/SOX9/GRHL2 **significantly UP into cirrhotic F4 biopsy.** So
the biliary program is **not** confined to explants — it rises in acquisition-matched cirrhotic biopsy too.

## Why we suspected ambient (the 3 circumstantial reasons → motivation for the decontX re-analysis)
The 64 hits looked like Paper 1's plasticity program, so we asked whether the molecules were *made by
hepatocytes* or are *ambient spillover*. Three reasons pointed to ambient and motivated running decontX:
1. **Cell-type identity:** the markers are cholangiocyte genes — after binomial down-thinning every nucleus
   to a common 1,500-UMI budget (so the comparison is not driven by library-size differences), cholangiocytes
   carry 5–65× more (e.g. EPCAM 0.0695 vs hepatocyte 0.0034 mean UMIs/nucleus = 20×). So in the shared ambient "soup"
   these molecules come mostly from cholangiocytes.
2. **F4-specific timing:** cholangiocytes proliferate in cirrhosis (their fraction rises ~1% at F0 → 8.3% at
   F4, the ductular reaction), so the soup gets richer in cholangiocyte RNA exactly at F4; and in the F1→F3
   interior EPCAM is flat (FDR = 0.77 → no detectable change).
3. **Per-cell rarity:** only ~0.4% of hepatocyte nuclei carry ≥2 biliary-marker molecules (F8) — a thin
   smear across many nuclei, not many hepatocytes switching the program on.

## decontX RESULT — partly ambient, partly unresolved (NOT cleanly all-ambient)
`src/dge/decontX_replan_a.R` → `dge_planA_decontx_F4vsF1.csv` (+ `pseudobulk_hep_decontx.csv`). decontX
estimated **mean per-cell contamination 8.7% (hepatocytes 5.1%)**; removing it and re-running edgeR F4-vs-F1:
- hits 64 → **34**; **zonation 0/13 significant** (sanity: decontX did not distort the matrix).
- **SOX4 and SOX9 — the canonical transdifferentiation TFs — dropped BELOW significance** (SOX4 FDR 0.131,
  SOX9 FDR 0.118; both now above the 0.05 cut → no longer detectable) → consistent with **ambient**.
- **EPCAM (FDR 0.010), B3GNT3 (0.004), SPINT2 (0.005), CXCL10 (0.002) SURVIVED** → **not fully ambient.**
**Honest conclusion (do not overclaim):** ambient removal explains a substantial part — notably SOX4/SOX9 —
but a **residual epithelial/inflammatory signal survives** whose source we then resolved (F21): (a) residual
ambient decontX under-corrected, (b) **hepatocyte–cholangiocyte doublets** (high-copy co-capture decontX
doesn't model; rises with cirrhosis), or (c) genuine low-level hepatocyte expression. CXCL10 (+5.2) may be
real inflammation, not biliary. → We CANNOT say "the biopsy transdifferentiation signal is artifact," but
we CAN say it is **not hepatocyte-intrinsic** (F21 below). 

**Doublet chase (F21) resolves the residual toward (a)+(b), away from (c).** Defining doublet-suspects as
hepatocyte nuclei co-detecting cholangiocyte structural markers (KRT19 or KRT7 ≥2 UMI): they **exist and
rise ~17× with fibrosis** (0.01%→0.167% F1→F4) and carry the doublet signature of **inflated total counts**
(F4 median 14,065 vs 3,096 ordinary, ~4.5×; ambient does not inflate library size, so these are genuine
co-captures). **Paper 1's "remove >50,000 counts" filter catches none of them — 0 of 42,579 biopsy
hepatocyte nuclei exceed 50,000.** But the suspects are too rare to be the main driver: they carry only
**~2.9% of F4-hepatocyte EPCAM**; the other ~97% is the diffuse ambient smear. So the residual = mostly
ambient + a small fibrosis-rising doublet contribution Paper 1 could not have removed — **neither is
hepatocyte-intrinsic transdifferentiation.** (Full numbers, caveats: F21.)

## What Paper 1 did about this (verbatim, no memory)
Their snRNA QC = CellRanger v5.0.0 + Seurat v4.0.3. They used **no computational ambient-RNA removal** (no
SoupX/decontX/CellBender — verified: zero occurrences in Methods/refs) and **no dedicated doublet-detection
algorithm** (no Scrublet/DoubletFinder/scDblFinder) — only a **crude count-threshold doublet filter**:
*"nuclei with more than 50,000 counts were also removed."* They state *"Quality control was performed to
confirm that these cells were not the result of doublets or RNA contamination,"* but the contamination check
is unspecified and their positive evidence for the biphenotypic cells is the **tissue imaging**. So **we ran the specific ambient test
they did not** — and it shows their snRNA co-expression signal is, in part (SOX4/SOX9), attributable to
ambient. This does **not** refute their imaging; it shows the snRNA leg is not cleanly hepatocyte-intrinsic.
Compositional audit (`src/dge/dge_planA_compositional.py` → `dge_planA_compositional.csv`; cross-lineage
burden over all 99,809 nuclei, `prep/11`): **54 of 64 hits are ambient, 7 mixed, only 3 intrinsic.** Every
headline marker is massively **cholangiocyte-dominant** (UMIs/10k, cholangiocyte vs hepatocyte): GRHL2 **78×**,
EPCAM 25×, B3GNT3 18×, SOX9 15×, SPINT2 9×, CXCL10 8×, SOX4 7×. The cholangiocyte fraction is elevated at
cirrhotic F4 (median 8.3% vs ~2–4% earlier; the ductular reaction). So the F4 hepatocyte-pseudobulk "rise" in
these genes is **spillover from the expanding cholangiocyte population**, not hepatocyte transdifferentiation.
- The 3 "intrinsic" hits (LINC02365, TREH, SLC6A11) are scattered, low-burden, not a coherent program → noise.
- **Conclusion: no hepatocyte-INTRINSIC disease program in the biopsy F1→F4 axis.** Combined with the per-cell
  evidence (hepatocytes do not co-express biliary markers — biliary panel ≤0.004 by anchor class, F8/load_bearing),
  **we do NOT confirm Paper 1's hepatocyte transdifferentiation in acquisition-matched biopsy tissue** — the
  apparent plasticity signal is **cholangiocyte ambient (ductular reaction)**, compositional.
- **Honest bound:** pseudobulk + per-cell co-expression both show no hepatocyte-intrinsic transdiff program;
  but pseudobulk cannot rule out *rare* individual transdifferentiating cells (would need targeted per-cell
  analysis). Batch/LOO checks on these hits are moot — they are ambient regardless of run.

## Library-size-controlled confirmation (belt-and-suspenders) + the F1–F3 interior
- **After binomial down-thinning every nucleus to a common 1,500-UMI budget** (mean UMIs/nucleus): EPCAM 20×, GRHL2 65×,
  SOX9 13×, SPINT2 9×, SOX4 7.5×, CXCL10 5× cholangiocyte-over-hepatocyte — same as the per-10k version, so
  the cell-identity conclusion is robust to the normalization choice. EPCAM is a cholangiocyte-identity gene
  at **baseline, healthy included** (pooled hep 0.018 vs cholangiocyte 0.45 /10k = 25×) — not disease-induced
  in hepatocytes.
- **F1–F3 interior contrast** (`plan_a_interior.R`, pre-cirrhotic): **F3-vs-F1 = only 3 genes FDR<0.05**
  (scattered noise, no program); **the biliary markers are non-significant** (EPCAM FDR 0.77, SOX4 0.78,
  GRHL2 0.78); **zonation 0/13 significant**. F2-vs-F1 = 11 scattered lincRNAs, no program. → the biliary
  signal is a **cirrhosis/F4-specific** phenomenon; pre-cirrhotic biopsy is near-flat. Confirms F4 dominated
  the F4-vs-F1 contrast.

## We neither confirm NOR refute Paper 1's transdifferentiation (important)
"More cholangiocytes at F4" is **NEUTRAL** — it can come from a **ductular reaction** (cholangiocytes
proliferating; standard cirrhosis biology) OR from **transdifferentiation** (hepatocytes becoming biliary;
Paper 1's claim). snRNA pseudobulk **cannot distinguish them**. Our ambient finding only says the biliary RNA
*inside hepatocyte-annotated nuclei* looks like spillover → **no positive evidence of transdifferentiation in
those nuclei** — but we **cannot rule out** that the extra cholangiocytes arose from hepatocytes (needs
lineage tracing). Same shape as F10: a cautionary note on one transcriptional leg in biopsy, NOT a refutation;
their imaging/co-staining/organoid evidence is untouched.

**Credit where due — the paper already localized transdifferentiation to end-stage.** Paper 1 states the
*"full phenotype... seems to be acquired only towards the end stage of progression"* and that transdifferentiating
cells are *"observed mainly in end-stage livers."* Their one across-stage trend (Fig 3e, proportion of
"cholangiocyte-like hepatocytes" by stage, Welch's t, **P = 0.03058**) **pools all 47 donors including the
procurement-confounded healthy + end-stage groups** and is, by their own text, end-stage-driven. So on the
transdifferentiation leg we are largely **agreeing with the paper's own scoping** (strong signal = end-stage,
the tissue we both treat as special) and only **adding** that the *modest biopsy-stage* biliary rise is largely
ambient/ductular — not overturning a biopsy-transdifferentiation claim they never strongly made. (decontX done,
above: partly ambient, residual unresolved.)

## The "is there any OTHER hepatocyte program?" result, stated honestly (document verbatim)
We tested all ~21,000 expressed genes for an F4-vs-F1 change; only **64 reached FDR<0.05**, and those are the
(ambient-looking) biliary set. Everything else was tested and **did not** cross the bar → no *other* coherent
hepatocyte program reached significance. **Honest limit:** with **F4 n=4** we are powered for moderate-to-large
coordinated changes, not subtle ones — a weak program could sit below threshold. **But** the F1–F3 interior
(better balanced, no F4) is *also* near-flat — two independent looks agree. So: **"well-supported, not certain."**

## Reconciliation with F10
F10's *spirit* holds (no established hepatocyte-intrinsic transdifferentiation in matched biopsy), but its
*wording* ("markers flat across biopsy") was wrong: at the expression level they rise into F4 biopsy — as
ambient. Update F10/manuscript §C to: "the biliary/transdifferentiation markers rise into cirrhotic F4 biopsy
**as cholangiocyte ambient (ductular reaction), not hepatocyte-intrinsic** (cross-lineage 7–78× cholangiocyte-
dominant; hepatocytes do not co-express them)."
