# Liver-Genomics Hackathon — Research Question Options

*Computational Genomics (76553), final hackathon. Team of 2, ~2 concentrated days + prep. Goal: a genuinely novel question (reproduction = 0), in-scope methods, high feasibility, full-mark potential.*

---

## What each paper actually did (map first)

**P1 — Acquisition of epithelial plasticity in human chronic liver disease** (Nature 2024, Gribben/Vallier). snRNA-seq of 47 liver biopsies spanning MASLD stages (healthy→MASLD→MASH→cirrhosis) + 3D imaging. Main claim: hepatocytes lose zonation and **transdifferentiate** to cholangiocytes (and vice-versa) *without* adult stem cells; the PI3K–AKT–mTOR (insulin) pathway drives the plasticity. Data: **GEO GSE202379**; code github.com/Core-Bioinformatics/MASLD-NASH.

**P2 — A spatial atlas of the healthy human liver from live donors** (Nature 2026, Yakubovsky/Itzkovitz). Visium / Visium HD / MERFISH / PhenoCycler + snRNA-seq on 16 samples (8 live healthy donors, 8 "adjacent-normal" from pathology). Main claim: a **quantitative healthy zonation reference** along the porto–central axis (key functions pericentrally shifted vs mouse); live-donor livers differ from "adjacent normal"; early-steatotic hepatocytes show declining nuclear-encoded mitochondrial proteins + compensatory rise in mito-encoded transcripts. Data: **GSE248077** (+ GSE223559, GSE240429), **Zenodo 17735506/558/587**; code github.com/OranYak/Human-liver.

**P3 — Integrative analyses of regulatory functions of MASLD risk alleles** (Nat Genet 2026, Zhu/Hu/Lazar). snATAC-seq of MASLD liver nuclei; GWAS risk variants enriched in **cell-type-specific** regulatory elements bound by lineage-determining TFs; a **MPRA** finds hundreds of differential-activity variants (DAVs), context/stimulus dependent; eQTL + Hi-C/ChIA-PET looping + scCRISPRi assign target genes (SLC22A3, APOA5, ANGPTL3, LPL); DAVs improve MASLD PRS. Data: **GSE281367/281364/281160** (generated); public **GSE189600, GSE244832**; Hi-C **GSE86189**.

**P4 — Single-cell atlas of liver + blood immune cells across fatty-liver stages** (Nat Immunol 2025, Martin/Alatrakchi/Chung). scRNA-seq of **paired peripheral blood + liver fine-needle aspirates** across the MASLD/MASH spectrum. Main claim: stage-specific immune remodeling — hepatic Tregs, M-MDSCs, TREM2⁺S100A9⁺ macrophages, S100ʰⁱHLAˡᵒ cDC2; cytotoxic-T exhaustion with fibrosis, NK toxicity up; ligand–receptor maps for fibrogenesis. Data: **dbGaP phs004044** (raw, controlled) + processed matrices.

**The unifying fact:** all four are MASLD studies covering different layers — epithelial (P1), spatial/healthy baseline (P2), genetic/regulatory (P3), immune (P4). Cross-paper integration is where the novelty (and marks) live.

---

## The 6 options

Each lists: the new question, why it is **not** a reproduction, data, course-aligned method, hypothesis, a 2-person/2-day plan, and risks. Ratings are 1–5 (★).

---

### Option 1 — "Zonation as a disease clock": transfer the healthy zonation coordinate onto the disease cohort
**Papers:** P2 (reference) × P1 (disease). 
**Question:** P2 built a *quantitative* healthy porto–central zonation axis; P1 only *qualitatively* says hepatocytes "lose zonation." Build a zonation-reconstruction model from P2's landmark genes, assign every P1 hepatocyte (across stages) a continuous zonation coordinate, and define a **"de-zonation score"** per cell/sample. Ask: does zonation erode monotonically with stage, and does the most de-zonated hepatocyte fraction coincide with the transdifferentiating (cholangiocyte-marker⁺) cells P1 describes?
**Why novel:** nobody has projected P1's disease data onto P2's brand-new healthy coordinate system; you turn a qualitative claim into a quantitative, stage-resolved trajectory and link it to plasticity.
**Data:** GSE202379 (P1) + P2 landmark genes/reference (GitHub/Zenodo). Processed count matrices — light download.
**Method (in scope):** marker-based gradient inference, regression of score vs stage, permutation/LRT for trend significance, correlation with transdifferentiation markers.
**Hypothesis:** de-zonation increases with stage and is strongest in plasticity-acquiring hepatocytes; risk = cross-dataset batch effects, mouse→human landmark transfer.
**2×2 plan:** Person A = build/validate the zonation model on P2; Person B = ingest + QC P1. Day 2 = project, score, test, link to plasticity. Parallelizable.
**Ratings:** Feasibility ★★★★★ · Novelty ★★★★ · Challenge ★★★ · Wow ★★★★

---

### Option 2 — Does inherited risk hit the cells that change most? Map GWAS-regulatory targets onto disease-dynamic cell states
**Papers:** P3 (risk variants → cell-type regulatory elements + target genes) × P1 + P4 (cell-type composition/expression shifts across stages). 
**Question:** Are P3's risk-variant–accessible cell types and DAV target genes (APOA5, LPL, SLC22A3, ANGPTL3, …) the *same* cell types/states that expand or transcriptionally shift during progression in P1/P4? I.e., is inherited risk channeled through the dynamic cellular response?
**Why novel:** P3 stops at "variants act in cell-type-specific elements"; you connect the genetics to the *longitudinal cellular biology* from two other cohorts — a link none of the papers make.
**Data:** P3 peaks/DAVs/target-gene tables + P1 (GSE202379) + P4 processed matrices.
**Method (in scope):** overlap of risk-variant peaks with cell-type marker sets, enrichment + permutation testing, differential abundance across stages; simple cell-type-stratified score.
**Hypothesis:** risk-variant target genes are enriched in stellate/hepatocyte states that expand with fibrosis; risk = harmonizing cell-type labels across 3 datasets.
**2×2 plan:** A = parse P3 regulatory/target tables; B = compute composition/expression shifts in P1+P4. Day 2 = enrichment + permutation. Parallelizable.
**Ratings:** Feasibility ★★★★ · Novelty ★★★★★ · Challenge ★★★★ · Wow ★★★★★

---

### Option 3 — Orthogonal validation of MPRA variants by allelic imbalance in primary chromatin (build-your-own ATAC pipeline)
**Papers:** P3. 
**Question:** P3's DAVs come from an *episomal* MPRA. Do they replicate as **allelic imbalance** at heterozygous risk SNPs in the *endogenous* snATAC reads? Build a course-style pipeline — your own aligner / bwa-mem2 → MACS2 peak calling per cell type → count ref/alt reads at het SNPs → test imbalance — and ask whether endogenous allelic imbalance predicts the MPRA DAVs.
**Why novel:** an independent, sequence-intrinsic test of P3's central result using a different assay/principle (episomal reporter vs native chromatin); not a reproduction of their MPRA.
**Data:** P3 ATAC FASTQs / public GSE244832; DAV list.
**Method (in scope — this is the most "course-core" option):** short-read alignment (Ex1), ATAC peak calling/coverage (lectures), allelic-imbalance binomial/LRT test (Ex2-style statistics), genomic variation.
**Hypothesis:** MPRA-positive DAVs show stronger endogenous allelic imbalance than matched controls; risk = needs het genotypes + adequate per-SNP coverage; allele-mapping bias must be controlled.
**2×2 plan:** A = alignment + peak calling; B = SNP/allele counting + statistics. Sequential dependency but each owns a half.
**Ratings:** Feasibility ★★★ · Novelty ★★★★ · Challenge ★★★★★ · Wow ★★★★ · (best "course-alignment" score)

---

### Option 4 — Saturation & library-complexity audit of the atlases: do reported shifts survive down-sampling?
**Papers:** any one or two (natural fit: P2 or P4). 
**Question:** Apply the Ex2 library-complexity framework to single-cell/spatial data: does **effective complexity** (unique molecules recovered per cell) differ systematically by cell type, disease stage, or zonation — and do the papers' compositional/expression claims survive when you equalize complexity by down-sampling?
**Why novel:** reframes the atlases through a sampling-statistics lens the papers don't apply; can confirm *or* qualify a published claim — either is a real result.
**Data:** any processed BAM/matrix with UMI counts.
**Method (in scope — directly Ex2):** Poisson model, MLE for λ/N, saturation curves, LRT, subsampling.
**Hypothesis:** stressed/steatotic hepatocytes and fibrotic-stage cells are under-sampled, partly inflating some shifts; risk = lower biological "wow," more of a rigor play.
**2×2 plan:** A = complexity estimation per cell type; B = down-sampling re-analysis of one headline claim. Parallelizable.
**Ratings:** Feasibility ★★★★★ · Novelty ★★★ · Challenge ★★★ · Wow ★★★ · (safest full-marks-for-rigor option)

---

### Option 5 — A blood proxy for liver state: predict hepatic stage/fibrogenesis from PBMCs alone
**Papers:** P4 (paired blood + liver). 
**Question:** Can a model trained on **blood (PBMC) signatures only** predict the patient's liver immune state / MASH stage? P4 describes blood-vs-liver differences but builds no predictive cross-compartment model — a non-invasive-biomarker concept.
**Why novel:** a predictive, validated blood→liver mapping, not a description; clinically resonant.
**Data:** P4 processed paired matrices.
**Method (in scope):** feature selection, regularized logistic regression, cross-validation, permutation testing for significance.
**Hypothesis:** a sparse PBMC signature predicts stage above chance; risk = small patient n → overfitting (must use strict CV + permutation; report honest CIs).
**2×2 plan:** A = blood feature engineering; B = liver labels + CV harness. Parallelizable.
**Ratings:** Feasibility ★★★★ · Novelty ★★★★ · Challenge ★★★ · Wow ★★★★

---

### Option 6 — Immune→epithelial crosstalk: does the MASH immune niche signal the plasticity program?
**Papers:** P4 (immune ligands) × P1 (transdifferentiating epithelium). 
**Question:** Do ligands from MASH-enriched immune cells (e.g., TREM2⁺ macrophages, MDSCs) map to receptors upstream of the PI3K–AKT–mTOR plasticity program in P1's transdifferentiating hepatocytes — and does the signal strengthen with stage?
**Why novel:** bridges the immune and epithelial papers; proposes a mechanistic driver (immune niche → plasticity) neither paper tests.
**Data:** P4 + P1 (GSE202379), a public ligand–receptor list (e.g., Ramilowsky, which P2 also uses).
**Method (in scope):** ligand–receptor expression scoring, cross-stage correlation, permutation testing.
**Hypothesis:** specific macrophage ligand→hepatocyte receptor pairs co-increase with stage and the plasticity score; risk = correlative (two separate cohorts); integration confounds.
**2×2 plan:** A = immune ligand profiles (P4); B = epithelial receptor/plasticity scores (P1). Day 2 = pairing + stats. Parallelizable.
**Ratings:** Feasibility ★★★ · Novelty ★★★★★ · Challenge ★★★★ · Wow ★★★★★

---

## Quick comparison

| # | Short name | Papers | Feasibility | Novelty | Challenge | Course-fit | Best for |
|---|-----------|--------|:--:|:--:|:--:|:--:|---|
| 1 | Zonation disease-clock | P2×P1 | ★★★★★ | ★★★★ | ★★★ | high | safe + elegant |
| 2 | Risk hits dynamic cells | P3×P1×P4 | ★★★★ | ★★★★★ | ★★★★ | high | most integrative |
| 3 | MPRA allelic-imbalance check | P3 | ★★★ | ★★★★ | ★★★★★ | **highest** | most "core course" |
| 4 | Complexity/saturation audit | any | ★★★★★ | ★★★ | ★★★ | high (Ex2) | rigor / safe |
| 5 | Blood→liver predictor | P4 | ★★★★ | ★★★★ | ★★★ | med-high | clinical hook |
| 6 | Immune→plasticity crosstalk | P4×P1 | ★★★ | ★★★★★ | ★★★★ | med | highest wow |

**Suggested shortlist for a 2-person/2-day full-mark run:** Option 1 (lowest risk, clean story) or Option 2 (highest integrative payoff). Option 3 if you want to lean hardest into the course's alignment/ATAC/statistics core.

**Next step:** pick one (or a 1+fallback), and I'll turn it into the formal 1–2-page proposal in the Ex4 template (title, background, question+objectives, data, hypothesis & risks, computational model/algorithm/stat-tests, parallelized steps, bibliography).
