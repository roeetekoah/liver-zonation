# F19 — The zonation-preservation claim, in full (what we say, how it's grounded, what it is NOT)

**Status: LIVE.** The single stable claim (Decision D3):
> **Across acquisition-matched biopsy MASLD (fibrosis F1 → cirrhotic F4), hepatocyte gene-expression
> zonation is preserved** — meaning no detectable change AND large coordinated shifts affirmatively excluded.

"Preserved" rests on **three independent grounds**, each below; then the precise meaning of the equivalence
bound; then "what this claim is NOT."

## Ground 1 — the zonation marker GENES show no detectable change (expression level)
Genome-wide donor-level test (pseudobulk per donor + edgeR with TMM normalization and a negative-binomial
quasi-likelihood test — the method Squair et al. 2021 recommend): every zonation/detox gene is
non-significant at F4-vs-F1. **Verbose (FDRs from `dge_planA_F4vsF1.csv`):** the pericentral master gene
**GLUL has FDR = 0.803** (far above the 0.05 significance cut → if we called genes "changed" at GLUL's level,
about 80% would be false; so GLUL shows no detectable change); **CYP3A4 FDR = 0.85, CYP2E1 = 0.90, ASS1 =
0.96, CPS1 = 0.92** — all flat; the lowest of the set are the detox genes **ADH4 = 0.43, SLCO1B3 = 0.57**,
still non-significant; fold-changes small (log2 −0.1 to −0.6, i.e. ≤1.5× either way). (An earlier draft wrote
"GLUL FDR = 0.43" — that is ADH4's value, not GLUL's; corrected.) These are high-expression genes where the
n=4 power limit does not bite, so the flatness is genuine evidence. Sources: F15, F18; held also after
decontX (0/13 significant) and in the F1→F3 interior (0/13).

## Ground 2 — the zonal-classification PROPORTIONS are flat across every threshold
Per-nucleus zonal-anchor classification (PC / PP / null / dual) + donor-level proportions, after binomial
down-thinning every nucleus to a common 1,500-UMI budget. The pericentral-anchor fraction is flat /
non-monotone across biopsy stages — **donor-median 36% / 19% / 23% / 22% / 21% for F0/F1/F2/F3/F4** — and
this holds across the WHOLE sensitivity grid (anchor = GLUL-only / CYP3A4-only / both; threshold k=1 or 2;
periportal rule 2-of-4 / 3-of-4 / CPS1-based; ALDOB in/out). The apparent "co-expression" (dual) is **ambient
soup**: ~7–10% at a 1-UMI threshold collapses to **0.2–0.6%** at the ambient-robust ≥2-UMI threshold. Source: F8.

## Ground 3 — the affirmative EQUIVALENCE BOUND (this is what licenses the word "preserved")
A null ("nothing was significant") is not, by itself, proof of preservation — so we add an equivalence test
(F16). **Plain explanation of "we exclude a coordinated shift larger than ~±0.15 of the compartment":**
- We take the per-donor pericentral-anchor fraction and compute the **change from F1 to cirrhotic-F4**:
  observed difference **Δ = +0.024** (i.e. +2.4 percentage points of hepatocytes), with a **90% confidence
  interval of −0.147 to +0.194**.
- A confidence interval is the range of true values compatible with our data. Because that interval **does
  not extend beyond about ±0.19**, any *true* shift **larger than ±0.19 of the compartment** would have
  pushed our measurement outside this interval — we would have seen it, and we did not. **That is what
  "exclude a shift larger than ~±0.15–0.19" means:** a de-zonation that moved >15–19% of hepatocytes between
  poles is statistically ruled out. The better-powered **F1→F3 interior tightens this to ±0.12** (90% CI).
- Scale anchor: the explant "collapse" we *do* see moves the pericentral fraction by **~0.3–0.5** (30–50
  points) — far outside our bound. So we exclude an explant-scale collapse in biopsy; we cannot exclude a
  *small* drift.

## What this claim is NOT (caveats — read these with the claim)
1. **Not "unchanged to the last percent."** A modest coordinated drift of **≤±0.10** (≤10 points) is NOT
   excluded (donor-to-donor spread is too large at F4 n=4). We exclude *large* change, not *all* change.
2. **Not spatial/architectural preservation.** snRNA measures per-cell transcriptional balance, not lobule
   geometry; a needle core cannot see septa/perivenular remodelling. We claim the *gene-expression* signal,
   not the *spatial* architecture.
3. **Not a per-gene guarantee for every zonated gene** — GLUL is dropout-prone in snRNA (detection ~0.18) and
   CYP3A4 covaries with detox; the claim rests on the *set* + the proportions, not one fragile marker.
4. **Single cohort, no protein/independent validation** of the transcriptional null.
5. Scope: **biopsy F1→cirrhotic-F4 only.** End-stage explants are excluded (procurement/stress/batch
   confounds); we say nothing about them here.
6. **Not a test of the paper's actual co-expression readout.** Paper 1's de-zonation metric is a *marker–marker
   correlation* breaking down (cells co-expressing both poles), not the pole *proportion* we measure. A flat
   proportion (36/19/23/22/21%) is consistent with — but does not by itself rule out — a rise in the *fraction
   of cells co-expressing both poles*. We address that separately with the ambient-robust ≥2-UMI dual fraction
   (F8: 0.2–0.6%, flat), but the proportion alone is not the same instrument as their correlation test.
7. **Needle-core sampling-axis caveat (raised by review, not separately tested).** A 16-gauge core may not
   traverse the full central-vein→portal-tract lobule axis, so a flat pericentral/periportal proportion could
   in principle reflect *what the needle sampled* rather than preserved zonation. The lobe-invariance result
   (F1) and the across-many-donors consistency argue against a systematic per-core bias, but we have not
   directly modelled needle-track position — flagged as an untested alternative.
8. **Regeneration as a third option for the biliary markers (not separately tested).** Beyond "ambient" vs
   "hepatocyte transdifferentiation," the paper frames biphenotypic cells as *regenerative*; regeneration-
   associated biliary-marker induction is a hepatocyte-intrinsic possibility our compositional/ambient analysis
   does not separately distinguish from ductular ambient. (Bears on F18/F21, not on the zonation null itself.)
