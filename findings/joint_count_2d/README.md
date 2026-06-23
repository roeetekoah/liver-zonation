# F13 — The 2D joint-count "amount" view: what it does and does NOT show

**Status: LIVE, with an important correction.** Figure: `results/figures/h2/census_2d_joint.png`
(1934×1254). Script: `src/census/census_2d.py`. This is the "amount conviction" view the lead asked
about (real co-expression = high amounts of BOTH poles, not 1+1 ambient).

## What it is
Per nucleus, plot pericentral-**program** count (x) vs periportal-**program** count (y), down-thinned to
B=1,500. Intended reading: zonation = two separated clouds (PC-high/PP-low and PP-high/PC-low); de-zonation
= the both-high corner fills.

## The correction (caught on audit — scaling/threshold trap)
The PC/PP **programs are the broad 7+6-gene sums**, which include **broadly-expressed metabolic genes**
(CPS1, ALDOB, ASS1, the CYPs) that are ON in essentially every normal hepatocyte. So "both programs ≥ H" is
**not** a co-expression test — it is satisfied by most normal cells. Measured (down-thinned B=1,500,
donor-mean fraction with PC-prog ≥H AND PP-prog ≥H):

| | H≥2 | H≥3 | H≥5 |
|---|---|---|---|
| biopsy F0–F4 | ~0.80–0.84 | ~0.59–0.65 | ~0.17–0.31 |
| **Explant** | **0.43** | 0.30 | 0.17 |

So the both-high corner is **FULLER in biopsy than explant** — the opposite of "fills only in explants."
The explant is lower because it **collapsed to the PP-pole** (high PP, low PC). → The 2D joint-count is a
**pole-collapse visualization** (consistent with the manuscript's correct "collapses to a single periportal
pole only in explants" caption and the F9 polarization figure), **NOT** a clean co-expression test. The
screenshot reading "both-high corner fills = de-zonation" is **wrong for these broad-program genes.**

## Where the real "amount" conviction lives
The clean high-amount co-expression test uses the **strict mutually-exclusive anchor markers** (GLUL/CYP3A4
vs ASS1/PCK1/HAL/ALDOB) at the **ambient-robust ≥2-UMI** threshold (F8): real dual co-expression is
**≈0.2–0.6% in biopsy vs ≈2.9% in explant (~7×)**. That is what shows high-amount co-expression is near-
absent across biopsy disease and present only in explants — the lead's instinct ("amounts carry the
conviction"), satisfied by F8, not by the broad-program 2D.

## Crucial or just nice?
The **anchor ≥2 dual (F8) is CRUCIAL** — it is the conviction. The broad-program 2D figure is a useful
*pole-collapse* picture but must NOT be cited as a co-expression test. **Optional (O10):** rebuild the 2D
on the strict anchors at ≥2 UMI so the "high-amount corner empty in biopsy, fills in explant" is shown
directly and correctly.
