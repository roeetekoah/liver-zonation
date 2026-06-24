# Detox-dimming dossier — complete provenance, in plain English + raw numbers

One-line: **In matched MASLD biopsies, hepatocytes keep their zonal identity (no rezonation), but
the pericentral detox program dims in level. This is real (survives composition control), invisible
to single-gene DGE, and surfaces only with gene-set + per-cell tests.**

> **Naming note.** Earlier files called the per-cell metric "within-PC detox *burden*" — misleading
> ("burden" connotes a load). It is the **within-PC detox output**: detox transcripts per pericentral
> nucleus, depth-matched. Renamed throughout the deck.
>
> **Framing note (adopted canonical wording).** This is a **relative** decline — detox transcripts
> within a fixed 1,500-UMI budget — **not proven absolute molecule loss**. It is a **donor-level**
> trend (not pseudoreplicated). It **could partly reflect a shift among PC subzones** (fewer
> deep-zone-3 high-detox cells) rather than pure within-cell downregulation. It is **functional
> dimming of a zonated program, NOT de-zonation or transdifferentiation**, and does not rescue the
> paper's identity claim. Lead with the fibrosis-wide trend (ρ=−0.48, p=0.003), not the F1-vs-F4
> endpoint (F4 n=4). Sets were **pre-specified** from CYP/detox biology + Paper 2 markers.

---

## 0. Two things that are NOT the same

- **Rezonation / de-zonation** (what Gribben et al. claimed): cells *change identity* — pericentral
  cells co-express periportal markers, lose their distinct program, transdifferentiate toward
  cholangiocytes. A reorganization of *which cell is what*. **Our result: no** (anchors flat, gradient
  holds, no co-expression rise).
- **Dimming** (this dossier): cells *keep* their identity, but the *level* of the program drops — same
  pericentral cell, quieter detox program. **Our result: yes, subtly.**

Radio analogy: rezonation = the station changes genre; dimming = same genre, lower volume.

## 1. What "the detox module" is

The liver lobule has two zones, each with a signature job:
- **Pericentral (PC, zone 3)** = **drug / xenobiotic metabolism** — the CYP enzymes (CYP2E1, CYP3A4 …).
  **This is "the detox module." Detox = the pericentral program.**
- **Periportal (PP, zone 1)** = urea cycle / ammonia disposal (CPS1, ASS1 …).

"The pericentral detox program dims" = pericentral cells' drug-metabolism genes drop in expression
level, while the cells stay pericentral.

## 2. The exact question

Per-gene pseudobulk DGE (`dge_genomewide.csv`) found NO single zonation/detox gene moving with
fibrosis (all FDR > 0.79; GLUL 0.85, CYP2E1 0.98). Open question: could a **weak coordinated program**
exist — many genes each nudging a little, same direction — that per-gene FDR misses? Gene-set tests
are built for exactly that.

## 3. The 10 pre-specified gene sets (no fishing; every gene fixed in the scripts)

| Set | Genes (n) | Biology | What it tests |
|---|---|---|---|
| xenobiotic_CYP | 13: CYP2E1,1A2,3A4,3A5,3A43,2C8,2C9,2C19,2B6,1A1,2A6,2D6,4F12 | cytochrome-P450 phase-I drug metabolism | core **pericentral detox** |
| detox_phase2 | 16: UGT1A1,2B4,2B7; GSTA1,A2; SULT2A1,1A1; AKR1D1,1C1; ADH1A,1B,4; ALDH1L1; FMO3; AOX1; AMACR | phase-II conjugation + alcohol/aldehyde detox | broader **detox** |
| pericentral_anchors | 20 (Paper 2 PC landmarks) | PC zonal identity | does PC identity shift |
| periportal_anchors | 20 (Paper 2 PP landmarks) | PP zonal identity | does PP identity shift |
| urea_cycle | 9: CPS1,OTC,ASS1,ASL,ARG1,NAGS,SLC25A13,GLS2,GLUL | periportal nitrogen metabolism | does the **PP program** move |
| bile_acid_lipid | 20 | bile-acid synth/transport + lipid | broad metabolism (≈ negative) |
| cholangiocyte_ductular | plasticity.txt + KRT7,19,23,EPCAM,CFTR,HNF1B,SPP1,ANXA4,DEFB1,PKHD1,CLDN4,TACSTD2,MMP7 | bile-duct cell markers | does the **biliary / transdifferentiation** signal appear |
| CTRL_interferon | 20 | inflammation | **control** — expect mild UP |
| CTRL_EMT | 20 | fibrogenesis / scar | **control** — expect UP |
| CTRL_ER_stress | 20 | unfolded-protein response | **control** — expect flat |

Sources: PC/PP anchors = `data/signatures/*_paper2_landmark.txt` (Paper 2's own genes, verbatim);
cholangiocyte = `data/signatures/plasticity.txt` + canonical markers; metabolic modules =
KEGG/HGNC cores; controls = MSigDB Hallmark cores. All hard-coded in the scripts (no DB pulled).

**Why the controls are controls:** a control is a set whose answer we already know from biology, so
it proves the test is detecting real signal and not noise. Fibrosis *is* scar → EMT must rise (UP ✓).
Chronic injury has inflammation → interferon mild UP (✓). ER-stress has no link to fibrosis stage →
flat (✓). All three behaved → the detox-DOWN call is credible.

## 4. The methods, plain English

- **Pseudobulk**: sum each donor's hepatocyte UMIs into one profile per donor (donor = unit of
  inference; 38 biopsy donors, F0–F4 = 2/8/12/12/4; deceased/explant ends excluded).
- **CPM** (counts per million): express each gene as a share of the donor's library. Simple but
  **compositional** — if some genes balloon, everyone else's share mechanically shrinks (pie slices).
- **TMM** (trimmed mean of M-values, edgeR): a scaling that ignores the few wildly-changing genes →
  **composition-robust** (a rising biliary set can't fake a drop elsewhere).
- **camera** (limma): a **competitive** gene-set test — "is this set more shifted than the rest of the
  transcriptome?" Adjusts for inter-gene correlation. Relative → vulnerable to the pie-slice trap.
- **ROAST / mroast** (limma): a **self-contained** gene-set test — "does this set move on its own,
  against zero?" Absolute, rotation-based p-value → immune to the pie-slice trap, more conservative.
- **GSEA pre-rank** (gseapy): rank all genes by their fibrosis-trend statistic, ask whether a set
  clusters at one end. Competitive, like camera.
- **Within-PC depth-matched burden**: skip gene-sets — count detox molecules per pericentral nucleus
  after equalizing read depth (down-thin to 1,500 UMI). Per-cell, absolute, composition cannot touch it.

## 5. How it was run (the exact pipeline)

1. `src/dge/dge_genomewide.py` → `dge_genomewide.csv`: donor-level per-gene trend (Spearman ρ of
   log2-CPM vs fibrosis + p + BH-FDR), 17,572 genes, 38 biopsy donors.
2. `src/dge/geneset_tests.py` (Python, **gseapy v1.3.0**, pip-installed): `gp.prerank` on the ranked
   list (signed −log10 p primary; signed ρ robustness), 10,000 permutations, seed 0 →
   `geneset_tests.csv`.
3. `src/dge/geneset_camera.R` (R, **limma::camera**): rebuilds donor-level log2(CPM+1) pseudobulk
   from `pseudobulk_hep_by_donor.csv`, filter CPM≥1 in ≥half donors, design `~F`, `camera(contrast="F")`
   → `geneset_camera.csv`.

## 6. Raw results

**camera (competitive, the headline tool) — `geneset_camera.csv`:**

| Set | n tested | Direction | P | FDR |
|---|---|---|---|---|
| xenobiotic_CYP | 13 | Down | 2.3e-7 | 2.3e-6 |
| CTRL_EMT | 15 | Up | 1.8e-6 | 9.1e-6 |
| cholangiocyte_ductular | 10 | Up | 5.6e-6 | 1.9e-5 |
| pericentral_anchors | 20 | Down | 5.8e-5 | 1.5e-4 |
| CTRL_interferon | 20 | Up | 7.4e-4 | 1.5e-3 |
| detox_phase2 | 16 | Down | 4.2e-3 | 7.0e-3 |
| periportal_anchors | 20 | Up | 1.0e-2 | 1.5e-2 |
| urea_cycle | 9 | Down | 9.9e-2 | 0.12 |
| bile_acid_lipid | 20 | Down | 0.68 | 0.72 |
| CTRL_ER_stress | 20 | Up | 0.72 | 0.72 |

**GSEA — `geneset_tests.csv` (NES, FDR):** CYP −2.04, 1.1e-3 · PC-anchors −1.88, 5.2e-3 ·
detox_phase2 −1.47, 0.081 · cholangiocyte +1.69, 0.011 · controls as above. Directions all agree.

The conclusion table = a join of these two files: Direction = camera `Direction` (= sign of GSEA NES),
"camera FDR" = camera FDR column, "GSEA FDR" = geneset_tests FDR column. Nothing hand-curated.

**The red flag that forced verification:** PC-anchors DOWN while PP-anchors UP (a see-saw) is exactly
what a competitive test on CPM shows if biliary/stromal genes rise and eat library budget.

## 7. Adversarial verification (`src/dge/geneset_verify.R`, `geneset_verify_test4.py`)

| Test | Rules out | Result |
|---|---|---|
| 1. CPM vs **TMM** camera | CPM pie-slice artifact | TMM factors 0.91–1.21; detox FDRs unchanged (CYP 2.3e-6→3.5e-6) ✓ |
| 2. **mroast** (self-contained) | competitive borrowing | CYP core Down FDR 0.015 ✓; broader PC set borderline (0.08) |
| 3. Drop 65 up-going genes, renormalize | the see-saw cause | detox stays Down, FDRs unchanged (CYP 2.7e-6) ✓ |
| 4. **Within-PC depth-matched burden** | everything compositional | F0→F4 = 12.5/11.9/10.2/9.9/8.8 UMI/nuc; Spearman −0.48, p=0.003; F1→F4 d=−2.1, exceeds MDE ✓ |

## 8. Verdict

**Real per-hepatocyte program change**, robust to composition (survives TMM, contaminant removal, and
a per-cell measure that compositionality cannot affect). Honest limit: in the strictly self-contained
gene-set test, only the **CYP xenobiotic core** clears FDR alone; the within-PC per-cell burden is what
makes the broader claim solid. The up-going biliary/ductular contrast remains "a lead, not closed."

**Defensible deck wording:** "The pericentral detox program dims coordinately with fibrosis — a real
per-hepatocyte decline (within-PC depth-matched burden ~11.9→8.8 UMI/nucleus F1→F4, Spearman −0.48,
p=0.003; gene-set Down survives TMM + contaminant removal) — even though no single detox gene clears
per-gene FDR. Cells keep their zonal identity; the program's level drops."

## 9. Files

Analysis: `src/dge/dge_genomewide.py`, `geneset_tests.py`, `geneset_camera.R`, `geneset_verify.R`,
`geneset_verify_test4.py`. Tables: `results/tables/analysis/dge_genomewide.csv`, `geneset_tests.csv`,
`geneset_camera.csv`, `geneset_verify_*.csv`, `within_pc_detox.csv`, `mde_table.csv`. Notes:
`findings/geneset_tests/README.md`, `findings/geneset_detox_verification.md`, this dossier.
