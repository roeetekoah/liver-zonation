#!/usr/bin/env python3
"""Stage 2 — run the explicit signature-set battery in a FIXED, auditable order.

Does NOT use config.SETS_TO_COMPARE / config.signature_files / filesystem ordering. Reads gene
sets from signatures/candidates/ and runs each through the donor-level battery:
  score -> validate GATE -> ruler diagnostics -> (if pass) H1 collapse, H3 plasticity,
  H2 slope-loss; fallback donor x zone DE only for paper2_full.

SCIENTIFIC RULE: ruler quality is judged on Paper 2 / HEALTHY criteria. Paper 1 disease H1/H2/H3
are TRANSFER results, never used to pick the set. Classifier is NOT trained here (entropy is only
merged if classifier_entropy.csv already exists).

Run:  python src/run_explicit_signature_battery.py [--include-selected]
"""
import os, sys, argparse
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # src/
import config
from steps.common import log, OUT, set_dir
from steps.step2_load_qc import load_qc
from steps.step4_score import score
from steps.step5_validate import validate
from steps.step5b_ruler_diagnostics import ruler_diagnostics
from steps.step6_collapse import collapse
from steps.step7_de import h2_slope_loss, de
from steps.step8_plasticity import plasticity

EXPLICIT_SET_ORDER = [
    "paper2_landmark", "core_curated", "expanded_curated",
    "paper2_top50", "paper2_top100", "paper2_top250", "paper2_full",
]
CAND = config.SIGNATURES / "candidates"
K_SLOPE = 20


def read_set(name):
    pcf, ppf = CAND / f"pericentral_{name}.txt", CAND / f"periportal_{name}.txt"
    if not (pcf.exists() and ppf.exists()):
        return None
    PC = [g.strip() for g in open(pcf) if g.strip()]
    PP = [g.strip() for g in open(ppf) if g.strip()]
    return PC, PP


def _load_entropy():
    p = os.path.join(OUT, "classifier_entropy.csv")
    if not os.path.exists(p): return None
    try:
        log("  (found classifier_entropy.csv — merging AUXILIARY entropy into collapse)")
        return pd.read_csv(p, low_memory=False).set_index("cell_id")["entropy"]
    except Exception:
        return None


def main(include_selected=False):
    M, genes, bars, stage, donor, libsize = load_qc()
    gene_set = set(genes)
    entropy = _load_entropy()

    order = list(EXPLICIT_SET_ORDER)
    if include_selected:
        if (CAND / "pericentral_selected_frozen.txt").exists() and \
           (CAND / "periportal_selected_frozen.txt").exists():
            order.append("selected_frozen")
            log("  --include-selected: appending 'selected_frozen' to the order")
        else:
            log("  --include-selected requested but selected_frozen files absent — skipping it")

    status = []
    for which in order:
        log(f"\n================  SET: {which}  ================")
        s = read_set(which)
        if s is None:
            log(f"  candidate files missing for '{which}' — set NOT built; recording and continuing.")
            status.append({"signature_set": which, "built": False, "validation_pass": "",
                           "downstream_run": False, "n_pc": 0, "n_pp": 0,
                           "notes": "candidate files missing"})
            continue
        PC, PP = s
        n_pc_present = sum(g in gene_set for g in PC); n_pp_present = sum(g in gene_set for g in PP)
        coord, pc, pp, plast, col = score(M, genes, libsize, PC, PP, which=which)
        pd.DataFrame({"signature_set": which, "cell_id": bars, "donor": donor, "stage": stage,
                      "coord": coord, "pc": pc, "pp": pp, "plasticity": plast}
                     ).to_csv(os.path.join(set_dir(which), "coordinates.csv"), index=False)
        rep, passed = validate(coord, col, stage, entropy=entropy, which=which)
        ruler_diagnostics(coord, pc, pp, col, stage, donor, PC, PP, which=which)
        if not passed:
            log(f"  GATE FAILED for '{which}' — H1/H2/H3 downstream SKIPPED.")
            status.append({"signature_set": which, "built": True, "validation_pass": False,
                           "downstream_run": False, "n_pc": n_pc_present, "n_pp": n_pp_present,
                           "notes": "validation gate failed; downstream skipped"})
            continue
        collapse(coord, pc, pp, stage, donor, entropy=entropy, bars=bars, which=which)
        plasticity(coord, plast, stage, donor, which=which)
        if min(n_pc_present, n_pp_present) >= 4:
            h2_slope_loss(M, genes, libsize, col, coord, stage, donor, PC, PP, which=which, K=K_SLOPE)
            h2_note = ""
        else:
            h2_note = "H2 skipped (too few genes for held-out split)"
            log(f"  {h2_note}")
        if which == "paper2_full":
            de(M, genes, libsize, coord, stage, donor, set(PC + PP), which=which)
        status.append({"signature_set": which, "built": True, "validation_pass": True,
                       "downstream_run": True, "n_pc": n_pc_present, "n_pp": n_pp_present,
                       "notes": h2_note})

    pd.DataFrame(status).to_csv(os.path.join(OUT, "battery_run_status.csv"), index=False)
    log(f"\nDone. Per-set tables + battery_run_status.csv in {OUT}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-selected", action="store_true",
                    help="append selected_frozen if its candidate files exist")
    a = ap.parse_args()
    main(include_selected=a.include_selected)
