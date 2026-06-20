# Original plan — as first phrased — and everything since

A provenance record, so you can see nothing core was dropped: we **kept the whole original idea** and **added** rigor and a second method around it.

---

## 1. The original brainstorm
`docs/research_question_options.md` holds the original six candidate questions. We chose **Option 1 — "Zonation as a disease clock"**: use Paper 2's healthy spatial zonation as a reference to assign a pseudo-zonation coordinate to Paper 1's disease cells and measure the collapse across stages.

## 2. The original step-by-step (as first written)
The first concrete plan for Option 1 was three steps:

- **Step A — define "ground-truth" spatial signatures (Paper 2).** Extract the pericentral and periportal landmark genes.
- **Step B — score the single cells (Paper 1 + Lec 15–16).** Process the matrix with PCA/UMAP; compute a per-cell **zonation score** (high if pericentral genes high, low if periportal high) → a pseudo-spatial coordinate for tens of thousands of cells.
- **Step C — track the degradation (Lec 5, FDR).** Group cells by disease stage; find genes that change with progression within a pseudo-zone; apply **Benjamini–Hochberg FDR**.

Plus the "why full marks" rationale: not a reproduction (Paper 2 decodes Paper 1), and squarely on the syllabus (single-cell clustering, multiple-testing/FDR).

---

## 3. What we kept / added / changed

| Original element | Status now | Where |
|---|---|---|
| Option 1 ("zonation as a disease clock") | **Kept** — the whole project | primer §1, §4 |
| Step A: pericentral/periportal signatures from Paper 2 | **Kept** = Step 1 / artifact A1 | primer §6, `pericentral_genes.txt`/`periportal_genes.txt` |
| Step B: per-cell zonation score (PCA/UMAP, Lec 15–16) | **Kept** = Step 4a | primer §5.4, §6; `pipeline.py` |
| Step C: stage-resolved DE + BH-FDR (Lec 5) | **Kept** = Step 7 (H2) | primer §5.7, §6; `pipeline.py` |
| Collapse "blurring/variance" across stages | **Kept + sharpened** into the H1 collapse curve (spread + trend test + donor bootstrap) | Step 6 / A6 |
| — | **ADDED: classifier (the AI model) + entropy** (Step 4b) — your original "AI classifier" intent, now with the same-platform training trick | primer §5.5; `classifier_step.py` |
| — | **ADDED: validation gate (Step 5)** — recover zonation in healthy donors before trusting disease | primer §6 |
| — | **ADDED: "is the ruler still a ruler?" diagnostics (Step 5b)** — internal coherence / anti-correlation / split-half / program-off-vs-restriction | primer §5.6, §6 |
| — | **ADDED: de-zonation ↔ plasticity link (H3, Step 8)** | primer §4.3, §6 |
| — | **ADDED: the "gap" framing + non-circularity + scope limits** (population structure, not per-cell position; can't see pure spatial scrambling) | primer §3.4, §5.4 |
| — | **ADDED: optional Paper 3 bonus** (collapse-driver genes vs inherited-risk genes) | primer §6 |
| — | **ADDED: statistical rigor** — donor-level bootstrap, negative control (shuffle labels), held-out classifier accuracy | primer §6 |

## 4. Bottom line
- **Nothing core was dropped.** Steps A/B/C survive verbatim as Steps 1, 4a, and 7.
- The **classifier you originally wanted is in** — it's the headline (Step 4b); the signature score was *added* as a robust baseline beside it, not a replacement.
- Everything else is **additive**: controls (Steps 5, 5b), a second hypothesis (H3), honesty framing, and the optional bonus — i.e. the project got more rigorous and better-defended, not narrower.
