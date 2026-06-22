#!/usr/bin/env python3
"""Orchestrator for the biology deep-dive analysis layer (PLAN.md A/B/C/D).

Runs each analysis module as a subprocess so one failure doesn't abort the rest. Figures land under
results/figures/{h1,h2,confounders,staging}/ and tables under results/tables/analysis/.

Run:  python src/analysis/run_analysis.py [signature_set]      (default expanded_curated)
"""
import os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))

# (module file, human label, PLAN id). Add C* / D* / B1-3 / A3 here as they land.
MODULES = [
    ("a1_scatter.py",        "A1 PC/PP scatter (contact sheet + reps)",  "A1"),
    ("a2_distributions.py",  "A2 per-patient coordinate distributions",  "A2"),
    ("a3_marker_profiles.py","A3 marker zonation profiles",              "A3"),
    ("a4_mechanism.py",      "A4 per-donor mechanism quantification",    "A4"),
    ("b1_heatmap.py",        "B1 gene x cell heatmap (centerpiece)",     "B1"),
    ("b2_zone_boxplots.py",  "B2 zone x program boxplots",               "B2"),
    ("b3_program_vs_coord.py","B3 program-arm expression vs coordinate", "B3"),
    ("b4_set_levels.py",     "B4 per-set expression level vs stage/fib", "B4"),
    ("c_confounders.py",     "C  confounder controls (cell-count, depth, UMI)", "C"),
    ("c3_level_vs_slope.py", "C3 level vs slope per gene",               "C3"),
    ("d_staging.py",         "D  fibrosis / NAS higher-res staging",     "D"),
    ("e_pca_interpretation.py","E  interpret the learned PCA ruler",     "E"),
]


def main(which="expanded_curated"):
    ok, fail = [], []
    for fname, label, pid in MODULES:
        path = os.path.join(HERE, fname)
        if not os.path.exists(path):
            print(f"  [skip] {pid} {label} — {fname} not present yet")
            continue
        print(f"\n===== {pid}: {label} =====")
        r = subprocess.run([sys.executable, path, which], cwd=os.path.dirname(HERE))
        (ok if r.returncode == 0 else fail).append(pid)
    print(f"\nDONE. ok={ok}  failed={fail}")
    print("Figures: results/figures/{h1,h2,confounders,staging}/ ; tables: results/tables/analysis/")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "expanded_curated")
