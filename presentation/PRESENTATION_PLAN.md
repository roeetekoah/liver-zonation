# Final presentation — plan & build map

Target: **~15 min**, ~14 main slides (~1 min each) + backup. Audience: course staff + peers (technical).
This is a **results** talk, different from the old proposal deck (`archive/Zonation_Hackathon_Deck.pptx`);
the current deck is `presentation/Zonation_Final_Presentation.pptx`, and that + the primer are the
source of all the pre-made material.

Status code:
- 🟢 **Pre-made now** — stable regardless of results.
- 🟡 **Template now, fill after** — layout/title/caption built now; swap one figure + fill a blank later.
- 🔴 **Results-only** — needs the hackathon numbers (but the *question* it answers is pre-written).

---

## Slide map (the 15-min deck = `Zonation_Final_Presentation.pptx`)

| # | Slide | ~min | Status | Source / what to drop in after |
|---|-------|------|--------|--------------------------------|
| 1 | Title — project, names, course | 0.5 | 🟢 | proposal deck |
| 2 | The hook: why zonation loss matters (drug clearance · ammonia/encephalopathy · finer severity · cancer) | 1.5 | 🟢 | primer §4 "Why this matters" |
| 3 | Biology in one slide: lobule + porto-central gradient = a *gene* gradient | 1 | 🟢 | primer Fig 2 (asset) |
| 4 | Two datasets, one gap (the jigsaw) | 1 | 🟢 | primer Fig 3 (asset) |
| 5 | The question + H1 / H2 / H3 | 1 | 🟢 | primer §4 table |
| 6 | Method: decode position (ruler → coordinate → classifier/entropy) | 1.5 | 🟢 | primer Figs 5 & 6 (assets) |
| 7 | Doing it honestly: donor-level · circularity guard · what de-zonation is/isn't | 1 | 🟢 | primer §5.4/§5.6 |
| 8 | **Positive control — the ruler works on healthy liver** | 1.5 | 🟢 *(already real data)* | `results/figures/p2_validation.png` |
| 9 | **H1 — does zonation collapse across stages?** | 2 | 🔴 | real A6 collapse curve + ρ, donor-bootstrap CI, perm-p. Expected: spread↓, anti-corr→0. *We found: ___* |
| 10 | **H2 — which programs collapse, and where** | 1.5 | 🔴 | A7 volcano + top non-signature genes per zone (q<0.05). *We found: ___* |
| 11 | **H3 — are the de-zonated cells the plastic ones?** | 1.5 | 🔴 | A8 within-donor scatter + per-donor ρ / OLS dez coef. *We found: ___* |
| 12 | Limitations & honest scope (can't see pure spatial scrambling; ruler-validity) | 1 | 🟢 | primer Fig 7 + §5.6 |
| 13 | Conclusions / takeaways | 1 | 🟡 | 3 bullets templated; fill the actual findings |
| 14 | Thanks / questions | 0.5 | 🟢 | — |

### Backup / appendix (Q&A insurance — keep after slide 14)
| # | Slide | Status | Fill |
|---|-------|--------|------|
| B1 | "Is the ruler still a ruler?" — validity battery (Step 5b) | 🟡 | A5b per-stage curves |
| B2 | Classifier confusion matrix (held-out on Paper 2) | 🔴 | from Step 4b |
| B3 | Stats appendix: donor-level inference, pseudobulk, FDR, controls | 🟢 | primer §6.6/§6.7 |
| B4 | Bonus: collapse-drivers vs inherited risk (Paper 3) | 🔴 (optional) | A9 enrichment fold + q |
| B5 | Data & reproducibility (raw→processed, repo, run_all) | 🟢 | PROJECT_MAP |

---

## What is genuinely pre-made vs. left as stub

- **~11 slides fully pre-made** (1–8, 12, 14, + B3/B5): motivation, biology, datasets/gap, question, method, honesty, the *real* positive control, limitations.
- **3 results slides are stubs** (9, 10, 11) + conclusions (13) + optional backups (B1, B2, B4).
- Slide 8 is a freebie: it shows the validation we already ran (`p2_validation.png`) — real data, no waiting.

## The trick that makes stubs cheap to fill
Each 🟡/🔴 slide is built NOW with: the **title**, an **axis / "what am I looking at" caption**, a **grey placeholder box** where the figure goes, and the pre-written line **"We expect X → we found ___."** After the hackathon the work is a *figure swap + one blank*, not building a slide under time pressure.

## Post-hackathon fill checklist (do in this order)
1. Slide 9 ← `plot_a6_collapse` output (A6) + trend stats. Replace placeholder image; fill "we found".
2. Slide 10 ← `plot_a7_volcano` (A7) + name the 3–5 earliest collapsing programs (non-signature).
3. Slide 11 ← `plot_a8_plasticity` (A8) + the within-donor statistic.
4. Slide 13 ← write the 3 real takeaways (one per hypothesis).
5. Optional: B1 (A5b), B2 (confusion matrix), B4 (A9 enrichment).
6. Re-export PDF; rehearse to 15 min (cut B-slides from the spoken flow, keep for Q&A).

## Assets
- `presentation/assets/` — PNGs rendered from the primer's figures (biology, gap, method, expected-collapse, limitations) + the real `p2_validation.png`.
- Figures the hackathon must produce go to `results/figures/` (the `src/plotting` functions already exist).
