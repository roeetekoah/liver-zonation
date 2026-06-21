#!/usr/bin/env python3
"""Unsupervised-axis agreement check: does the label-free PCA axis agree with the Paper-2
landmark signature coordinate? If yes, the signal is not a signature-formula artefact.

Reads coordinates_learned_unsupervised.csv + coordinates_paper2_landmark.csv (+ validation/ruler
for the unsupervised set). Writes results/tables/unsupervised_axis_eval.csv (one row).
Run:  python src/unsupervised_axis_eval.py
"""
import os, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # src/
import config

T = config.TABLES
HEALTHY = "Healthy control"


def main():
    up = os.path.join(T, "coordinates_learned_unsupervised.csv")   # step4c artifact (flat)
    lp = os.path.join(T, "paper2_landmark", "coordinates.csv")     # battery per-set subdir
    if not (os.path.exists(up) and os.path.exists(lp)):
        print("missing inputs (run step4c + battery first):", up, lp); return
    u = pd.read_csv(up).set_index("cell_id")
    l = pd.read_csv(lp).set_index("cell_id")
    idx = u.index.intersection(l.index)
    u = u.reindex(idx); l = l.reindex(idx)
    axis = u["coord"].values
    coord, pc, pp, stage = l["coord"].values, l["pc"].values, l["pp"].values, l["stage"].values
    h = stage == HEALTHY
    row = {
        "rho_axis_coord": spearmanr(axis, coord).statistic,
        "rho_axis_pc": spearmanr(axis, pc).statistic,
        "rho_axis_pp": spearmanr(axis, pp).statistic,
        "rho_axis_coord_healthy": spearmanr(axis[h], coord[h]).statistic if h.sum() > 3 else np.nan,
        "n_cells": int(len(idx)), "n_healthy": int(h.sum()),
    }
    val = os.path.join(T, "unsupervised", "validation.csv")
    if os.path.exists(val):
        v = pd.read_csv(val)
        row["healthy_marker_correct"] = f"{int(v['pass'].sum())}/{int(v['present'].sum())}"
    rul = os.path.join(T, "unsupervised", "ruler_diagnostics.csv")
    if os.path.exists(rul):
        r = pd.read_csv(rul); hr = r[r["stage"] == HEALTHY]
        if len(hr):
            row["healthy_pc_pp_anticorr"] = float(hr.iloc[0]["pc_pp_anticorr"])
            row["healthy_splithalf_rho_mean"] = float(hr.iloc[0]["splithalf_rho_mean"])
    pd.DataFrame([row]).to_csv(os.path.join(T, "unsupervised_axis_eval.csv"), index=False)
    print("wrote unsupervised_axis_eval.csv")
    for k, val_ in row.items():
        print(f"  {k:28s} {val_}")
    print("\nInterpretation: rho_axis_coord near +1 = the label-free PCA axis agrees with the "
          "Paper-2 signature coordinate -> the zonation signal is not a formula artefact.")


if __name__ == "__main__":
    main()
