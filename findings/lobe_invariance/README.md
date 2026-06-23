# F1 — Lobe sampling: the zonation pattern is lobe-invariant; primary analysis is right-lobe-only

**Status: LIVE (with a caveat on absolute levels).** Data: [`lobe_invariance.csv`](lobe_invariance.csv).
Reproduced by `src/analysis/lobe_invariance.py` from the saved per-(donor,lobe,stage,gene) table
`results/tables/analysis/rawA_donor_lobe_stage_gene.csv` (built by `src/analysis/raw_counts.py`).

## Why lobe matters — what the caudate lobe is (sampling context)
The end-stage explants were sampled from **three lobes (Right + Left + Caudate)**; every disease needle
biopsy is **Right lobe only** (see [`../../CLAIMS_LEDGER.md`] tissue-source entry). The **caudate lobe**
(Couinaud **segment I**) is anatomically and hemodynamically *distinct*: it sits on the posterior liver
between the ligamentum-venosum fissure and the IVC groove; it has a **dual blood supply** (from both
right and left portal veins / hepatic arteries) and **drains directly into the IVC** via small veins
rather than through the three main hepatic veins; and it is **often relatively spared and hypertrophied
in cirrhosis**. So caudate tissue is *not* interchangeable with right-lobe parenchyma — which is exactly
why multi-lobe explant sampling was a candidate confound for the apparent de-zonation.
Sources: Radiology Assistant (liver segmental anatomy); Mao et al., *Quant Imaging Med Surg* (PMC7930664).

## What the numbers are (metric definitions)
Within **end-stage explant** hepatocytes (5 donors, each contributing Right+Caudate+Left), per gene,
mean across donors per lobe:
- **frac_{lobe}** = fraction of that lobe's hepatocyte nuclei with **raw UMI > 0** for the gene (detection rate).
- **umi10k_{lobe}** = pseudobulk **raw UMIs of the gene per 10,000 total UMIs** in that lobe (burden).
- **umi10k_rel_spread** = (max−min)/mean of the burden across the three lobes (0 = identical; lobe-invariance index).

## The finding
- **Detection is lobe-invariant.** e.g. GLUL frac 0.350 / 0.343 / 0.297 (R/C/L); ALDOB 0.821 / 0.837 / 0.838;
  CPS1 0.826 / 0.874 / 0.879. The *same markers are on/off* in every lobe — no lobe turns the zonation
  program on or off.
- **The end-stage zonation pattern is fully present in Right-lobe-only cells**, so the multi-lobe /
  caudate sampling is **not manufacturing** the apparent de-zonation signal.
- **Caveat (honest):** absolute *burden* shows moderate per-lobe variation — median |max−min|/mean ≈ **0.36**
  across genes, up to ~0.5 for a few (e.g. CYP3A4 8.75 / 9.78 / 14.13; ASS1 3.41 / 4.19 / 5.71). It is
  unsystematic and not in a direction that creates de-zonation, but "invariant" applies cleanly to
  detection/pattern, not to exact expression level.

## Scope of what this clears
Clears **only the lobe sub-confound** (caudate/multi-lobe sampling is not the cause). It does **not**
clear the separate, larger **explant-vs-biopsy sampling-mode / procurement-stress confound**, which is a
different axis (see the tissue-source finding).

## Right-lobe-only restriction (related, confirmed)
The primary across-stage raw-count result is computed **right-lobe-only**: `raw_counts.py` line 78 builds
`dA_right = donor_stage(hep[hep["lobe"]=="Right"], "right")` and the "(B) RIGHT-LOBE-ONLY primary result"
uses it. Downstream anchor-classification/DE restrict to needle-biopsy donors, which are right-lobe **by construction**
(Caudate/Left appear only in healthy HL1 and the explants).

## Honest note on provenance
An earlier **inline** lobe table (GLUL 0.43/0.43/0.33, CYP2E1 0.97/1.01/0.82, …) used an unsaved,
ambiguously-scaled metric and **could not be reproduced** from any saved quantity. It is **discarded** in
favour of the defined `frac_raw_pos` / `UMIs_per_10k` table here. The lobe-invariance *conclusion* is
unchanged and holds on both defined metrics.
