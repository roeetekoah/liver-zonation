# F2/F3 — Stress-by-sampling confound + end-stage gene shape (ROBUST, donor-level, scaled)

**Status: LIVE.** Robust rebuild (down-thinned to B=1,500 + ambient-robust) of the old raw "fraction expressing" /
stress-by-stage tables, which used deprecated metrics (raw mean, ≥1 detection, UMIs_per_10k, medians).

**Data** · `per_donor.csv` (right-lobe, all panel genes, per-donor exact) · `per_group.csv` (right-lobe
group summary: mean across donors + min/max) · `stress_per_donor_alllobe.csv` (all-lobe, every donor's
exact stress — keeps the 2 no-lobe healthy donors).
**Scripts** · `src/confound/panel_by_stage.py` · `src/confound/stress_exact.py`.
**Source** · raw RNA UMIs `raw_panel_counts.csv` (prep/05) + Disease.status from metadata.

## Metric definitions (every number's scale)
| metric | meaning | robustness |
|---|---|---|
| `raw_mean` | mean **raw** UMIs / nucleus | DEPRECATED (provenance only) |
| `det1` | fraction of nuclei with UMI **≥ 1** | pre-robust detection |
| `det2` | fraction of nuclei with UMI **≥ 2** | **ambient-robust** detection ✔ |
| `dm_mean` | mean **down-thinned to B=1,500** UMIs/nucleus (binomial thinning to B=1500, 4-draw MC) | **robust** ✔ |
| `dm_det1` | fraction with down-thinned to B=1,500 UMI ≥ 1 | robust |
Unit = **donor** (per-donor first, then mean across donors; **no medians** in the final numbers).

## LEG A — Stress is a sampling confound, not disease (the "why exclude the ends" evidence)
Stress module = sum of 8 IEG+HSP genes (`FOS, JUN, JUNB, JUND, ATF3, DUSP1, HSPA1A, HSPA1B`) per nucleus.
Per-source, **mean across donors** (all-lobe; `stress_per_donor_alllobe.csv`):

| source | nDonors | raw_mean | **dm_mean** (UMIs/nuc) | **det2** (≥2) |
|---|---|---|---|---|
| needle biopsy (NAFLD→Cirrhosis) | 38 | 0.30 | **0.074** | 0.053 |
| healthy (deceased-donor) | 4 | 1.39 | **0.282** (~3.8×) | 0.247 |
| end-stage (explant) | 5 | 7.22 | **1.675** (~22.6× biopsy, ~6× healthy) | 0.770 |

- **Stress is elevated in BOTH deceased-donor groups** (healthy + end-stage), **far more in end-stage**.
  The needle-biopsy disease spectrum is uniformly low.
- **Per-donor heterogeneity (exact, not median):** healthy spans donor 30 = 0.022 → HL1 = 0.757 dm_mean;
  explants span CL17 = 0.91 → CL16 = 3.01. Healthy is driven by HL1 (multi-lobe).
- **Sampling correction:** all 4 healthy are **deceased-donor organ tissue** (Methods: "deceased transplant
  organ tissue… 1 cm³ cube"); the earlier **"2 surgical + 2 atlas" split was WRONG** — there is no atlas
  source. Donor 98 has biliary-stone disease.
- **What the IEG/HSP signal means:** immediate-early + heat-shock genes are the documented dissociation/
  ischemia artifact (van den Brink 2017; O'Flanagan 2019; Denisenko 2020). In snRNA their elevation =
  ongoing transcription; sustained across a whole organ = prolonged procurement/ischemic stress.

## LEG B — The end-stage gene SHAPE is selective, not a clean "turn-off" (item-two)
Ambient-robust detection (det2, ≥2 UMI), right-lobe, mean across donors (`per_group.csv`):

| gene | Healthy | NAFLD | NASH | Cirrhosis | **End-stage** | reading |
|---|---|---|---|---|---|---|
| CYP2E1 (detox) | 0.70 | 0.90 | 0.84 | 0.81 | **0.33** | detox **down** at end-stage |
| SLCO1B3 (detox) | 0.22 | 0.66 | 0.58 | 0.57 | **0.28** | detox **down** |
| GLUL (PC id) | 0.02 | 0.09 | 0.08 | 0.07 | **0.14** | PC identity **retained/up** |
| CYP3A4 (PC id) | 0.04 | 0.42 | 0.31 | 0.31 | **0.41** | retained/up |
| PCK1 (PP) | 0.26 | 0.36 | 0.27 | 0.15 | **0.58** | periportal **induced** |
| ALDOB (PP) | 0.32 | 0.68 | 0.65 | 0.55 | **0.70** | induced |

- The end-stage shape = **selective detox loss + periportal induction + PC identity retained** — **not** a
  pericentral "turn-off." The legacy "pericentral program turns off" reading is **wrong**.
- It is **flat across the biopsy stages** (NAFLD→Cirrhosis); all the movement is the **end-stage jump**.
- **Confound caveat:** this shape lives entirely in the end-stage explant group — co-located with the
  stress confound (Leg A), single experiment, multi-lobe. It is a **description of the explant phenotype**,
  **not** a disease trajectory. Lobe-invariant (see `findings/lobe_invariance/`), so not a caudate artifact.

## Caveats
- Right-lobe restriction drops the 2 no-lobe healthy donors → `per_group.csv` Healthy = n=2; use
  `stress_per_donor_alllobe.csv` for all 4 healthy.
- Depth-matching: B=1500, 4-draw MC, cells below B dropped (depth-driven, see lobe/discard checks).
- **B-robust:** stress explant/biopsy fold = 21.0× / 22.6× / 22.1× at B=1000/1500/3000 (absolute levels
  scale with B, the fold/conclusion does not). So fixed B=1500 is fine for the conclusion — no full sweep needed.
- `raw_mean`/`det1`/`UMIs_per_10k` retained only for provenance; conclusions use det2 + dm_mean.

## OPEN (queued)
- **O2** — *Why is stress high in both deceased-donor groups but ~6× higher in end-stage than healthy?*
  Hypothesis to test/source: both are deceased-donor procurement (warm/cold ischemia, dissociation) →
  baseline stress; end-stage organs are sicker / longer ischemic time / explant handling → much higher.
  Needs procurement-time data (not in cohort) or literature on ischemic-time vs IEG/HSP dose.
