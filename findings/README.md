# Findings — organized store (ordered by the story)

One subfolder per finding. Each holds the **data file(s)** (the actual numbers) and a local `README.md` stating
precisely: what the finding is, **what every number means and how it was computed** (script + metric), the honest
caveats, the verdict/status, and the grounding.

This index is now ordered to follow the **story** (see [`../FINDINGS.md`](../FINDINGS.md) for the summary and
[`../reports/FULL_STORY.txt`](../reports/FULL_STORY.txt) for the full narrative). The audited claim-by-claim trail
with decisions and the future-work queue is [`../CLAIMS_LEDGER.md`](../CLAIMS_LEDGER.md).

**Terminology:** "down-thinned to B=1,500" = binomial down-thinning of raw UMIs to a common budget (1,500), cells
below B dropped, Monte-Carlo averaged. "Ambient-robust" = observed UMI ≥ 2. Several scenario labels (depletion /
dimming / co-expression / gradient compression / turn-off / composition shift / induction / preserved) and the
"anchor classification" are our own coinages, defined where used.

---

## Part 1 — The central confound (tissue source ⟂ disease stage)
The load-bearing reframe. There is no single folder — it is grounded in Paper 1's Methods and quantified in
[`../reports/SYNTHESIS.md`](../reports/SYNTHESIS.md) §1 and [`../CLAIMS_LEDGER.md`](../CLAIMS_LEDGER.md) Item 1 /
Decision D1. Disease F0–F4 = needle biopsies; healthy + end-stage = deceased-donor organ tissue.

## Part 2 — Lobe invariance (clears one sub-confound)
| Finding | Folder | Status | One line |
|---|---|---|---|
| F1 | [lobe_invariance/](lobe_invariance/) | LIVE (caveated) | Within explants the zonation **detection** pattern is lobe-invariant; caudate/multi-lobe sampling does not manufacture the de-zonation signal. Primary stage analysis is right-lobe-only. |

## Part 3 — Procurement stress, by stage (the "why exclude the ends" evidence)
| Finding | Folder | Status | One line |
|---|---|---|---|
| F2 | [stress_and_panel_by_stage/](stress_and_panel_by_stage/) | LIVE | Stress (IEG+HSP) elevated in both deceased-donor groups (healthy + end-stage), far more in end-stage; uniformly low across needle biopsies. The sampling confound, quantified. |
| F3 | [stress_and_panel_by_stage/](stress_and_panel_by_stage/) | LIVE (caveat) | End-stage gene shape = selective detox loss + periportal induction + PC identity retained — NOT a "turn-off"; confined to end-stage, lobe-invariant. (same data as F2) |
| F5 | [stress_celltype_segmented/](stress_celltype_segmented/) | LIVE | Cross-lineage stress: IEG organ-wide (hep 18.5× ≈ endothelial 18.2×), HIF weak (≤2.6×) → acute handling, not hypoxia. The decisive control. |

## Methods — the depth control used throughout
| Finding | Folder | Status | One line |
|---|---|---|---|
| — | [downsampling_method/](downsampling_method/) | methods | Binomial down-thinning depth control: precise definition, verified citations, limitations/biases. |

## Part 4 — The main zonation test: anchor classification + scenario coverage
| Finding | Folder | Status | One line |
|---|---|---|---|
| F8 | [census_robustness/](census_robustness/) | LIVE | The structural anchor classification is flat across the WHOLE sensitivity grid; dual co-expression = ambient soup (collapses at ≥2 UMI). The positive case for "zonation preserved." |
| F9 | [scenario_taxonomy/](scenario_taxonomy/) | LIVE | Every de-zonation scenario (depletion/dimming/co-expression/gradient-compression/turn-off/composition-shift/induction) grounded row-by-row with numbers. Full mechanism coverage. |
| F7 | [integrated_census/](integrated_census/) | LIVE | The integrated donor-level anchor-classification table (depletion+co-expression+turn-off+stress+source in one); scales documented; reproducible. |
| F19 | [zonation_preserved/](zonation_preserved/) | LIVE | **The consolidated preservation claim**: 3 grounds (markers flat F15/F18; proportions flat across the grid F8; equivalence bound F16) + the equivalence explained + "what this claim is NOT." |

## Part 5 — Why we changed the measurement
| Finding | Folder | Status | One line |
|---|---|---|---|
| F12 | [relative_ruler_postmortem/](relative_ruler_postmortem/) | LIVE | Why the z-scored relative ruler is abandoned even biopsy-only: depth-sensitive + conflates mechanisms. The count anchor classification replaced it. |

## Part 6 — The 2D joint-count view (and its correction)
| Finding | Folder | Status | One line |
|---|---|---|---|
| F13 | [joint_count_2d/](joint_count_2d/) | LIVE (correction) | The broad-program 2D is a pole-collapse visual, NOT a co-expression test. Clean co-expression conviction = anchor ≥2 dual (F8). |

## Part 7 — End-stage explants are heterogeneous (important)
| Finding | Folder | Status | One line |
|---|---|---|---|
| F14 | [explant_heterogeneity/](explant_heterogeneity/) | LIVE | Per-donor end-stage scrutiny: the 5 explants are 5 phenotypes (CL104 retains PC 50%, CL16 collapses PP:PC≈20, CL18 dual 22%). End-stage is not one program. |

## Part 8 — Bounding the absence of a large shift
| Finding | Folder | Status | One line |
|---|---|---|---|
| F16 | [equivalence_bound/](equivalence_bound/) | LIVE | Affirmative equivalence bound: across biopsy F1→F4 we exclude a large shift (~20 pp; interior ~12 pp); a subtle ≤10 pp drift is NOT excluded. |
| F17 | [batch_randomization/](batch_randomization/) | LIVE | Sequencing batch is NOT randomized (run⟂source V=0.84). Biopsy biliary hits survive a run-covariate and a single-run test → not a batch artifact. |

## Part 9 — Genome-wide differential expression
| Finding | Folder | Status | One line |
|---|---|---|---|
| F15 | [genome_wide_dge/](genome_wide_dge/) | LIVE | Genome-wide donor-level DE (Spearman+BH): zonation flat genome-wide; the detox dip falsified. The first genome-wide pass. |
| F18 | [dge_plan_a/](dge_plan_a/) | LIVE | **The DGE finding** (edgeR pseudobulk): (1) zonation flat → independent count-based check on preserved zonation (sanity check, not the primary proof); (2) genome-wide nothing else moves except a biliary-marker burden + candidate-inflammatory CXCL10. KEY caveat O13: gene-set test still owed. |
| F20 | [dge_plan_b/](dge_plan_b/) | LIVE (**subordinate** to F18) | Within-class DGE: robustness check, confirmatory given flat proportions (F8). Zonation flat in every PC/PP/null/dual class; no within-zone program hides under pooling. |

## Part 10 — Interpreting the biliary-marker burden (a side lead, not closed)
| Finding | Folder | Status | One line |
|---|---|---|---|
| F18 | [dge_plan_a/](dge_plan_a/) | LIVE | Source-attribution section: cross-lineage burden 5–78×, ductular reaction at F4, ≤0.4% per-cell co-expression, decontX 64→34 (SOX4/SOX9 drop); CXCL10 carved out as candidate inflammation. |
| F21 | [doublet_chase/](doublet_chase/) | **EXPLORATORY LEAD** (not a finding) | Crude source-attribution probe: ambient + rare co-capture/biphenotypic nuclei below Paper 1's 50,000-count filter (0/42,579 over it); cannot separate doublet from rare transdifferentiating cell. |

## Scope — what the paper claims and what we correct
| Finding | Folder | Status | One line |
|---|---|---|---|
| F10 | [paper1_contribution/](paper1_contribution/) | LIVE | What Paper 1 actually claims (verbatim from PDF) and exactly what we can/cannot say: we correct only the snRNA/transcriptional de-zonation leg; protein/imaging legs untouched; not an overturning. |

## Supporting / data foundation
| Finding | Folder | Status | One line |
|---|---|---|---|
| F11 | [sanity_checks/](sanity_checks/) | LIVE | 9/9 raw-extraction sanity checks (each a falsifiable assertion) — the audited data foundation. |

## Quarantined — do NOT cite
| Finding | Folder | Status | One line |
|---|---|---|---|
| F6 | [nas_components_detox/](nas_components_detox/) | **QUARANTINED** | NAS-component/detox test — confusing result (inflammation n.s., ballooning −0.42 p=.008); not understood, pending a talk-down (O6). Do NOT cite. |

_(F-numbers are stable identifiers from the audit order; the sections above give the story order.)_
