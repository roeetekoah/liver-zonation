# Rulers & Methods Explained

A plain-language reference for *how the zonation ruler is built* and *what every candidate set
means*. Companion to `GROUND_TRUTH.md` (verified facts) and the report PDFs in `results/`.

---

## Part 1 — How Paper 2 built the zonation reference (where the "ruler" comes from)

Paper 2 (healthy human liver spatial atlas) turned tissue into a per-gene zonation table in five steps:

1. **Anchor on one spatially-verified gene.** A *pathologist* hand-marked the **portal triads** on
   the real Visium tissue (the periportal anatomical landmark = portal vein + hepatic artery + bile
   duct at lobule corners). They confirmed **CYP2E1** is high *far* from triads (pericentral) and low
   *near* them — i.e. CYP2E1 is a validated pericentral marker, grounded in a human expert's reading
   of the actual tissue.

2. **Build 40 landmark genes by correlation to that anchor.** Across all spatial spots, correlate
   every gene with CYP2E1. The **20 most positively correlated → pericentral landmarks**; the
   **20 most anti-correlated → periportal landmarks**. (40 genes total.)

3. **Assign a position score (η) per spot/cell from the landmarks.**
   `η = Σ(periportal-landmark expr) / (Σ periportal + Σ pericentral)`.
   High η ≈ periportal, low η ≈ pericentral.

4. **Bin η into 8 zones.** Sort all spots by η, cut into **8 equal-percentile layers** (zone 1 =
   periportal end … zone 8 = pericentral end). Each spot/cell now has a **zone label 1–8**.
   (Visium spots also get spatial median-smoothing using physical neighbours <150 µm.)

5. **Characterize *every* gene against those zones.** With zones assigned, for each of ~16k genes
   average its expression *within each of the 8 zones* → an 8-number **profile**. From the profile:
   - **center-of-mass (COM)** = the expression-weighted average zone (which end the gene concentrates at);
   - **q-value** = Kruskal–Wallis test across the 8 zones (is the gene significantly zonated?).
   This per-gene COM + q-value table is the **ranked zonation table** (`supplementary_table_8.xlsx`)
   that our data-driven sets are built from.

> So the 40 landmarks *define* the zones; then *all* genes are *measured against* those zones.
> **The Paper-2 "zone label" = the 1–8 η-percentile bin.** Our cache (`paper2_train.npz`) uses 3
> terciles of η instead of 8 (a simplification); classifier entropy is therefore auxiliary.

---

## Part 2 — How *we* turn a cell's expression into a coordinate (two mechanisms)

Everything below produces a per-cell **zonation coordinate** (pericentral high, periportal low).
There are exactly two mechanisms — this is the distinction to keep straight:

### Mechanism 1 — SCORING (no model is fit; pure arithmetic)
Given two gene lists (PC, PP):
1. **z-score each gene across cells** (subtract the gene's mean, divide by its SD — so every gene is
   on a common "SDs from its own average" scale; stops a few loud genes dominating).
2. average the z-scores within each arm → `mean_z(PC)`, `mean_z(PP)`.
3. standardize each arm, then **coord = mean_z(PC) − mean_z(PP)**.
No training, no labels — just averaging two gene lists.

### Mechanism 2 — LEARNED PROJECTION (a model is fit to find per-gene *weights*)
Two sub-kinds:
- **Unsupervised (PCA).** Take the cells × ~8,488-gene **z-scored** matrix (genes shared with
  Paper 2 and expressed in ≥5% of Paper 1 hepatocytes). PCA finds the directions of **maximum
  variance** — each principal component is a *weighted combination of all 8,488 genes*, discovered
  from the data's covariance with **no labels**. We then pick the component that best matches the
  marker axis (mean CYP2E1/GLUL z − mean HAL/ASS1 z); markers only **identify & orient** which PC is
  zonation. `coord = expression · that component's weights`.
  → The axis is **rediscovered from expression variance**, *not* CYP2E1's position and *not* Paper 2's axis.
- **Supervised (regression).** Take Paper-2 cells with **zone labels**, train a multinomial logistic
  regression to *predict* the label from genes (landmark genes excluded to avoid circularity), apply
  to Paper 1 → predicted expected-zone = coordinate, entropy = confidence.

**PCA vs regression, in one line:** PCA = *find the biggest axis of variation* (no labels);
regression = *learn weights to predict a known target* (labels). Different tools.

---

## Part 3 — Every candidate ruler (families A / B / C)

### Family A — SCORING rulers (Mechanism 1: average two fixed gene lists)
| set | the two gene lists came from |
|---|---|
| `paper2_landmark` (20+20) | Paper 2's exact hepatocyte landmark CSVs (`Hepatocyte-{PC,PP}-LM.csv`) — the genes Paper 2 uses to zonate snRNA cells |
| `core_curated` (13+8) | hand-picked canonical markers (GLUL, CYP2E1 … / ASS1, HAL …) |
| `expanded_curated` (26+23) | `paper2_landmark` ∪ curated extras (de-duplicated) |
| `paper2_top50 / top100 / top250` | Paper 2's ranked table: q<0.05 & expressed, ranked by \|center-of-mass\|, top-N each end |
| `paper2_full` (1624+447) | **all** q<0.05 zonated genes split by COM sign — the primer's intended default; **it dilutes** |

### Family B — LEARNED PROJECTION rulers (Mechanism 2: fit a model for per-gene weights)
| set | method | trained on | labels? |
|---|---|---|---|
| `unsupervised` | PCA | Paper-1 **healthy** cells | none |
| `unsupervised_p2` | PCA | **Paper-2 atlas** (external; leakage control) | none |
| `unsupervised_combined` | PCA | **pooled** P1-healthy + P2-atlas (best healthy ruler) | none |
| `supervised` | multinomial logistic regression | Paper-2 cells w/ zone labels (landmarks excluded) | yes |

### Family C — sparse gene sets *derived from* the learned (PCA) axis
| set | how derived | then used by |
|---|---|---|
| `unsupervised_top50 / top100 / top250` | keep the PCA axis's top-N ± loading genes | **scoring** (Mechanism 1) |
| `unsupervised_full` | keep **all** signed-loading genes, equal weight | scoring — **dilutes** (proof weighting matters) |
| `unsupervised_lasso` | Lasso (L1) regression that reproduces the PCA axis with few genes (~275) | sparse weighted axis |
| `unsupervised_elasticnet` | Elastic-net (L1+L2), same idea (~606 genes) | sparse weighted axis |

> Lasso/elastic-net here are **self-supervised**: their target is the PCA axis's *own* score (to
> compress it), not external zone labels.

---

## Part 4 — How to read the results (the governing rule)

- **Ruler quality is judged ONLY on the healthy atlas** — the 8-marker sign gate (PC markers +, PP
  markers −), the **healthy PC–PP anti-correlation** (a real axis has the two arms mutually
  exclusive → strongly negative), and **split-half reproducibility**. The best healthy ruler is
  **frozen**, then applied to disease. Disease H1/H2/H3 are the **test**, never the selector
  (choosing a ruler by disease strength = leakage).
- **Unit of inference = donor** (~47), never the cell (~69k).
- **Key finding:** focused/weighted rulers work; the *unweighted* full sets (`paper2_full`,
  `unsupervised_full`) **dilute** (healthy PC–PP correlation flips positive). The collapse (H1) and
  program slope-loss (H2) hold across every valid ruler — including a fully external,
  label-free axis — which is the robustness evidence.

See `results/Zonation_Narrative_Report.pdf` (analysis) and `results/Zonation_Ruler_Report.pdf`
(per-set dossier); machine-readable in `results/tables/signature_battery_summary.csv`.
