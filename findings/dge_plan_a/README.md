# F18 — Plan A: genome-wide discovery DGE across biopsy fibrosis (edgeR)

**Status: LIVE.**
Script `src/dge/plan_a_genomewide.R`; data `results/tables/analysis/dge_planA_F4vsF1.csv` (+ omnibus).
Method: pseudobulk per donor (sum raw UMIs over each donor's hepatocytes) → **edgeR with TMM library-size
normalization + a negative-binomial quasi-likelihood gene-by-gene test (robust dispersion)**, the pseudobulk
approach Squair et al. (Nat Commun 2021) show avoids the false-positive inflation of per-cell tests. 38 biopsy
donors (all ≥50 hepatocyte nuclei; F0–F4 = 2/8/12/12/4 donors), 21,022 genes retained by `filterByExpr`,
common biological coefficient of variation 0.405. Primary contrast = **cirrhotic F4 vs F1**; an across-all-
stages omnibus is secondary.

## Purpose & framing — a discovery scan whose null ALSO independently corroborates preserved zonation
This analysis has one primary job and one genuine bonus, and they should be kept distinct.

**Primary job — discovery.** Zonation preservation is already established by the count-based instruments
(anchor classification flat across the whole sensitivity grid F8; marker-set invariance F1; donor-balanced
gradient F9; equivalence bound F16). Taking that as settled, the genome-wide DGE asks a *different* question:
**given preserved zonation, does any OTHER coordinated hepatocyte program shift across the matched needle-biopsy
axis F1 → cirrhotic-F4?**

**Bonus — independent corroboration of preserved zonation (NOT a mere sanity check).** Because the scan tests
every gene, it also tests the zonation markers, and they come back flat *at the expression level*, with
strikingly non-significant FDRs, while the housekeeping controls are flat and the rest of the genome behaves.
This is **not the primary proof** of preservation (the count instruments are) — but it is also **far more than a
pipeline sanity check.** It is a genuine **second, independent line of support**, from a method (per-gene
donor-level expression with edgeR/TMM) that shares no machinery with the count-based anchor instruments. Two
independent methods agreeing that the zonation genes do not change is real corroboration, and we state it as
such.

## Headline result — two parts
**(1) Zonation is kept — independently corroborated.** Every zonation/detox gene is non-significant at
F4-vs-F1 (numbers below), the housekeeping panel is flat, and nothing in the rest of the genome rediscovers
the original de-zonation. A genome-wide expression scan independently agrees with the count-based preservation
claim.

**(2) Beyond zonation, essentially nothing else moves — except a biliary-marker burden (and one candidate
inflammatory gene).** Of ~21,000 genes only **64 reach FDR<0.05** at F4-vs-F1, and they are a biliary/ductular
marker set (EPCAM, GRHL2, SPINT2, SOX4, SOX9, B3GNT3) — exactly the markers Paper 1 flagged — plus CXCL10.
**The careful reading (ChatGPT item 5): this scan detects a biliary-MARKER BURDEN inside hepatocyte-labeled
pseudobulk; it does NOT, by itself, prove or measure hepatocyte "plasticity."** Whether that burden is
cholangiocyte ambient RNA, rare doublets, or genuine rare hepatocyte expression is a **separate source-
attribution question**, explored at lower depth in a sub-finding (below) — that exploration is a promising
**lead, not the point of this finding**, and was only crudely probed. CXCL10 stands apart from the biliary
set: its hepatocyte expression does not track the cholangiocyte fraction (correlation −0.09 vs +0.24..+0.68),
so it is a **candidate real inflammatory signal**, not biliary/ambient.

**The key open caveat on part (2) — gene-level FDR ≠ "no program."** "Nothing else moves" is a *gene-level*
statement: no single gene outside the biliary set crosses FDR. Gene-level DGE can still miss a **coordinated
weak program** — tens-to-hundreds of genes each shifting modestly (a whole pathway dimming a little) without
any one gene reaching significance. To claim "no other hepatocyte program" with full confidence we need a
**gene-set / pathway-level layer** (CAMERA for competitive enrichment; ROAST/mroast for self-contained
pre-specified signatures) over the standard hepatocyte programs — detoxification, urea cycle, bile-acid and
lipid metabolism, ER stress, interferon/inflammation, hypoxia, mitochondrial, cell-cycle, senescence, EMT,
fetal/progenitor, cholangiocyte/ductular. **Until that runs, the honest claim is: "no single-gene program and
no large coordinated change (> ~2-fold); a coordinated *weak* program is not yet formally excluded."**
[OPEN — O13; decision pending: future work vs run now.]

**Power note (bounds the single-gene null).** "No other program" at the gene level means **none larger than
~2-fold** (log2 ≈ 1): at common biological-variation 0.405 with F4 n=4 / F1 n=8 the realized detection floor
is roughly a 2-fold coordinated change. The well-populated F1–F3 interior (n=8/12/12) is also near-flat, so
two looks agree — but neither rules out subtle effects, which is exactly why the gene-set layer (O13) matters.
(Secondary detail: the across-all-stages omnibus finds 91 genes FDR<0.05 vs 64 for F4-vs-F1; the biliary genes
are an F4-weighted jump, not a smooth gradient — e.g. EPCAM log2 vs F1 = +0.6 at F2, +0.7 at F3, **+2.3 at
F4** — consistent with a cirrhosis-stage ductular reaction.)

## Results (detail)
- **Independent corroboration — zonation + housekeeping flat at the expression level.** Every zonation/detox
  gene is non-significant at F4-vs-F1. Verbose, from `dge_planA_F4vsF1.csv`: **GLUL FDR 0.803** (logFC −0.33),
  CYP3A4 0.851, CYP2E1 0.903, ALDOB 0.846, CPS1 0.920, ASS1 0.962 — all far above the 0.05 cut. The lowest
  detox FDRs are **ADH4 0.428** (logFC −0.54) and SLCO1B3 0.571 (−0.64) — still non-significant. (Earlier
  drafts mis-stated "GLUL FDR 0.43"; 0.43 is ADH4's value, GLUL is 0.80 — corrected here and in F19.) No
  housekeeping gene is FDR-significant (ACTB mildly up +1.06 but FDR 0.33; GAPDH/MALAT1/PPIA/TBP flat). These
  are high-expression genes where the n=4 power limit does NOT bite, so their flatness is **genuine evidence**,
  not absence of power — a second, independent method agreeing with the count instruments (not a re-proof, and
  not a mere pipeline check). One honest limit (ChatGPT item 4): housekeeping flatness shows normalization is
  sound, which is necessary but not the same as proving the model is perfectly specified.
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
doesn't model; rises with cirrhosis), or (c) genuine low-level hepatocyte expression. → We CANNOT say "the
biopsy transdifferentiation signal is artifact," but we CAN say the *biliary/epithelial* part is **not
hepatocyte-intrinsic** (F21 below).

**CXCL10 is the exception — treat it as inflammation, NOT biliary/ambient (correction after adversarial review).**
The compositional audit (`dge_planA_compositional.csv`) stamped CXCL10 "ambient" because it keys on cross-lineage
burden alone (CXCL10 is 7.8× cholangiocyte-over-hepatocyte). But CXCL10's **`corr_hepCPM_vs_cholFrac = −0.09`** —
the only *negative* value among the hits (EPCAM +0.34, GRHL2 +0.36, SOX4 +0.33, KCNJ16 +0.68): its expression in
hepatocyte pseudobulk does **not** rise with the cholangiocyte fraction, so it does **not** behave like spillover
from the expanding cholangiocyte pool. CXCL10 is an interferon-γ-induced chemokine, a classic NASH/cirrhosis
inflammation gene. It has the largest fold-change in the set (log2 +5.4) and survives decontX (FDR 0.002). So the
"ambient" verdict for CXCL10 is **wrong**, and lumping it into the biliary story made our headline cleaner than
the data support: there is at least a **candidate inflammatory axis** that changed across the biopsy disease axis.
(The verdict rule should require high burden AND positive cholangiocyte-fraction correlation to call "ambient" —
a fix for the audit script. Other negative-correlation genes, if any, deserve the same separate treatment.)

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
