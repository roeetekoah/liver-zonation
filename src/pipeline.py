#!/usr/bin/env python3
"""
Spatial Degradation of Hepatocyte Zonation — ORCHESTRATOR (Steps 2-8), DONOR-LEVEL.

Thin orchestrator: every step lives in src/steps/ (single source of truth). main() wires
them. Unit of inference = DONOR, never cell.

Coordinate sets compared head-to-head, each through the SAME battery
(validate gate -> ruler -> H1 collapse -> H3 plasticity -> H2 slope-loss):
  * signature sets (config.SETS_TO_COMPARE, e.g. paper2_landmark, full): coord = mean_z(PC)-mean_z(PP).
  * learned sets (LEARNED_SETS: unsupervised PCA axis, supervised whole-transcriptome LR):
    coordinates produced by steps/step4c_learned_coords.py and INGESTED from CSV here; their
    +/- gene poles act as the PC/PP gene lists for the battery.

Run from src/:  python pipeline.py        (run step4c first to populate learned coords)
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # src/ on path
import config
from steps.common import log, OUT, PLAST, VAL, set_dir
from steps.step2_load_qc import load_qc
from steps.step4_score import score, load_signature_set, zrows
from steps.step5_validate import validate
from steps.step5b_ruler_diagnostics import ruler_diagnostics
from steps.step6_collapse import collapse
from steps.step7_de import h2_slope_loss, de
from steps.step8_plasticity import plasticity

# ---- orchestration knobs ----
RUN_CLASSIFIER = True            # run Step 4b (auxiliary entropy) before the per-set loop
LEARNED_SETS = ["unsupervised", "supervised"]   # ingested from step4c CSVs (skipped if absent)
K_SLOPE = 20                     # held-out splits for H2 (drop to 5 for a fast demo)
N_POLE = 50                      # genes per pole used as PC/PP lists for learned coords


def _load_entropy():
    p = os.path.join(OUT, "classifier_entropy.csv")
    if not os.path.exists(p): return None
    try:
        e = pd.read_csv(p, low_memory=False)
        log("  (found classifier_entropy.csv — merging AUXILIARY entropy into collapse)")
        return e.set_index("cell_id")["entropy"]
    except Exception as ex:
        log(f"  (could not read classifier_entropy.csv: {ex})"); return None


def _signature_provider(M, genes, lib, which, bars, donor, stage):
    PC, PP = load_signature_set(which)
    coord, pc, pp, _plast, col = score(M, genes, lib, PC, PP, which=which)
    pd.DataFrame({"signature_set": which, "cell_id": bars, "donor": donor, "stage": stage,
                  "coord": coord, "pc": pc, "pp": pp}
                 ).to_csv(os.path.join(set_dir(which), "coordinates.csv"), index=False)
    return coord, pc, pp, col, PC, PP


def _learned_provider(M, genes, lib, which, bars, n_pole=N_POLE):
    """Ingest a learned coordinate (step4c). Its top/bottom gene poles become the PC/PP lists,
    so the standard battery (anticorr, ruler split-half, H2 slope-loss) applies."""
    cpath = os.path.join(OUT, f"coordinates_learned_{which}.csv")
    spath = os.path.join(OUT, f"learned_signature_{which}.csv")
    if not (os.path.exists(cpath) and os.path.exists(spath)):
        log(f"  [{which}] learned artifacts missing — run "
            f"`python steps/step4c_learned_coords.py {which}` first; skipping set.")
        return None
    coord = pd.read_csv(cpath).set_index("cell_id")["coord"].reindex(bars).astype(float).values
    sdf = pd.read_csv(spath)
    scol = "pc_minus_pp_coef" if "pc_minus_pp_coef" in sdf.columns else "loading"  # both: + = pericentral
    sdf = sdf[sdf["gene"].isin(set(genes))].sort_values(scol)
    PP = sdf["gene"].head(n_pole).tolist()    # most negative loading/coef = periportal pole
    PC = sdf["gene"].tail(n_pole).tolist()    # most positive = pericentral pole
    col = zrows(M, genes, lib, set(PC + PP + VAL["pericentral"] + VAL["periportal"]))
    pc = np.mean([col[g] for g in PC if g in col], axis=0)
    pp = np.mean([col[g] for g in PP if g in col], axis=0)
    pc = (pc - pc.mean()) / (pc.std() + 1e-9); pp = (pp - pp.mean()) / (pp.std() + 1e-9)
    return coord, pc, pp, col, PC, PP


def main():
    M, genes, bars, stage, donor, libsize = load_qc()                    # Step 2: load/QC
    # plasticity score (coordinate-independent) — computed once, reused for every set
    pcol = zrows(M, genes, libsize, set(PLAST))
    plast = (np.mean([pcol[g] for g in PLAST if g in pcol], axis=0)
             if any(g in pcol for g in PLAST) else np.zeros(len(bars)))

    if RUN_CLASSIFIER:
        log("\n--- Step 4b (pre-step, independent of scoring): classifier entropy (auxiliary) ---")
        try:
            from steps.step4b_classifier import main as classifier_main
            classifier_main()
        except Exception as ex:
            log(f"  classifier skipped: {ex}")
    entropy = _load_entropy()

    sets = list(getattr(config, "SETS_TO_COMPARE", [config.DEFAULT_SET])) + LEARNED_SETS
    for which in sets:
        log(f"\n================  COORDINATE SET: {which}  ================")
        prov = (_learned_provider(M, genes, libsize, which, bars) if which in LEARNED_SETS
                else _signature_provider(M, genes, libsize, which, bars, donor, stage))
        if prov is None:
            continue
        coord, pc, pp, col, PC, PP = prov
        rep, passed = validate(coord, col, stage, entropy=entropy, which=which)      # Step 5 GATE
        if not passed:
            log(f"  GATE FAILED for set '{which}' — skipping collapse/plasticity/H2.")
            continue
        ruler_diagnostics(coord, pc, pp, col, stage, donor, PC, PP, which=which)     # Step 5b
        collapse(coord, pc, pp, stage, donor, entropy=entropy, bars=bars, which=which)  # Step 6 H1
        plasticity(coord, plast, stage, donor, which=which)                          # Step 8 H3
        h2_slope_loss(M, genes, libsize, col, coord, stage, donor, PC, PP,
                      which=which, K=K_SLOPE)                                         # Step 7b H2
        if which == "full":                                                          # Step 7 fallback
            de(M, genes, libsize, coord, stage, donor, set(PC + PP), which=which)
    log(f"\nDone. Outputs in {OUT}")


if __name__ == "__main__":
    main()
