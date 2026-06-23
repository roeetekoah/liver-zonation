# Findings — organized store

One subfolder per finding. Each subfolder holds the **data file(s)** (the actual numbers) and a local
`README.md` that states, precisely: what the finding is, **what every number means and how it was
computed** (script + metric definition), the honest caveats, the verdict/status, and the grounding.

The audited index with status verdicts lives in [`../CLAIMS_LEDGER.md`](../CLAIMS_LEDGER.md); each ledger
entry points here.

## Index
| Finding | Folder | Status | One line |
|---|---|---|---|
| F1 | [lobe_invariance/](lobe_invariance/) | LIVE (caveated) | Within explants the zonation pattern is lobe-invariant (detection); caudate/multi-lobe sampling does not manufacture the de-zonation signal. Primary stage analysis is right-lobe-only. |
| F2 | [stress_and_panel_by_stage/](stress_and_panel_by_stage/) | LIVE | Stress (IEG+HSP) is elevated in both deceased-donor groups (healthy + end-stage), far more in end-stage; uniformly low across needle biopsies. The sampling confound, quantified. |
| F3 | [stress_and_panel_by_stage/](stress_and_panel_by_stage/) | LIVE (caveat: group-mean masks 5 discordant explants) | End-stage gene shape = selective detox loss + periportal induction + PC identity retained — NOT a "turn-off"; confined to end-stage, lobe-invariant. (same data as F2) |
| F5 | [stress_celltype_segmented/](stress_celltype_segmented/) | LIVE | Cross-lineage stress segmented IEG/HSP/HIF: IEG organ-wide (hep 18.5× ≈ endothelial 18.2×), HIF weak (≤2.6×) → acute handling, not hypoxia. |
| F6 | [nas_components_detox/](nas_components_detox/) | **QUARANTINED** | NAS-component/detox test — confusing result (inflammation n.s., ballooning −0.42 p=.008); not understood, pending a talk-down (queue O6). Do NOT cite. |
| F7 | [integrated_census/](integrated_census/) | LIVE | The integrated donor-level PC-anchor classification (depletion+co-expression+turn-off+stress+source folded into one table); scales documented; reproducible via load_bearing.py. |
| F8 | [census_robustness/](census_robustness/) | LIVE | The structural anchor-classification is flat across the WHOLE sensitivity grid (every anchor def, k, periportal rule); dual co-expression = ambient soup (collapses at ≥2 UMI). The positive case for "zonation preserved". |
| F9 | [scenario_taxonomy/](scenario_taxonomy/) | LIVE | Every de-zonation scenario grounded row-by-row (signature+script+metric+numbers+conclusion); incl. the down-thinned to B=1,500, donor-balanced, density-normalized gradient figure. The full mechanism-coverage finding. |
| F10 | [paper1_contribution/](paper1_contribution/) | LIVE | What Paper 1 actually claims (verbatim from PDF) and exactly what we can/cannot say: we correct only the snRNA/transcriptional leg of de-zonation; protein/imaging legs untouched; not an overturning. |
| F11 | [sanity_checks/](sanity_checks/) | LIVE | 9/9 raw-extraction sanity checks (each a falsifiable assertion) — the audited data foundation. |
| F12 | [relative_ruler_postmortem/](relative_ruler_postmortem/) | LIVE | Why the z-scored relative ruler is abandoned even biopsy-only: depth-sensitive + conflates mechanisms (turn-off/de-zonation/noise all shrink spread). The count anchor-classification replaced it. |
| F13 | [joint_count_2d/](joint_count_2d/) | LIVE (correction) | The broad-program 2D joint-count is a pole-collapse visual, NOT a co-expression test (both programs on in normal hepatocytes). Clean co-expression conviction = anchor ≥2 dual (F8). |
| F14 | [explant_heterogeneity/](explant_heterogeneity/) | LIVE | Per-donor end-stage anchor scrutiny: the 5 explants are 5 different phenotypes (CL104 retains PC 50%, CL16 collapses PP:PC≈20, CL18 dual 22%). End-stage is not one program. |
| F15 | [genome_wide_dge/](genome_wide_dge/) | LIVE | Genome-wide donor-level DE, explicit method: 31,257-gene pseudobulk → 17,572 tested (CPM≥1 in ≥19/38 donors), CPM+log2, Spearman+BH-FDR. Zonation flat genome-wide; detox dip falsified. |
| F16 | [equivalence_bound/](equivalence_bound/) | LIVE | Affirmative equivalence bound for the preservation claim (O12): across biopsy F1→cirrhotic-F4 we EXCLUDE a coordinated PC-anchor shift larger than ≈±0.12–0.19; a modest ≤±0.10 drift is not excluded. Supports D3. |
| F17 | [batch_randomization/](batch_randomization/) | LIVE | Sequencing batch is NOT randomized — run predicts tissue source (Cramér's V=0.84; 9/13 runs single-stage). Biopsy F1-vs-F4 salvageable (V=0.40; F4 mixed into 2 multi-stage runs → estimable within-batch). |
| F18 | [dge_plan_a/](dge_plan_a/) | LIVE | Plan A genome-wide DGE (edgeR): zonation genes show NO detectable change; housekeeping flat. 64 F1→F4 hits = a biliary program. decontX result: **partly ambient** (SOX4/SOX9 drop below significance) but EPCAM/B3GNT3/SPINT2/CXCL10 **survive** — residual source unresolved (ambient/doublets/real). Paper 1 named NO ambient tool. |
| F19 | [zonation_preserved/](zonation_preserved/) | LIVE | The full zonation-preservation claim: 3 grounds (marker genes flat F15/F18; proportions flat across the grid F8; equivalence bound F16 excludes shifts >~±0.15) + the equivalence explained + "what this claim is NOT". |
| F20 | [dge_plan_b/](dge_plan_b/) | LIVE | Plan B within-class DGE: zonation flat in every class (0/13); the only program (biliary GRHL2/EPCAM/SPINT2) appears uniformly across PC/PP/null/dual = class-agnostic = ambient-like. Reinforces F18. |
| F21 | [doublet_chase/](doublet_chase/) | LIVE | Doublet chase: the decontX-surviving biliary genes are NOT hepatocyte-intrinsic. ~97% is diffuse ambient; the rest is genuine hepatocyte–cholangiocyte doublets (KRT19/KRT7≥2, ~4.5× inflated total counts) that rise 17× F1→F4 and sit entirely below Paper 1's 50,000-count filter (0/42,579 over it). Resolves F18's "residual unresolved". |
| — | [downsampling_method/](downsampling_method/) | methods | The binomial down-thinning depth control: precise definition, verified citations (DropletUtils/Lun, OSCA/Amezquita 2020, 10x), and its limitations/biases. |

**Terminology:** "down-thinned to B=1,500" everywhere = binomial down-thinning of raw UMIs to a common budget B (=1500),
cells below B dropped, Monte-Carlo averaged over N draws (4 or 8). "Ambient-robust" = observed UMI ≥ 2.

_(grows as we audit items, one by one)_
