# signatures/

Pericentral (PC) and periportal (PP) hepatocyte zonation gene sets. One gene symbol per
line, no header. **Four families per zone** — the key distinction is **extracted vs derived**:

| File | What it is | Extracted or derived? | Size (PC / PP) |
|---|---|---|---|
| `*_paper2_landmark.txt` | **The EXACT Paper 2 hepatocyte landmark set** — the genes Paper 2 used to anchor the porto-central axis. **This is the pipeline's default baseline.** | **Extracted verbatim** from Paper 2 | 20 / 20 |
| `*_core.txt` | Curated, biology-informed anchor set (canonical anchors added, inflammation genes dropped) | **Derived** (our edit) | 13 / 8 |
| `*_expanded.txt` | Union of the landmark + core + the top ~80 ranked zonated genes from Paper 2's snRNA table | **Extracted** (ranked) ∪ derived | ~102 / ~91 |
| `periportal_sensitivity.txt` | The periportal core with inflammation-linked `HAMP` removed | **Derived** (our edit) | — / 7 |

> **Your question — "derived or extracted purely from the paper?"** The **baseline
> (`paper2_landmark`) is extracted purely and verbatim from Paper 2.** `expanded` is also
> built from Paper 2's data (its ranked table). Only `core` and `sensitivity` are *our* edits,
> kept as alternatives — never the baseline.
>
> **And yes — there are four families:** the exact Paper 2 set **plus** the previous three
> (`core`, `expanded`, `sensitivity`). The earlier confusion was naming: what used to be
> called `core` (the curated set) is `core` again; the exact Paper 2 set has its own explicit
> name, `paper2_landmark`.

## The baseline IS exactly Paper 2's set (deliberate, and the default)
`pericentral_paper2_landmark.txt` / `periportal_paper2_landmark.txt` are byte-for-byte the
contents of:
- `data/raw/Human-liver/Matlab_scripts/Hepatocyte-PC-LM.csv`  (20 genes)
- `data/raw/Human-liver/Matlab_scripts/Hepatocyte-PP-LM.csv`  (20 genes)

**`config.py` (`PC_GENES`/`PP_GENES`) points the pipeline at these by default**, so the
primary analysis uses *exactly the set Paper 2 used* — the most defensible baseline. The
other tiers are swapped in only for robustness.

## How `*_expanded.txt` was built
Ranked from `data/raw/2025-01-01424E-s1/supplementary_table_8.xlsx`, sheet **`Hepatocyte`**
(Paper 2's **single-nucleus** zonation table — chosen over the Visium Table 2 because it is
**hepatocyte-specific** and on the **same platform as Paper 1**, avoiding portal-tract stroma
contamination). Zone 1 = pericentral, zone 8 = periportal (verified: CYP2E1/GLUL low
center-of-mass, ASS1/HAL high). We scored each gene by center-of-mass, kept genes expressed
above the 55th percentile **and present in Paper 1**, took the ~80 most polarized per end, and
unioned with the landmark + core sets. Rebuild: `python src/prep/03_build_expanded_signatures.py`.

## Why a curated `core` exists
The landmark **periportal** set is heavy on **secreted / acute-phase / complement /
coagulation** genes (`HAMP, SERPINA1, HP, LBP, FGA/FGB/FGG, TF, HPX, C8G, CFHR3, APOA1, APOF,
F9, FABP1, SERPINA11`) that can move with **inflammation/fibrosis** in MASLD, not only with
zonal position. The landmark **pericentral** set is missing canonical anchors (`GLUL, CYP2C8,
CYP27A1, PCK2, SLC2A2, AXIN2`). `core` addresses both — but it's an *opinion*, so it's an
alternative, not the baseline.

## Human-specific note
`PCK2` is **pericentral in humans** (Paper 2), not periportal; urea-cycle enzymes
`ASL/OTC/NAGS` are pericentrally shifted in humans while `ASS1` stays periportal — kept **out**
of the periportal lists accordingly.

## Hackathon guidance
- **Primary = `paper2_landmark` (exact Paper 2).** Report `core` (curated) and `expanded` as robustness.
- Run H1 with `periportal_sensitivity.txt` to show the collapse isn't an acute-phase artefact.
- For the H2 "driver" analysis use **held-out genes** — never test the same genes that built
  the coordinate (circularity).
