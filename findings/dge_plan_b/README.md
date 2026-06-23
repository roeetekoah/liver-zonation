# F20 — Plan B: within-class DGE (does the program shift INSIDE a stable zonal population?)

**Status: LIVE but SUBORDINATE to Plan A (robustness check, largely confirmatory).** Script
`src/dge/plan_b_within_class.R` → `dge_planB_{PC,PP,null,dual}_F4vsF1.csv`.

**Why this is subordinate, not a co-equal second finding (reasoned).** Plan A pools all of a donor's
hepatocytes; Plan B first labels each hepatocyte by zone and pseudobulks *within* each label. The only thing
Plan B can catch that Plan A cannot is a **within-zone program masked by pooling** — and pooling masks a
within-zone change *only if zone composition also shifts* to cancel it (an aggregation/Simpson effect). But we
have already established that **zone proportions are flat across F1→F4 (F8)**, so there is no composition shift
for pooling to hide behind, and Plan A and Plan B are *expected* to agree — which they do. So Plan B is mostly
**confirmatory of A**, not independent evidence. Its one genuinely useful job is to **foreclose the specific
question a reviewer will ask** — "could a disease program hide inside a zone?" — answered cleanly: no. (Its
other output, that the biliary burden is class-agnostic, was corroboration for the *source-attribution*
sub-leg, which is downweighted.) **Recommendation: report Plan A as the DGE finding and keep this as a short
within-zone robustness paragraph under it; do not present A and B as two separate headline analyses.**
Each biopsy hepatocyte nucleus is classified PC / PP / null / dual by ambient-robust (≥2-UMI) anchor
detection; then the full transcriptome is pseudobulked per donor WITHIN each class and tested F4-vs-F1 with
edgeR (TMM + negative-binomial quasi-likelihood); classifier genes (GLUL,CYP3A4,ASS1,PCK1,HAL,ALDOB) excluded;
≥30 nuclei/donor-class required. **Read alongside the class proportions (F8): a flat within-class result is
interpreted together with whether the class COUNT moved.**

## Result
Hits FDR<0.05 by class (F4-vs-F1): **PC 43, PP 18, null 6, dual 32.** In **every class, 0 of 13 zonation
genes are significant** → within a stable zonal population the zonation genes do not change.

**The key observation:** the hits are the SAME biliary/epithelial set across all four classes — **GRHL2 is
the top hit in PC, null and dual; SPINT2 tops PP; EPCAM, ESRP1, CATSPERB, KRTAP5-AS1 recur in every class.**
The program is **class-agnostic** — it appears in pericentral, periportal, null and dual nuclei alike.

**Honest logic (corrected after adversarial review):** class-agnosticism rules out a *zone-specific* intrinsic
program, but it does **NOT** by itself distinguish "uniform ambient" from a *uniform pan-zonal*
transdifferentiation — a genuine program acquired by hepatocytes everywhere would also look class-agnostic.
So Plan B is **corroborating, not decisive.** The decisive evidence for the ambient reading is elsewhere: the
**cross-lineage burden** (these genes are 5–65× cholangiocyte-dominant, F18) and the **per-cell co-expression
≤0.4%** (F8) — Plan B's class-agnosticism is *consistent with* that, not independent proof of it.

## Interpretation
- **Corroborates (does not prove) the ambient reading (F18):** the within-class signal is the same
  class-agnostic biliary/epithelial program — consistent with ambient, but the weight is carried by the
  cross-lineage burden + per-cell evidence, not by class-agnosticism alone.
- **No within-class hepatocyte-intrinsic disease program** beyond that (largely ambient) biliary set; and
  zonation genes flat inside every class.
- Honest limit: classification is a thresholded label, so within-class results are **conditional** and read
  jointly with the class proportions; within-class p-values are descriptive (same donors recur across classes,
  not BH-corrected across the 4 classes as if independent).
