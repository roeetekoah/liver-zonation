# HANDOFF — orientation for whoever picks this up next

_Pure orientation: what to read, what's current, what's legacy. No commands, no setup steps._

## Read these, in this order
1. **CLAUDE.md** — auto-loaded conventions. The load-bearing rule: **treat narrative docs as
   unverified** — confirm a file/function/number still exists before relying on it.
2. **RESUME.md** — the FOUNDATIONAL orientation: the two papers, the "ruler" idea, the unit-of-
   inference rule, the repo map. Read it to understand the *machinery*. Caveat: its results section
   (H1/H2/H3, "zonation collapse") is the *earlier* framing — superseded on the biology (see below).
3. **PLAN.md** — the CURRENT thinking. The "Emerging findings" block at the top is the live scientific
   position. The A–F checklist shows what's built, dropped, and parked.
4. **CONFOUNDERS_PLAN.md** — why the confounder controls were dropped and the recentered plan.

For the science as a finished artifact, the authoritative read is **results/reports/Zonation_Story.pdf**
(arc-driven, plot-grounded). **Zonation_Methods_Explainer.pdf** explains how the ruler / normalization
/ PCA / validation work.

## The current branch of thought (the live story)
- Healthy liver is zonated. In MASLD the **dominant, robust event is pericentral program TURN-OFF** —
  those genes are silenced, expression LEVEL drops ~34–37% by end-stage / fibrosis F4. Seen
  consistently across the level heatmap, per-set program levels, zone boxplots, the gene-level
  level/slope map, and marker profiles.
- The **periportal program largely HOLDS** its level.
- **DE-ZONATION (gradient flattening with expression retained) is WEAK and not convincingly shown** —
  the program slopes flatten only modestly, and the heatmap "pattern" view's apparent end-stage signal
  is largely a z-scoring artifact (silenced genes → amplified noise). Do not oversell de-zonation.
- The apparent **"zonation collapse" (anti-correlation / spread falling) is mostly DOWNSTREAM** of the
  turn-off — silence the pericentral genes and the coordinate becomes noise. Spread / IQR / anti-corr
  are **weak indicators**, not the result.
- The effect **tracks FIBROSIS specifically** (not generic activity/NAS), and the **label-free PCA
  ruler is genuine biology** (its PC1 is zonation; sequencing depth loads on PC2, not PC1).
- **Where we stopped:** the next intended step is the **negative-control-gene confounder check** in
  CONFOUNDERS_PLAN.md (do housekeeping genes wrongly show "turn-off"? if so it's technical) — a sharp,
  honest test that does NOT route through spread/IQR.

## What is LEGACY / superseded / dropped (don't be misled by leftover artifacts)
- **The C confounder-control apparatus is REMOVED** (`c_confounders.py` gone). It validated the
  *secondary* indicators (spread/IQR/anti-corr), not the dominant turn-off. Reasoning + the recentered
  plan live in CONFOUNDERS_PLAN.md. (`c3_level_vs_slope.py` was KEPT — it's gene-level turn-off
  *evidence*, not a spread/IQR control.)
- **The old "Biology Findings" report is GONE** (rejected: shrunk-unreadable figures, mis-placed auto-
  circles). Replaced by **Zonation_Story.pdf**. Do not resurrect auto-placed annotation circles.
- **A4's mechanism CLASSIFICATION is deprecated** (a heuristic that was unreliable). Its per-donor
  metric *trajectories* are fine; the mechanism story is carried by B1–B4 / C3.
- **The H1/H2/H3 "collapse" framing in RESUME** (measured via spread/anti-correlation) predates the
  turn-off reframing. It's not wrong as machinery, but the *headline* is now turn-off, with
  spread/anti-corr understood as weak/downstream.
- The two **battery reports** (Zonation_Narrative_Report, Zonation_Ruler_Report) are about an *earlier*
  phase — **ruler selection** (leakage-clean eligibility, the two co-primary rulers). Foundational and
  still valid for *how the ruler was chosen*, but the Narrative one is stale on the biology.

## Non-negotiable facts to internalise before touching anything
- **Unit of inference = donor (~47), never the cell.** No cell-level pseudoreplication.
- **The scored count matrix is the SCT-corrected assay** (`counts.npz` == nCount_SCT exactly;
  per-cell totals ~3–5.7k), so sequencing depth is already largely equalized. "Depth" in any control
  is on the SCT scale, not raw UMI. A true raw-depth check would need the RNA assay (not extracted).
- **Fibrosis / NAS / SAF staging is already in** `data/processed/paper1/metadata_all_cells.csv` — no
  download needed.

## How this collaborator works (so you don't repeat rejected moves)
- Wants the story **grounded in the actual plots**, with correlations as *support*, never the headline.
- Demands **honesty about strong vs weak** — say plainly when something (e.g. de-zonation) isn't shown.
- Reports: **one readable figure per page, full panels (not just representatives), NO auto-circles**
  (captions guide the eye instead).
- Holds your claims to the same bar as summary stats: a correlation is an *indicator*, an intervention
  is *proof*. Don't state a confound as established from a correlation alone.
- Owns/expects course-corrections; values a parked plan over shipping a mismatched analysis.
