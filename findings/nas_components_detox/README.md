# F6 — NAS components vs detox: the sharp test of the cytokine-CYP-suppression mechanism

**Status: QUARANTINED (2026-06-23).** The lead flagged this result as not-understood; it is held out of
all conclusions pending a joint talk-down (queue **O6**). The numbers below are reproducible and kept, but
**must not be cited** until we discuss what they mean (the inflammation-n.s. / ballooning-significant split
is confusing and may reflect collinearity, small n, or a metric issue). DO NOT USE.

_(original write-up retained below for that discussion)_

**Original framing — does NOT support the inflammation hypothesis; detox tracks ballooning instead.**
Data: [`nas_components_detox.csv`](nas_components_detox.csv). Script: `src/analysis/nas_components_detox.py`.

## The question (recovering the NAS analysis)
The disease axis we mostly used was fibrosis F0–F4. But NAS (and its **components** — Steatosis,
Ballooning, Inflammation — read by a pathologist from histology, **independent of the RNA**) was a
recommended *second* axis and was largely dropped. The sharpest free test of the pathologist's mechanism
hypothesis (end-stage detox loss = **cytokine/IL-6/TNF CYP-suppression**): if real, the **inflammation**
sub-score should predict detox loss **within biopsies** (orthogonal to fibrosis). Components are in the
metadata; NaN for explants + HL healthy, so this is naturally biopsy-only.

## Method
- Detox module = CYP2E1, CYP1A2, ADH4, AKR1D1, SLCO1B3 (xenobiotic drug-metabolism; excludes CYP3A4 = PC
  identity). Per-donor metric = mean **down-thinned to B=1,500 UMIs/cell** over hepatocytes (binomial thinning to
  B=1500, 4-draw MC). n = **38 biopsy donors**; detox_dm range 5.05–12.48.
- Spearman(detox, each NAS component) + partial(detox, inflammation | fibrosis).

## Result
| predictor | Spearman ρ | p |
|---|---|---|
| **Inflammation** | **−0.188** | **0.258 (n.s.)** |
| Ballooning | **−0.422** | **0.008** |
| Steatosis | −0.299 | 0.068 |
| Fibrosis | −0.321 | 0.050 |

partial(detox, Inflammation | Fibrosis) = **−0.104** (weak).

## Interpretation
- **The inflammation-driven CYP-suppression hypothesis is NOT supported in biopsy tissue** — inflammation
  is the weakest predictor and non-significant. So if cytokine-CYP-suppression is real, it is **not
  detectable across the biopsy spectrum** (would be an end-stage-only phenomenon, where it is confounded).
- **Detox loss within biopsies tracks BALLOONING** (hepatocyte degeneration/injury; ρ=−0.42, p=0.008,
  survives 4-test Bonferroni) more than inflammation — i.e. the modest within-biopsy detox variation
  follows hepatocyte injury, not the inflammatory infiltrate.
- Caveat: n=38, four predictors; ballooning is the one robust hit. This **tempers** the strong screenshot-5
  claim and is the biopsy-side evidence to weigh against it (see OPEN O5).
