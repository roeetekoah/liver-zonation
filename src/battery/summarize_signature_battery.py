#!/usr/bin/env python3
"""Stage 3 + 4 — summarize the signature battery and auto-select a frozen primary set.

Reads per-set validation/ruler/collapse/H2 tables, writes signature_battery_summary.csv with a
recommended_role per set (chosen ONLY from HEALTHY-ruler metrics, never disease collapse), then
freezes the best healthy ruler if unambiguous (Stage 4).

Run:  python src/summarize_signature_battery.py
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # src/
import config

T = config.TABLES
CAND = config.SIGNATURES / "candidates"
# Published Paper-2 gene-set rulers (the interpretable family).
SIGNATURE_SETS = ["paper2_landmark", "core_curated", "expanded_curated",
                  "paper2_top50", "paper2_top100", "paper2_top250", "paper2_full"]
# Rulers whose axis is FIT on Paper-1 cells. Their HEALTHY selection metrics (anticorr, split-half)
# are computed on the same Paper-1 healthy cells the axis was fit to -> in-sample / leakage-inflated,
# so they cannot compete head-to-head on healthy quality. They are still valid H1 robustness checks
# (the Paper-1 *disease* cells are never used to fit them), so we keep + show them, just ineligible.
PAPER1_FIT = {"unsupervised", "unsupervised_combined"}
# A ruler may compete for the frozen primary slot iff it was NOT fit on Paper-1 cells (leakage-clean):
# published gene lists fit nothing; Paper-2-trained learned axes (unsupervised_p2, supervised,
# lasso, elasticnet) are external to Paper 1. Eligibility is by leakage, NOT by publishability.
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
        row["leakage_clean"] = row["set_name"] not in PAPER1_FIT     # NOT fit on Paper-1 cells
        rows.append(row)

    df = pd.DataFrame(rows)

    # healthy-ruler quality score (split-half + bipolarity); same metric used everywhere.
    df["healthy_score"] = (df["healthy_splithalf_rho_mean"].fillna(0)
                           - df["healthy_pc_pp_anticorr"].fillna(0))
    # eligible for the frozen primary slot: passes the healthy gate AND is leakage-clean AND is not
    # one of the frozen copies (avoid double-counting selected_frozen, a copy of the chosen set).
    df["eligible_primary"] = ((df["recommended_role"] == "primary_candidate")
                              & df["leakage_clean"] & (df["set_name"] != "selected_frozen"))

    # ---------- Stage 4: freeze TWO co-primary rulers on HEALTHY metrics only (never disease) ----------
    # The frozen primary competes among ALL leakage-clean rulers (publishability is NOT a criterion).
    # We designate two co-primaries so the headline rests on independent construction mechanisms:
    #   A = best leakage-clean PUBLISHED gene-set ruler  (interpretable anchor)
    #   B = best leakage-clean LEARNED axis              (label-free; trained external to Paper 1)
    elig = df[df["eligible_primary"]].sort_values("healthy_score", ascending=False)
    pub = elig[elig["set_name"].isin(SIGNATURE_SETS)]
    learned = elig[~elig["set_name"].isin(SIGNATURE_SETS)]
    co_a = pub.iloc[0]["set_name"] if len(pub) else None              # interpretable
    co_b = learned.iloc[0]["set_name"] if len(learned) else None      # label-free
    overall_best = elig.iloc[0]["set_name"] if len(elig) else None

    # display_role: honest human-facing label (the machine column recommended_role is unchanged).
    def _display_role(r):
        if r["set_name"] == co_a: return "PRIMARY (interpretable)"
        if r["set_name"] == co_b: return "PRIMARY (label-free)"
        if (not r["leakage_clean"]) and r["recommended_role"] in ("primary_candidate", "robustness"):
            return "control (Paper1-fit)"          # passes quality bar but ineligible (in-sample)
        return r["recommended_role"]
    df["display_role"] = df.apply(_display_role, axis=1)
    df.to_csv(os.path.join(T, "signature_battery_summary.csv"), index=False)
    print("wrote signature_battery_summary.csv")
    print(df[["set_name", "n_pc", "n_pp", "validation_pass", "healthy_pc_pp_anticorr",
              "healthy_splithalf_rho_mean", "leakage_clean", "display_role"]].to_string(index=False))

    decision = os.path.join(T, "selected_set_decision.txt")
    if co_a is None and co_b is None:
        with open(decision, "w") as f:
            f.write("AMBIGUOUS — manual review required.\nNo leakage-clean set qualified as "
                    "primary_candidate on healthy-ruler metrics.\n")
        print("\nNo eligible primary — wrote AMBIGUOUS decision.")
        return
    # Freeze the interpretable anchor's gene lists into selected_frozen (downstream H2b/H2c use it).
    if co_a is not None:
        for arm in ("pericentral", "periportal"):
            (CAND / f"{arm}_selected_frozen.txt").write_text((CAND / f"{arm}_{co_a}.txt").read_text())

    def _line(name, kind):
        r = df[df["set_name"] == name].iloc[0]
        return (f"  [{kind}] {name}: score={r['healthy_score']:+.3f}, "
                f"anticorr={r['healthy_pc_pp_anticorr']:+.3f}, "
                f"split-half={r['healthy_splithalf_rho_mean']:+.3f}, "
                f"markers={int(r['n_validation_correct'])}/{int(r['n_validation_present'])}, "
                f"{int(r['n_pc'])} PC + {int(r['n_pp'])} PP\n")
    with open(decision, "w") as f:
        f.write("CO-PRIMARY rulers (frozen on HEALTHY metrics only; eligibility = leakage-clean, "
                "i.e. NOT fit on Paper-1 cells -- publishability is NOT a criterion):\n\n")
        if co_a is not None: f.write(_line(co_a, "interpretable / published anchor"))
        if co_b is not None: f.write(_line(co_b, "label-free / learned, external to Paper 1"))
        f.write(f"\nHighest healthy score among ALL eligible rulers: {overall_best}.\n")
        if co_a and co_b:
            ga = df[df.set_name == co_a].iloc[0]["healthy_score"]
            gb = df[df.set_name == co_b].iloc[0]["healthy_score"]
            f.write(f"Interpretable vs label-free healthy-score gap = {abs(ga - gb):.3f} "
                    f"({'within' if abs(ga - gb) < 0.02 else 'beyond'} the 0.02 tie band) -- reported "
                    "side-by-side; the headline rests on their agreement, not on either alone.\n")
        f.write("\nExcluded from the competition (fit on Paper-1 cells -> in-sample healthy metrics, "
                f"kept as H1 robustness controls): {', '.join(sorted(PAPER1_FIT))}.\n")
        f.write("selected_frozen.txt = copy of the interpretable anchor (for downstream H2b/H2c).\n")
        f.write("WARNING: selection used HEALTHY-atlas criteria ONLY, NOT Paper 1 disease effect "
                "(disease is the transfer/test cohort, not the tuning cohort).\n")
    print(f"\nCO-PRIMARY (healthy-ruler): interpretable={co_a}, label-free={co_b} "
          f"(overall-best eligible={overall_best}) -> wrote selected_frozen + selected_set_decision.txt")


if __name__ == "__main__":
    main()
