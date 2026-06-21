#!/usr/bin/env python3
"""SINGLE UNIFIED ORCHESTRATOR for the whole zonation-ruler study.

One explicit ruler registry (no hidden config defaults), covering BOTH gene-set rulers and
learned PROJECTION rulers (dense PCA, regularized, supervised). Every ruler goes through the
SAME donor-level battery and writes to results/tables/<set>/. Then it summarizes, plots the
panel, and builds the narrative + per-set PDF reports.

Pipeline:
  0. ensure candidate gene sets exist        (build_candidate_sets.py)
  1. ensure learned coordinates exist         (step4c: supervised/unsupervised/unsupervised_p2/lasso/elasticnet)
  2. load_qc once (+ optional classifier entropy if present)
  3. for each ruler -> score|project -> validate gate -> ruler diag -> H1 -> H3 -> H2
  4. summarize (healthy-ruler selection) -> panel -> H2b program analysis -> LaTeX reports

Run:  python src/run_everything.py
"""
import os, sys, subprocess
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # src/
import config
from steps.common import log, OUT, PLAST, VAL, set_dir
from steps.step2_load_qc import load_qc
from steps.step4_score import score, zrows
from steps.step5_validate import validate
from steps.step5b_ruler_diagnostics import ruler_diagnostics
from steps.step6_collapse import collapse
from steps.step7_de import h2_slope_loss, de
from steps.step8_plasticity import plasticity

CAND = config.SIGNATURES / "candidates"
K_SLOPE = 20

# ---- THE explicit ruler registry (kind: 'geneset' = score PC/PP lists; 'projection' = learned coord) ----
RULERS = [
    ("paper2_landmark", "geneset"), ("core_curated", "geneset"), ("expanded_curated", "geneset"),
    ("paper2_top50", "geneset"), ("paper2_top100", "geneset"), ("paper2_top250", "geneset"),
    ("paper2_full", "geneset"),
    ("unsupervised_top50", "geneset"), ("unsupervised_top100", "geneset"),
    ("unsupervised_top250", "geneset"), ("unsupervised_full", "geneset"),
    ("unsupervised_lasso", "geneset"), ("unsupervised_elasticnet", "geneset"),
    ("unsupervised", "projection"), ("unsupervised_p2", "projection"),
    ("unsupervised_combined", "projection"), ("supervised", "projection"),
]
# learned coords that step4c must have produced (name -> step4c mode)
LEARNED = {"supervised": "supervised", "unsupervised": "unsupervised",
           "unsupervised_p2": "unsupervised_p2", "unsupervised_combined": "unsupervised_combined",
           "unsupervised_lasso": "lasso", "unsupervised_elasticnet": "elasticnet"}


def _py(*args):
    subprocess.run([sys.executable, *args], cwd=os.path.dirname(os.path.abspath(__file__)), check=False)


def ensure_inputs():
    if not (CAND / "pericentral_paper2_landmark.txt").exists():
        log("building candidate gene sets ..."); _py("build_candidate_sets.py")
    for name, mode in LEARNED.items():
        if not os.path.exists(os.path.join(OUT, f"coordinates_learned_{name}.csv")):
            log(f"generating learned coords: {name} ..."); _py("steps/step4c_learned_coords.py", mode)
    # ensure the unsupervised pole gene sets exist (top50/100/250 + full)
    if not (CAND / "pericentral_unsupervised_full.txt").exists():
        _py("steps/step4c_learned_coords.py", "export_poles")


def geneset_provider(M, genes, lib, which, bars, donor, stage):
    pcf, ppf = CAND / f"pericentral_{which}.txt", CAND / f"periportal_{which}.txt"
    if not (pcf.exists() and ppf.exists()):
        return None
    PC = [g.strip() for g in open(pcf) if g.strip()]; PP = [g.strip() for g in open(ppf) if g.strip()]
    coord, pc, pp, _pl, col = score(M, genes, lib, PC, PP, which=which)
    pd.DataFrame({"signature_set": which, "cell_id": bars, "donor": donor, "stage": stage,
                  "coord": coord, "pc": pc, "pp": pp}).to_csv(os.path.join(set_dir(which), "coordinates.csv"), index=False)
    return coord, pc, pp, col, PC, PP


def projection_provider(M, genes, lib, which, bars, donor, stage, n_pole=50):
    cpath = os.path.join(OUT, f"coordinates_learned_{which}.csv")
    spath = os.path.join(OUT, f"learned_signature_{which}.csv")
    if not (os.path.exists(cpath) and os.path.exists(spath)):
        return None
    coord = pd.read_csv(cpath).set_index("cell_id")["coord"].reindex(bars).astype(float).values
    sdf = pd.read_csv(spath)
    scol = next(c for c in sdf.columns if sdf[c].dtype.kind == "f")
    sdf = sdf[sdf["gene"].isin(set(genes))].sort_values(scol)
    PP = sdf["gene"].head(n_pole).tolist(); PC = sdf["gene"].tail(n_pole).tolist()
    col = zrows(M, genes, lib, set(PC + PP + VAL["pericentral"] + VAL["periportal"]))
    pc = np.mean([col[g] for g in PC if g in col], 0); pp = np.mean([col[g] for g in PP if g in col], 0)
    pc = (pc - pc.mean()) / (pc.std() + 1e-9); pp = (pp - pp.mean()) / (pp.std() + 1e-9)
    pd.DataFrame({"signature_set": which, "cell_id": bars, "donor": donor, "stage": stage,
                  "coord": coord, "pc": pc, "pp": pp}).to_csv(os.path.join(set_dir(which), "coordinates.csv"), index=False)
    return coord, pc, pp, col, PC, PP


def main():
    ensure_inputs()
    M, genes, bars, stage, donor, lib = load_qc()
    pcol = zrows(M, genes, lib, set(PLAST))
    plast = (np.mean([pcol[g] for g in PLAST if g in pcol], 0) if any(g in pcol for g in PLAST)
             else np.zeros(len(bars)))
    entp = os.path.join(OUT, "classifier_entropy.csv")
    entropy = pd.read_csv(entp, low_memory=False).set_index("cell_id")["entropy"] if os.path.exists(entp) else None

    status = []
    for which, kind in RULERS:
        log(f"\n================  RULER: {which} [{kind}]  ================")
        prov = (projection_provider(M, genes, lib, which, bars, donor, stage) if kind == "projection"
                else geneset_provider(M, genes, lib, which, bars, donor, stage))
        if prov is None:
            log(f"  inputs missing for {which} — recorded, skipping.");
            status.append({"signature_set": which, "kind": kind, "built": False}); continue
        coord, pc, pp, col, PC, PP = prov
        rep, passed = validate(coord, col, stage, entropy=entropy, which=which)
        ruler_diagnostics(coord, pc, pp, col, stage, donor, PC, PP, which=which)
        if not passed:
            status.append({"signature_set": which, "kind": kind, "built": True, "validation_pass": False}); continue
        collapse(coord, pc, pp, stage, donor, entropy=entropy, bars=bars, which=which)
        plasticity(coord, plast, stage, donor, which=which)
        if min(sum(g in set(genes) for g in PC), sum(g in set(genes) for g in PP)) >= 4:
            h2_slope_loss(M, genes, lib, col, coord, stage, donor, PC, PP, which=which, K=K_SLOPE)
        if which == "paper2_full":
            de(M, genes, lib, coord, stage, donor, set(PC + PP), which=which)
        status.append({"signature_set": which, "kind": kind, "built": True, "validation_pass": True})
    pd.DataFrame(status).to_csv(os.path.join(OUT, "battery_run_status.csv"), index=False)

    log("\n--- summarize + panel + program-analysis + reports ---")
    _py("summarize_signature_battery.py")
    _py("make_panel_figure.py")
    for s in ("paper2_full", "unsupervised"):
        _py("h2_program_analysis.py", s)
    _py("h2_transcriptome_wide.py", "expanded_curated")   # H2c: every gene, donor-level
    _py("unsupervised_axis_eval.py")
    _py("make_latex_report.py")        # per-set results dossier
    _py("make_narrative_report.py")    # narrative analysis report
    log("\nDONE. Inspect: results/Zonation_Narrative_Report.pdf (analysis), "
        "results/Zonation_Ruler_Report.pdf (per-set), "
        "results/tables/signature_battery_summary.csv, results/figures/ruler_panel.png")


if __name__ == "__main__":
    main()
