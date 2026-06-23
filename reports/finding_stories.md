# Finding stories

One self-contained narrative paragraph per finding (F1–F18) and per key methodological decision (D1–D3),
written for a paper Discussion or a talk. Every number is stated with its scale and meaning. Status is
reported honestly: a null ("no detectable change, large shifts excluded") is never inflated to "proven
preserved", quarantined and not-yet-confirmed results are flagged as such, and we are explicit that we
correct specific transcriptional evidence legs of Gribben et al. (Nature 2024), not the whole claim.

Grounded throughout in the per-finding `findings/F*/README.md` numbers and the audited
[`CLAIMS_LEDGER.md`](../CLAIMS_LEDGER.md). The overall thesis: in acquisition-matched needle-biopsy MASLD,
hepatocyte gene-expression zonation shows no detectable change (with large coordinated shifts affirmatively
excluded); the dramatic "de-zonation" and "transdifferentiation" signals are confined to confounded
end-stage explant tissue or to compositional/ambient effects.

---

## F1 — Lobe sampling: the zonation pattern is lobe-invariant

The end-stage explant livers were sampled from three anatomical lobes (Right, Left, and Caudate), whereas
every disease needle biopsy comes from the Right lobe only — raising the worry that multi-lobe sampling,
and the caudate lobe in particular, could manufacture the apparent de-zonation signal. The caudate lobe
(Couinaud segment I) is genuinely distinct: it has a dual portal blood supply, drains directly into the
inferior vena cava rather than through the three main hepatic veins, and is often spared and hypertrophied
in cirrhosis, so it is not interchangeable with right-lobe parenchyma. We tested this by computing, within
the 5 end-stage explant donors, the per-gene detection rate (fraction of that lobe's hepatocyte nuclei with
at least one raw UMI for the gene) separately in each lobe. Detection is essentially lobe-invariant: GLUL
detection fraction is 0.350 / 0.343 / 0.297 across Right/Caudate/Left, ALDOB is 0.821 / 0.837 / 0.838, and
CPS1 is 0.826 / 0.874 / 0.879 — the same zonation markers are on or off in every lobe, and the whole
de-zonation pattern is already fully present in Right-lobe-only cells. The honest caveat is that absolute
gene burden (UMIs per 10,000 total UMIs) does vary moderately between lobes (median relative spread, defined
as (max−min)/mean, is about 0.36 across genes, e.g. CYP3A4 at 8.75 / 9.78 / 14.13 per 10,000), so
"invariant" applies cleanly to detection and pattern, not to exact expression level. This clears only the
lobe sub-confound; it does not clear the separate and larger explant-versus-biopsy sampling-mode and
procurement-stress confound (F2). For the thesis, it removes one candidate technical explanation for the
explant signal and confirms the primary across-stage analysis is right-lobe-only by construction.

## F2 — Stress-by-sampling confound: IEG+HSP elevation tracks procurement, not disease

This finding asks whether the tissue groups being compared are even biologically comparable, or whether they
differ by an acquisition artifact that travels with disease stage. We defined a stress module as the
per-nucleus sum of 8 immediate-early and heat-shock genes (FOS, JUN, JUNB, JUND, ATF3, DUSP1, HSPA1A,
HSPA1B) — the canonical dissociation/ischemia signature documented by van den Brink 2017, O'Flanagan 2019,
and Denisenko 2020 — and quantified it as the mean module UMIs per nucleus after binomial down-thinning of
every nucleus to a common 1,500-UMI budget (4-draw Monte-Carlo average), plus an ambient-robust detection
rate (fraction of nuclei with module sum ≥ 2 UMI). The stress burden is uniformly low across the 38 needle
biopsies (mean 0.074 down-thinned UMIs per nucleus), about 3.8× higher in the 4 deceased-donor healthy
livers (0.282), and about 22.6× higher in the 5 end-stage explants (1.675 UMIs/nucleus, ~6× the healthy
group); the ambient-robust det2 rates tell the same story (0.053 / 0.247 / 0.770). Stress is therefore
elevated in both deceased-donor groups and dramatically so in the explants, while the entire biopsy disease
spectrum stays flat — meaning procurement mode, not MASLD severity, drives this signal. The fold is robust
to the depth budget (21.0× / 22.6× / 22.1× at B = 1,000 / 1,500 / 3,000). We also corrected a provenance
error here: all 4 healthy samples are deceased-donor 1 cm³ organ cubes (the earlier "2 surgical + 2 atlas"
description was wrong; there is no atlas source). This is the quantitative justification for excluding the
deceased-donor explant and healthy groups from the disease axis, and the foundation for treating their
de-zonation signal as confounded.

## F3 — The end-stage gene shape is selective, not a pericentral "turn-off"

Having established that the explants are a confounded group (F2), this finding characterizes exactly what
their gene-expression shape looks like, to test the legacy reading that "the pericentral program turns off."
Using ambient-robust detection (fraction of nuclei with ≥ 2 UMI), right-lobe cells, averaged across donors,
the end-stage shape is selective rather than a clean turn-off: the xenobiotic detox genes fall (CYP2E1 from
~0.81 in cirrhotic biopsy to 0.33 in explant, SLCO1B3 from 0.57 to 0.28), but the pericentral identity genes
are retained or even rise (GLUL from 0.07 to 0.14, CYP3A4 from 0.31 to 0.41), and the periportal genes are
induced (PCK1 from 0.15 to 0.58, ALDOB from 0.55 to 0.70). So the explant phenotype is selective detox loss
plus periportal induction with pericentral identity preserved — the legacy "pericentral turns off" reading
is wrong. Crucially, all of this movement is the end-stage jump; the values are flat across the four biopsy
stages (NAFLD through cirrhosis), and the pattern is lobe-invariant (F1), so it is not a caudate artifact.
The important caveat (status: LIVE but caveated) is that this is a group mean that masks substantial
per-donor heterogeneity — the 5 explants go in different directions (F14) — so the "selective shape" should
be read as a pooled description of a confounded contrast, not as a single mechanism or a disease trajectory.

## F5 — Cross-lineage stress segmented into IEG / HSP / HIF: acute handling, not hypoxia

If the explant stress signal were a genuine hepatocyte disease program, it should be specific to
hepatocytes; if it is a whole-organ procurement artifact, it should appear equally in non-zonated cell
types. We segmented the stress signal into three programs measured separately — IEG (immediate-early: FOS,
JUN, JUNB, JUND, ATF3, DUSP1), HSP (heat-shock: HSPA1A, HSPA1B), and HIF (hypoxia: VEGFA, SLC2A1, LDHA, CA9,
ENO1, PGK1, HSP90AA1, held out by design because chronic low-O2 differs from acute handling) — using mean
module UMIs per cell after binomial down-thinning to a common 1,500-UMI budget. The acute IEG signal is
organ-wide rather than hepatocyte-specific: the explant-over-biopsy fold is 18.5× in hepatocytes and an
essentially identical 18.2× in endothelial cells, which carry no hepatocyte zonation at all, and remains
elevated across stellate (12.0×), cholangiocyte (10.6×), macrophage (5.3×), and lymphocyte (3.2×) lineages.
The heat-shock signal is also high (66× in hepatocytes, with elevation even in healthy non-parenchymal
cells), whereas the hypoxia/HIF program is weak everywhere (only 1.7–2.6× across lineages). Because a
zonation-irrelevant cell type is equally stressed and the hypoxia axis barely moves, the end-stage signal is
acute tissue handling and procurement, not chronic disease hypoxia. This reinforces F2's exclusion of the
explants: the signal that drives the dramatic "de-zonation" is a whole-organ artifact, not a hepatocyte
disease state.

## F6 — NAS components versus detox (QUARANTINED — do not cite)

This finding is QUARANTINED and is held out of all conclusions pending a joint review (queue item O6); the
numbers are reproducible and recorded, but they must not be cited because the result is not yet understood.
The question was a sharp, free test of the pathologist's mechanistic hypothesis that end-stage detox loss
reflects cytokine-driven (IL-6/TNF) CYP suppression: if real, the histology-graded Inflammation sub-score
(read independently of the RNA) should predict detox loss within the 38 biopsy donors, orthogonal to
fibrosis. We defined detox as the per-donor mean down-thinned-to-1,500-UMI burden of CYP2E1, CYP1A2, ADH4,
AKR1D1, SLCO1B3 (excluding CYP3A4, which is a pericentral identity gene) and correlated it against each NAS
component. The confusing result is that Inflammation is the weakest, non-significant predictor (Spearman
ρ = −0.188, p = 0.258, not significant), while Ballooning is the one robust hit (ρ = −0.422, p = 0.008,
surviving 4-test Bonferroni); the partial correlation of detox with inflammation controlling for fibrosis is
only −0.104. Read naively, the inflammation/cytokine-CYP-suppression hypothesis is not supported in biopsy
tissue, and the modest within-biopsy detox variation tracks hepatocyte ballooning/injury instead — but the
inflammation-null/ballooning-significant split may reflect collinearity, the small n = 38, or a metric
issue, which is exactly why it is quarantined. For the thesis its only standing role is cautionary: it
argues against the strong "end-stage is cytokine CYP-suppression" narrative, and it is the reason the detox
sub-story (D2) was dropped rather than promoted.

## F7 — The integrated donor-level pericentral-anchor classification

This finding is the consolidated, information-dense instrument that several downstream findings build on: a
single donor-level table in which each row folds together pericentral depletion, co-expression, identity
turn-off, stress coupling, and tissue source, computed by per-nucleus zonal-anchor classification and
donor-level proportions. Every nucleus is down-thinned to a common 1,500-UMI budget (cells below B dropped),
and within each donor we count nuclei that are pericentral-anchor (detect GLUL and/or CYP3A4 at ≥1 UMI with
fewer than 2 periportal markers), periportal-anchor (≥2 of ASS1/PCK1/HAL/ALDOB at ≥1 UMI with no pericentral
marker), ambient-robust dual co-expression (a pericentral marker at ≥2 UMI and ≥2 periportal markers at ≥2
UMI), and null (neither pole detected), each as a fraction of the donor's down-thinned nuclei. By stage, the
pericentral-anchor fraction is 36 / 19 / 23 / 22 / 21% across F0–F4 (donor-median) — flat and non-monotone,
with no depletion — the ambient-robust dual fraction stays at ~0.05–0.45%, and the null fraction stays at
34–44%, while the 5 explants are heterogeneous and high-stress (3–50% pericentral, stress 6–20 per 10,000).
An honest provenance note: an earlier partition-based classification (census.py/census_v2.py) produced a
deprecated relative "detox within pericentral" column with different numbers; that relative metric is
superseded and not used. This table is the backbone that the sensitivity-grid robustness (F8), the
equivalence bound (F16), and the per-explant scrutiny (F14) all read from.

## F8 — The structural classification is flat across the whole sensitivity grid

This is the positive evidentiary backbone of the preservation claim, and its strength is robustness rather
than any single threshold: the flat donor-level zonal-anchor classification holds across every reasonable
anchor definition and detection threshold rather than one fragile cut. Across the entire sensitivity grid —
GLUL-only / CYP3A4-only / both anchors, per-gene detection threshold k ∈ {1, 2}, periportal rule of 2-of-4
or 3-of-4 markers, ALDOB included or excluded, CPS1-based, and a strict-identity variant — the
pericentral-anchor fraction is flat or non-monotone across biopsy F0–F4 in every variant, indicating no
pericentral depletion, and the null (identity turn-off) fraction is likewise flat. The most decisive result
is the ambient-robustness of co-expression: at a 1-UMI threshold the biopsy dual (co-expression) fraction
looks like ~7–10% (0.071–0.097), which would superficially suggest real de-zonation, but raising the
threshold to the ambient-robust ≥ 2 UMI collapses it to ~0.2–0.6% (0.002–0.006) at every fibrosis stage —
so the apparent co-expression at 1 UMI was ambient RNA soup, not true dual-positive cells, and real
co-expression is near zero and shows no trend. The confounded explants, by contrast, retain a dual fraction
of ~2.9% even at ≥ 2 UMI, about 7× higher. Because the null survives the entire grid rather than resting on
one cut or a single power calculation, this is the converging positive evidence (alongside F1, F9, F15, F16,
and retained GLUL/CYP3A4 identity) that supports decision D3 — though, properly stated, it is a robust null
plus an exclusion of large shifts, not a proof that nothing whatsoever changed.

## F9 — Scenario taxonomy: every de-zonation mechanism enumerated and tested

Rather than fishing for a metric that moves, this finding imposes discipline by enumerating every distinct
way zonation could collapse, mapping each to a specific count-based signature, and testing all of them on
nuclei down-thinned to a common 1,500-UMI budget (donor as the unit), so that no "flat" is asserted without
its own grounding. Depletion (pericentral-anchor fraction falling) is flat and non-monotone at 36 / 19 / 23
/ 22 / 21% across F0–F4. Co-expression (dual-positive fraction rising) collapses from an ambient-soup
~7–10% at 1 UMI to ~0.2–0.6% at the ambient-robust ≥ 2 UMI with no trend. Turn-off (null/double-negative
fraction rising) is flat at 34–44%. Composition shift (periportal-to-pericentral ratio) is roughly flat and
non-monotone at 0.62 / 1.16 / 1.01 / 1.10 / 1.18. Induction (program burden rising) appears only in the
explants (e.g. PCK1 from 0.15 in cirrhotic biopsy to 0.58 in explant), not across the biopsy axis. The
gradient-compression scenario — the previously open gap — is filled by a binomial-down-thinned (B = 1,500,
8-draw Monte-Carlo), donor-balanced (≤ 300 nuclei per donor, so no single donor such as the F4 donor with
~59% of cells can dominate), density-normalized per-cell polarization figure: the mid-mass (fraction of
cells with balance in [0.4, 0.6)) shows only a mild, non-monotone drift (0.21 / 0.22 / 0.24 / 0.28 / 0.26,
peaking at F3 and reverting at F4) while the poles stay dominant (0.47 / 0.41 / 0.39 / 0.32 / 0.38), so the
gradient is present and not collapsed — honestly described as "mild non-monotone drift," not a perfect flat.
Only the explant spikes to a single periportal pole (mid 0.18, poles 0.58). With every scenario covered, the
"preserved" row is simply the null that all the others return, and the systematic coverage is what stops the
analysis from being ad-hoc.

## F10 — What Gribben et al. actually claim, and the honest bound on our correction

This finding fixes the scope of our contribution by reading Gribben et al. (Nature 2024) directly from the
PDF rather than from any secondary prose, so we neither under- nor over-claim. Their headline is explicitly
hepatocyte↔cholangiocyte transdifferentiation/plasticity; de-zonation is framed as a supporting observation
("Hepatocytes lose their zonation... More importantly, our study uncovers transdifferentiation"), and they
claim the zonation loss at both the transcriptional and protein level. Their de-zonation rests on three
evidence legs: (1) the snRNA transcriptional leg, assessed by comparing the correlation between pairs of
periportal and pericentral markers and contrasting with Welch's t-test; (2) immunofluorescence co-staining
of GLUL and ASS1 in single cells (protein); and (3) FLASH 3D imaging of cleared whole organs
(architecture). Critically, their Welch's t-test pools all 47 donors (healthy 4, NAFLD 7, NASH 27,
cirrhosis 4, end-stage 5) — so the tissue-source/procurement confound we quantify in F2/F5 runs straight
through their significance test. We therefore attack only leg #1: the snRNA/transcriptional evidence is a
relative-correlation statistic computed on tissue-source-confounded data, and across the acquisition-matched
biopsy axis we find no transcriptional de-zonation (F1, F8, F9). We cannot and do not refute legs #2–3 —
end-stage cirrhosis genuinely destroys lobular architecture, and snRNA measures per-cell transcriptional
balance, not geometry. So this is a valid correction of one evidence leg plus the progressive-disease
framing, not a debunking of the paper or its imaging.

## F11 — Raw-extraction sanity checks: the audited data foundation

Every molecule-level conclusion in this project depends on the panel being the raw RNA-assay UMI counts and
not the SCT-corrected matrix, so this finding verifies that foundation with 9 explicit falsifiable
assertions, all of which pass. The panel values are non-negative integers (min 0, max 1602), as raw UMIs
must be and SCT fractional data would not be; the per-nucleus library size E_raw equals the authors'
metadata nCount_RNA exactly; the library size spans the raw range 920–49,854 rather than the depth-squeezed
SCT ~3–5.7k band; the panel counts differ from the SCT counts.npz matrix (565 of 800 cell-by-gene entries
differ; RNA median 5,491 versus SCT 4,706), proving we pulled the RNA assay; ALB is a top-burden hepatocyte
gene (43 per 10,000); each cell's panel sum is ≤ E_raw (the panel is a transcriptome subset); the hepatocyte
nucleus count matches Paper 1's reported 69,426; detection is biologically plausible (ALB 0.99, CYP2E1 0.77,
GLUL 0.24, LGR5 0.06, not all-or-nothing); and all analysis-critical genes are present with no silent drop
(RPLP0 legitimately absent, removed at Paper-1 QC). With 9/9 passing, the extracted panel is confirmed as
integer raw UMIs with donor/stage/lobe metadata intact — the audited bedrock under every downstream finding,
and the reason the SCT matrix was abandoned for molecule-level inference.

## F12 — Why the relative z-scored zonation ruler is abandoned, even biopsy-only

This methodological finding explains why we replaced the legacy z-scored relative zonation ruler (a
z(pericentral)−z(periportal) coordinate, with "collapse" read off its spread or anti-correlation) with the
count-based scenario taxonomy, and it identifies two separate reasons. First, the tissue-source confound:
pooling deceased-donor healthy and explant tissue with biopsies puts the dramatic "collapse" in the
confounded explant group, and simply dropping those groups removes most of the apparent collapse — this is
also a Simpson/aggregation effect, since the pooled anti-correlation reverses sign on aggregation
(legacy_simpson.py). Second, and surviving even a biopsy-only analysis, the ruler has an intrinsic weakness:
it is depth- and cell-number-sensitive (each program is standardized across the cells in the dataset, and
shallower F4 biopsies or differing per-donor cell counts change the spread for non-biological reasons), and
it conflates mechanisms (turn-off, true co-expression, and noise all shrink the coordinate's spread, so the
ruler cannot tell them apart — which is the entire motivation for the mechanism-separating taxonomy of F9).
Empirically, a biopsy-only relative "detox drift" (66 → 49 on the relative metric) turned out to be
within-donor spread noise that did not survive the count-based anchor classification. The conclusion is that
the relative ruler is not invalid but indirect, depth-sensitive, and mechanism-conflating; the trustworthy,
mechanism-specific instrument is the count-based anchor classification on down-thinned counts.

## F13 — The 2D joint-count view is a pole-collapse picture, not a co-expression test

This finding is a self-correction about how to read a specific figure. The 2D joint-count plot puts each
nucleus's pericentral-program count on one axis and periportal-program count on the other (after
down-thinning to 1,500 UMIs), and the tempting reading is that de-zonation fills the "both-high" corner. On
audit this reading is wrong for these genes, because the broad 7-gene and 6-gene program sums include
metabolic genes (CPS1, ALDOB, ASS1, the CYPs) that are on in essentially every normal hepatocyte, so "both
programs high" is satisfied by most healthy cells rather than by genuine dual-pole co-expression. Measured
directly (donor-mean fraction with both programs above threshold H), the both-high corner is actually
fuller in biopsy than in explant — at H ≥ 2 it is ~0.80–0.84 across biopsy F0–F4 versus only 0.43 in
explant, and at H ≥ 5 it is ~0.17–0.31 biopsy versus 0.17 explant — the opposite of "fills only in
explants." The explant is lower precisely because it collapsed to the periportal pole (high periportal, low
pericentral). So the 2D figure is a valid pole-collapse visualization, consistent with the
"collapses to a single periportal pole only in explants" reading, but it must not be cited as a
co-expression test. The clean high-amount co-expression conviction lives instead in the strict
mutually-exclusive anchor markers at the ambient-robust ≥ 2 UMI threshold (F8): real dual co-expression is
~0.2–0.6% in biopsy versus ~2.9% in explant. The lesson for the thesis is that the conviction-grade
co-expression evidence is the anchor ≥ 2 dual, not the broad-program 2D.

## F14 — Per-donor end-stage scrutiny: five explants, five different phenotypes

This finding is the load-bearing demonstration that the end-stage group is not one coherent disease program
but a collection of separately-procured organs going in opposite directions, which is why a pooled
marker-correlation (Paper 1's approach) is misleading for it. Classifying each explant donor's nuclei by
zonal anchor (down-thinned to 1,500 UMIs; dual at ambient-robust ≥ 2 UMI), the five explants span an
enormous range: CL104 retains its pericentral pole at 49.7% pericentral-anchor (more than the average biopsy
donor at ~24%), CL16 shows near-total pericentral collapse at 3.2% pericentral and 65.2% periportal (a
periportal-to-pericentral ratio of ~20), CL18 shows a co-expression explosion with 22.4% genuine
ambient-robust dual nuclei, and CL103 and CL17 are periportal-leaning (14.2% and 9.1% pericentral). Across
the five organs the pericentral-anchor fraction ranges 3%→50% and the periportal-to-pericentral ratio ranges
0.13→20. This spread is the signature of heterogeneous, separately-handled organ procurement, not a single
end-stage disease mechanism — and it is the explicit caveat on the F2/F3 group-mean "selective shape," which
is an average over these five discordant donors and must not be read as one program. Combined with the
organ-wide stress (F2/F5) and the perfect collinearity of stage with tissue source, the explant signal is
unattributable to disease and is treated only as a heterogeneous, caveated contrast, never as a clean
positive control.

## F15 — Genome-wide differential expression: the panel-free check (Spearman/Mann–Whitney pseudobulk)

To confirm that the flat zonation result is not an artifact of our curated marker panel, this finding tests
the entire transcriptome with a donor-level pseudobulk analysis. The unit is the donor: pseudobulk is the
sum of raw RNA-assay UMIs over each donor's hepatocyte nuclei (avoiding pseudoreplication) across all 31,257
genes, restricted to the 38 acquisition-matched biopsy donors (F0–F4 distribution 2/8/12/12/4). After
counts-per-million normalization and log2(CPM + 1) transformation and an expression filter (CPM ≥ 1 in ≥ 19
of 38 donors, leaving 17,572 genes tested), we ran a per-gene Spearman correlation of fibrosis stage against
log2-CPM with Benjamini–Hochberg FDR control, plus a Mann–Whitney F1-versus-F4 contrast. The zonation and
xenobiotic genes are flat transcriptome-wide and none are significant: CYP2E1 FDR = 0.98, CYP1A2 = 0.91,
ADH4 = 0.97, SLCO1B3 = 0.80, CYP3A4 = 0.97, GLUL = 0.85, and all periportal genes FDR > 0.79 — so the null
holds well beyond our panel. Only 23 genes trend at FDR < 0.05, and a compositional audit over all 99,809
nuclei shows 15 of 23 are ≥ 3× higher in a non-hepatocyte lineage (mostly ambient, with the non-hepatocyte
fraction not rising with fibrosis, ρ = −0.07), leaving A2M (an acute-phase gene, CPM 219→718) as the one
clear hepatocyte-intrinsic but modest injury response. This both strengthens the genome-wide gene-expression
preservation claim (D3) and kills the detox sub-story (those genes carry FDR 0.80–0.98), since the within-
pericentral detox dip does not survive proper multiple-testing — the only biopsy-internal hepatocyte signal
is a small acute-phase response, not de-zonation.

## F16 — Affirmative equivalence bound: excluding a large coordinated re-zonation

A referee can rightly object that "nothing was significant" is absence-of-evidence rather than
evidence-of-absence, so this finding converts the descriptive null into an affirmative exclusion bound using
two one-sided tests (TOST) / equivalence testing on the donor-level zonal-anchor proportions (no
re-classification — it reuses the F7 donor table). For each contrast and metric we take the observed
between-stage difference in mean donor fraction, build a 90% confidence interval (Welch two-sample t with a
20,000-resample percentile bootstrap as a small-n robustness check), and treat a margin as affirmatively
excluded when the entire 90% CI lies within it. For the headline F1 (n = 8) versus cirrhotic F4 (n = 4)
contrast, the pericentral-anchor fraction difference is only +0.024 (90% CI −0.147 to +0.194), so we exclude
any coordinated pericentral shift larger than about ±0.19 (±0.15 by bootstrap), and the periportal-anchor
difference is −0.019 (CI −0.151 to +0.114), excluding a periportal shift larger than about ±0.15 (±0.12
bootstrap). The better-powered interior contrast, F1 versus F3 (8 vs 12 donors), tightens this: the
pericentral difference is −0.038 (CI −0.119 to +0.043), excluding a shift larger than about ±0.12 (±0.11
bootstrap). In plain terms, a large coordinated re-zonation on the scale of the confounded explant collapse
is affirmatively ruled out across biopsy progression into established cirrhotic-F4 tissue, with the estimates
themselves small and centered near zero. The honest limit, stated plainly, is that a modest drift of ≤ ±0.10
is not excluded — the donor-to-donor fraction variability (pericentral-anchor SD ≈ 0.11–0.15) makes the CIs
wider than ±0.10, especially at F4 (n = 4) — so we rule out large/dramatic re-zonation, not subtle change,
and this bounds donor-level compositional structure, not per-gene expression.

## F17 — Sequencing batch is not randomized (confounded with stage and source)

This data-quality finding asks whether sequencing batch could itself drive the apparent group differences,
and the answer for the cross-source comparison is yes — but in a way that does not threaten the biopsy
analysis. Parsing the SLX sequencing run from orig.ident (13 runs over 47 donors), the run almost perfectly
predicts tissue source: Cramér's V(run, source) = 0.84 (where 1 is the maximum, meaning sequencing run
nearly determines tissue source), and 9 of the 13 runs carry only a single disease stage, with the
organ-cube groups largely on dedicated runs (healthy-only SLX-21151; end-stage-only SLX-19940/21153/21155).
So samples were sequenced in stage- and source-clustered batches, not randomized — another collinear layer
of the same confound (tissue source + procurement + now sequencing batch) for the deceased-donor groups,
though those are already excluded from the disease axis. Within the 38 biopsy donors, however, the
confounding is weaker and partly crossed: Cramér's V(run, fibrosis) = 0.40, and critically the 4 F4 biopsy
donors sit on 2 runs (SLX-20270 and SLX-20290) that each also carry F0–F3 donors, so the F1-versus-F4
fibrosis effect is estimable within-batch and is not collinear with run. The biopsy DGE is therefore not a
pure batch artifact, and the analysis is bounded honestly by within-run sensitivity checks and
leave-one-donor-out rather than by an over-parameterized 13-level run factor at n = 38. For the thesis this
shows the explant signal is irrecoverably batch-confounded while the biopsy null is defensible.

## F18 — Plan A genome-wide DGE (edgeR): zonation null confirmed; biliary hits look ambient (not yet decisive)

This finding is the discovery-grade genome-wide differential-expression analysis using pseudobulk per donor
(raw UMIs, hepatocytes) with edgeR TMM normalization and a quasi-likelihood negative-binomial F-test
(robust = TRUE), across the 38 biopsy donors (F0–F4 = 2/8/12/12/4, common biological coefficient of
variation 0.405), with F4-versus-F1 as the primary contrast. The zonation result holds on this independent
gold-standard method: every zonation and detox gene is non-significant (FDR 0.43–0.96 — GLUL, CYP2E1,
CYP3A4, CPS1, ASS1, ALDOB all flat; detox genes ADH4 −0.54 and SLCO1B3 −0.64 in log2 fold-change but none
survive FDR), the housekeeping negative control is flat (no HK gene FDR-significant, confirming sound
normalization), and the dropped detox dip (D2) stays dropped. The discovery is that 64 genes reach FDR <
0.05 (62 up), and they form a biliary/ductular program — EPCAM +2.3, GRHL2 +3.1, SPINT2 +2.7, SOX4, SOX9,
plus inflammatory CXCL10 +5.4 — which are exactly Paper 1's plasticity/transdifferentiation markers, and
which (correcting F10's earlier detection-fraction wording) genuinely rise into cirrhotic F4 biopsy, not only
into explants. The most parsimonious reading is that this is cholangiocyte ambient spillover, not hepatocyte
transdifferentiation: a cross-lineage compositional audit over all 99,809 nuclei finds 54 of 64 hits are
ambient and every headline marker is massively cholangiocyte-dominant (GRHL2 78×, EPCAM 25×, SOX9 15×, SOX4
7× cholangiocyte-over-hepatocyte), with the cholangiocyte fraction elevated at F4 (median 8.3% versus ~2–4%
earlier; the ductular reaction), so the apparent hepatocyte rise is spillover from an expanding
cholangiocyte population; the F1–F3 interior is near-flat (F3-vs-F1 only 3 scattered genes, biliary markers
non-significant). Crucially, this is stated honestly as NOT YET CONFIRMED — the ambient reading is in tension
with Paper 1 and is pending a decontX/SoupX ambient-removal re-run and biological review — and we explicitly
neither confirm nor refute their transdifferentiation, because "more cholangiocytes at F4" is neutral
between a ductular reaction and hepatocytes becoming biliary, and snRNA pseudobulk cannot distinguish them
without lineage tracing. So our positive statement is only that there is no hepatocyte-intrinsic disease
program detectable in the matched biopsy axis; their imaging/co-staining/end-stage evidence is untouched.

## D1 — End-stage explant tissue is analyzed separately from the F0–F4 biopsy axis

This is a standing methodological decision rather than a single result: the end-stage explant group is a
procurement artifact (established by the F2/F5 organ-wide stress, the F17 batch confound, and the F14
per-donor heterogeneity), and the perfect collinearity of disease stage with tissue source means any
explant-versus-biopsy difference is unattributable to disease. Therefore the explants are excluded from the
disease axis and treated only as a separate, caveated contrast, never as a disease endpoint or a clean
positive control. The decision also fixes which analyses carry the real F0–F4 conclusions: the in-depth
later methods — the depth-controlled per-nucleus zonal-anchor classification, the all-sets and
sensitivity-grid robustness, and the genome-wide differential expression — not the early high-level
screenshot tables, which are descriptive and must not be used to draw final F0–F4 verdicts. For the overall
thesis, D1 is what isolates the dramatic "de-zonation" into the confounded explant compartment and lets the
acquisition-matched biopsy axis speak cleanly.

## D2 — Drop the detox-attenuation sub-story

This standing decision retires the "biopsy-internal detox attenuation" as a finding because it does not
survive scrutiny on any axis. It is confounded with tissue source, it is not robust genome-wide (the
within-pericentral detox dip that twitched from ~12.7 to ~8.9 down-thinned UMIs is overturned by the
genome-wide pseudobulk analysis, where all detox genes carry FDR 0.80–0.98 in F15 and FDR 0.43–0.96 in the
edgeR analysis F18), and it is entangled with the quarantined and not-understood NAS/ballooning result (F6).
The honest account of how it ever entered the narrative is instructive: when the structural anchor
classification came up flat, the within-pericentral detox dip was the only thing that moved at all and got
over-promoted into a story. Per this decision the detox genes (CYP2E1, CYP1A2, ADH4, AKR1D1, SLCO1B3) are
kept only as pericentral markers within the anchor classification and within the end-stage descriptive shape
(where detox-down is part of the confounded explant phenotype), and the standalone detox-attenuation
narrative is removed from the write-up. For the thesis this tightens the central null: there is no
biopsy-internal hepatocyte change to point to, detox included.

## D3 — The scoped positive claim: gene-expression zonation is preserved across biopsy F1→cirrhotic F4

This standing decision states the central positive claim and scopes it carefully. We do affirm that the
hepatocyte gene-expression (transcriptional) zonation signal is preserved across the acquisition-matched
biopsy MASLD axis from F1 into established cirrhotic F4 — grounded not in a power calculation but in
converging positive evidence: the sensitivity-grid-robust flat zonal-anchor classification (F8), all-sets
marker invariance, genome-wide flatness with zonation-gene FDR > 0.79 (F15) and the edgeR confirmation
(F18), retained GLUL and CYP3A4 pericentral identity, the collapse of apparent co-expression to ambient soup
at the ≥ 2 UMI threshold (F8), the donor-balanced polarization figure showing both poles retained (F9), and
the affirmative equivalence bound that excludes a large coordinated re-zonation larger than about ±0.12–0.19
(F16). The three standard objections to "preserved" are weighed explicitly: pseudoreplication (the F4 donor
contributing ~59% of cells) is defused because inference is donor-level (n = 4 donors at F4, not the cells)
and the figures are donor-balanced; the minimal-detectable-effect/power concern is demoted to a
footnote-bound that constrains only the thin extremes (F0 n = 2, F4 n = 4) while the well-populated interior
F1–F3 (n = 8/12/12) is flat and adequately powered; and the genuinely valid objection — that needle-biopsy
snRNA measures per-cell transcriptional balance, not lobule geometry — is kept as the explicit architecture
caveat. So the claim is scoped to gene-expression/compositional preservation with an exclusion of large
shifts (a modest ≤ ±0.10 drift is not ruled out), not to spatial/architectural preservation, and it is this
scoped, honestly-bounded positive that corrects the transcriptional leg of Gribben et al. without overturning
their imaging or plasticity headline.
