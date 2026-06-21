#!/usr/bin/env python3
"""Stage 3 + 4 — summarize the signature battery and auto-select a frozen primary set.

Reads per-set validation/ruler/collapse/H2 tables, writes signature_battery_summary.csv with a
recommended_role per set (chosen ONLY from HEALTHY-ruler metrics, never disease collapse), then
freezes the best healthy ruler if unambiguous (Stage 4).

Run:  python src/summarize_signature_battery.py
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # src/
import config

T = config.TABLES
CAND = config.SIGNATURES / "candidates"
# Explicit signature-set order (the auto-selection competes ONLY among these).
SIGNATURE_SETS = ["paper2_landmark", "core_curated", "expanded_curated",
                  "paper2_top50", "paper2_top100", "paper2_top250", "paper2_full"]
SET_ORDER = list(SIGNATURE_SETS)
if (CAND / "pericentral_selected_frozen.txt").exists():
    SET_ORDER.append("selected_frozen")
# Append any other scored set-dirs (learned coords, unsupervised poles) for a UNIFIED comparison
# table — these are shown for comparison but do NOT compete in the frozen-set auto-selection.
for d in sorted(os.listdir(T)):
    if d not in SET_ORDER and os.path.isdir(os.path.join(T, d)) and \
            os.path.exists(os.path.join(T, d, "validation.csv")):
        SET_ORDER.append(d)


def _read(name):                       # global tables (flat in results/tables/)
    p = os.path.join(T, name)
    return pd.read_csv(p) if os.path.exists(p) else None


def _read_set(s, stem):                # per-set tables (results/tables/<set>/<stem>.csv)
    p = os.path.join(T, s, stem)
    return pd.read_csv(p) if os.path.exists(p) else None


def _count(path):
    return sum(1 for l in open(path) if l.strip()) if os.path.exists(path) else 0


def _n_genes(s):
    """Gene counts for a set: from the candidate files, else (for projection rulers with no
    gene-list) from the learned_signature weights (sign split)."""
    pc = _count(CAND / f"pericentral_{s}.txt"); pp = _count(CAND / f"periportal_{s}.txt")
    if pc == 0 and pp == 0:
        lp = os.path.join(T, f"learned_signature_{s}.csv")
        if os.path.exists(lp):
            d = pd.read_csv(lp)
            num = [c for c in d.columns if d[c].dtype.kind == "f"]
            if num:
                w = d[num[0]].values
                pc = int((w > 0).sum()); pp = int((w < 0).sum())
    return pc, pp


def role_of(r):
    if not r["validation_pass"]:
        return "failed_gate"
    ac, sh = r["healthy_pc_pp_anticorr"], r["healthy_splithalf_rho_mean"]
    if pd.isna(ac) or ac > -0.05:                       # arms not anti-correlated -> not a real ruler
        return "exploratory"
    markers_ok = r["n_validation_correct"] >= r["n_validation_present"] - 1   # allow 1 miss
    if r["n_pc"] >= 20 and r["n_pp"] >= 20 and ac <= -0.2 and (not pd.isna(sh) and sh >= 0.45) and markers_ok:
        return "primary_candidate"
    if r["n_pc"] < 20 or r["n_pp"] < 20:
        return "interpretability_only"
    return "robustness"


def main():
    status = _read("battery_run_status.csv")
    rows = []
    for s in SET_ORDER:
        val = _read_set(s, "validation.csv"); rul = _read_set(s, "ruler_diagnostics.csv")
        col = _read_set(s, "collapse_trends.csv"); h2 = _read_set(s, "h2_slope_loss_summary.csv")
        n_pc, n_pp = _n_genes(s)
        row = {"set_name": s, "n_pc": n_pc, "n_pp": n_pp,
               "validation_pass": False, "n_validation_present": 0, "n_validation_correct": 0,
               "healthy_pc_pp_anticorr": np.nan, "healthy_coord_spread": np.nan,
               "healthy_coord_iqr": np.nan, "healthy_splithalf_rho_mean": np.nan,
               "healthy_coherence_pc": np.nan, "healthy_coherence_pp": np.nan,
               "h1_coord_spread_rho_vs_stage": np.nan, "h1_coord_spread_perm_p": np.nan,
               "h1_coord_iqr_rho_vs_stage": np.nan, "h1_coord_iqr_perm_p": np.nan,
               "h1_pc_pp_anticorr_rho_vs_stage": np.nan, "h1_pc_pp_anticorr_perm_p": np.nan,
               "h2_n_genes_tested": np.nan, "h2_frac_weakening": np.nan,
               "h2_median_trend_rho": np.nan, "status": "not_built", "notes": ""}
        if status is not None and s in set(status["signature_set"]):
            st = status[status["signature_set"] == s].iloc[0]
            row["status"] = ("built" if st.get("built", False) else "not_built")
            row["notes"] = str(st.get("notes", "") or "")
        if val is not None:
            row["n_validation_present"] = int(val["present"].sum())
            row["n_validation_correct"] = int(val["pass"].sum())
            row["validation_pass"] = bool(row["n_validation_present"] >= 4 and
                                          row["n_validation_correct"] >= int(np.ceil(row["n_validation_present"] / 2)))
        if rul is not None:
            h = rul[rul["stage"] == "Healthy control"]
            if len(h):
                h = h.iloc[0]
                row.update(healthy_pc_pp_anticorr=h["pc_pp_anticorr"], healthy_coord_spread=h["coord_spread_std"],
                           healthy_coord_iqr=h["coord_iqr"], healthy_splithalf_rho_mean=h["splithalf_rho_mean"],
                           healthy_coherence_pc=h["coherence_pc"], healthy_coherence_pp=h["coherence_pp"])
        if col is not None:
            c = col.set_index("metric")
            for m, pre in [("coord_spread", "h1_coord_spread"), ("coord_iqr", "h1_coord_iqr"),
                           ("pc_pp_anticorr", "h1_pc_pp_anticorr")]:
                if m in c.index:
                    row[f"{pre}_rho_vs_stage"] = c.loc[m, "rho_vs_stage"]
                    row[f"{pre}_perm_p"] = c.loc[m, "perm_p"]
        if h2 is not None and len(h2):
            row["h2_n_genes_tested"] = int(h2.iloc[0]["n_genes_tested"])
            row["h2_frac_weakening"] = h2.iloc[0]["frac_weakening"]
            row["h2_median_trend_rho"] = h2.iloc[0]["median_trend_rho"]
        row["recommended_role"] = role_of(row)
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(T, "signature_battery_summary.csv"), index=False)
    print("wrote signature_battery_summary.csv")
    print(df[["set_name", "n_pc", "n_pp", "validation_pass", "healthy_pc_pp_anticorr",
              "healthy_splithalf_rho_mean", "recommended_role"]].to_string(index=False))

    # ---------- Stage 4: auto-freeze the best HEALTHY ruler (never by disease) ----------
    # auto-selection competes ONLY among the explicit signature sets (not the frozen copy,
    # not the learned/unsupervised comparison sets)
    cands = df[(df["recommended_role"] == "primary_candidate") &
               (df["set_name"].isin(SIGNATURE_SETS))].copy()
    decision = os.path.join(T, "selected_set_decision.txt")
    if cands.empty:
        with open(decision, "w") as f:
            f.write("AMBIGUOUS — manual review required.\nNo set qualified as primary_candidate on "
                    "healthy-ruler metrics (validation pass + bipolar PC-PP anticorr + split-half + size).\n")
        print("\nNo primary_candidate — wrote AMBIGUOUS decision.")
        return
    # rank by healthy-ruler quality only: all markers correct, then split-half desc, then anticorr asc
    cands["score"] = cands["healthy_splithalf_rho_mean"].fillna(0) - cands["healthy_pc_pp_anticorr"].fillna(0)
    cands = cands.sort_values("score", ascending=False).reset_index(drop=True)
    best = cands.iloc[0]
    ambiguous = len(cands) > 1 and (cands.iloc[0]["score"] - cands.iloc[1]["score"] < 0.02)
    if ambiguous:
        with open(decision, "w") as f:
            f.write("AMBIGUOUS — manual review required.\n"
                    f"Top healthy-ruler candidates near-tied: "
                    f"{cands.iloc[0]['set_name']} vs {cands.iloc[1]['set_name']} "
                    f"(scores {cands.iloc[0]['score']:.3f} vs {cands.iloc[1]['score']:.3f}).\n")
        print(f"\nAMBIGUOUS selection ({best['set_name']} ~ {cands.iloc[1]['set_name']}) — wrote decision, no freeze.")
        return
    sel = best["set_name"]
    for arm in ("pericentral", "periportal"):
        (CAND / f"{arm}_selected_frozen.txt").write_text((CAND / f"{arm}_{sel}.txt").read_text())
    with open(decision, "w") as f:
        f.write(f"SELECTED set: {sel}\n\n")
        f.write("Reason: best HEALTHY-ruler quality among primary candidates.\n")
        f.write("Healthy metrics used (NOT disease collapse):\n")
        f.write(f"  validation: {int(best['n_validation_correct'])}/{int(best['n_validation_present'])} markers correct\n")
        f.write(f"  healthy PC-PP anticorrelation: {best['healthy_pc_pp_anticorr']:+.3f} (want strongly negative)\n")
        f.write(f"  healthy split-half reproducibility: {best['healthy_splithalf_rho_mean']:+.3f}\n")
        f.write(f"  size: {int(best['n_pc'])} PC + {int(best['n_pp'])} PP\n\n")
        f.write("WARNING: selected using Paper 2 / healthy-ruler criteria ONLY, NOT Paper 1 disease "
                "effect (disease is the transfer/test cohort, not the tuning cohort).\n")
    print(f"\nSELECTED (healthy-ruler): {sel} -> wrote selected_frozen files + selected_set_decision.txt")


if __name__ == "__main__":
    main()
