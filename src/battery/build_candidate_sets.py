#!/usr/bin/env python3
"""Stage 1 — build explicit candidate PC/PP gene sets into signatures/candidates/.

AUDITABLE & SELF-CONTAINED: does NOT read config.DEFAULT_SET or config.SETS_TO_COMPARE.
Writes one pericentral_<set>.txt + periportal_<set>.txt per set, plus a build-coverage report.

Sources:
  paper2_landmark : data/raw/Human-liver/Matlab_scripts/Hepatocyte-{PC,PP}-LM.csv (fail loud if missing)
  core/expanded   : hardcoded curated anchors (+ landmark for expanded)
  paper2_top*/full: data/raw/2025-01-01424E-s1/supplementary_table_8.xlsx, sheet 'Hepatocyte'
                    (Gene_Name, qValue, Center_of_Mass, Max_expression; COM<4.5 = pericentral)
"""
import os, sys
import numpy as np, pandas as pd, openpyxl
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # src/
import config

EXPLICIT_SET_ORDER = [
    "paper2_landmark", "core_curated", "expanded_curated",
    "paper2_top50", "paper2_top100", "paper2_top250", "paper2_full",
]
CAND  = config.SIGNATURES / "candidates"
XLSX  = config.DATA_RAW / "2025-01-01424E-s1" / "supplementary_table_8.xlsx"
SHEET = "Hepatocyte"
LMDIR = config.DATA_RAW / "Human-liver" / "Matlab_scripts"
Q_THR, EXPR_THR, COM_MID = 0.05, 1e-4, 4.5   # paper's q<0.05 + max-zonal-expr>1e-4; axis 1..8

CORE_PC = ["GLUL", "CYP2E1", "CYP1A2", "CYP2C8", "CYP27A1", "PCK2", "SLC2A2", "SLCO1B3",
           "CYP3A4", "ALAS1", "AOX1", "GSTA2", "ADH1B"]
CORE_PP = ["ASS1", "ALDOB", "PCK1", "HAL", "SLC38A4", "TAT", "GLS2", "HAMP"]
EXTRA_PC = CORE_PC + ["ADH1A", "ADH4", "AKR1D1", "UGT2B4", "FMO3", "AMACR", "DCXR", "NADK2"]
EXTRA_PP = CORE_PP + ["SERPINA1", "APOA1", "F9", "FABP1", "APOF", "HPX", "TF", "FGA", "FGB", "FGG"]


def load_table():
    wb = openpyxl.load_workbook(XLSX, read_only=True); ws = wb[SHEET]
    hdr = None; rows = []
    for r in ws.iter_rows(values_only=True):
        if hdr is None:
            if r and "qValue" in [str(c) for c in r]:
                hdr = [str(c) for c in r]
                gi, qi = hdr.index("Gene_Name"), hdr.index("qValue")
                ci, mi = hdr.index("Center_of_Mass"), hdr.index("Max_expression")
            continue
        g = r[gi]
        if not g or g == "Gene_Name": continue
        try: rows.append((str(g), float(r[qi]), float(r[ci]), float(r[mi])))
        except Exception: pass
    wb.close(); return rows


def main():
    CAND.mkdir(parents=True, exist_ok=True)
    p1 = set(g.strip() for g in open(config.PAPER1 / "genes.txt") if g.strip())
    report = []

    def record_and_write(name, pc_raw, pp_raw, source, notes, p2set):
        out = {}
        for arm, raw in [("pericentral", pc_raw), ("periportal", pp_raw)]:
            dedup = list(dict.fromkeys(raw))
            miss1 = [g for g in dedup if g not in p1]
            miss2 = [g for g in dedup if p2set is not None and g not in p2set]
            report.append({
                "set_name": name, "arm": arm, "source": source,
                "n_raw": len(raw), "n_after_dedup": len(dedup),
                "n_present_paper1": sum(g in p1 for g in dedup),
                "n_present_paper2": (sum(g in p2set for g in dedup) if p2set is not None else ""),
                "missing_in_paper1": ";".join(miss1[:40]) + (" ..." if len(miss1) > 40 else ""),
                "missing_in_paper2": ";".join(miss2[:40]) + (" ..." if len(miss2) > 40 else ""),
                "notes": notes})
            out[arm] = dedup
        # write full (un-Paper1-filtered) lists; scoring skips genes absent in the data
        (CAND / f"pericentral_{name}.txt").write_text("\n".join(out["pericentral"]) + "\n")
        (CAND / f"periportal_{name}.txt").write_text("\n".join(out["periportal"]) + "\n")
        print(f"  {name:16s} PC={len(out['pericentral'])} PP={len(out['periportal'])}  [{source}]")

    def record_failure(name, source, why):
        for arm in ("pericentral", "periportal"):
            report.append({"set_name": name, "arm": arm, "source": source, "n_raw": 0,
                           "n_after_dedup": 0, "n_present_paper1": 0, "n_present_paper2": "",
                           "missing_in_paper1": "", "missing_in_paper2": "", "notes": f"FAILED: {why}"})
        print(f"  {name:16s} FAILED: {why}")

    # ---- 1. paper2_landmark (fail loud if LM files missing) ----
    pcf, ppf = LMDIR / "Hepatocyte-PC-LM.csv", LMDIR / "Hepatocyte-PP-LM.csv"
    if pcf.exists() and ppf.exists():
        lm_pc = [l.strip() for l in open(pcf) if l.strip()]
        lm_pp = [l.strip() for l in open(ppf) if l.strip()]
        record_and_write("paper2_landmark", lm_pc, lm_pp, "Hepatocyte-{PC,PP}-LM.csv", "", None)
    else:
        lm_pc, lm_pp = [], []
        record_failure("paper2_landmark", "Hepatocyte-{PC,PP}-LM.csv",
                       f"LM files not found; searched {pcf} and {ppf}")
        print(f"  !! paper2_landmark LM files missing — searched {LMDIR}")

    # ---- 2. core_curated ----
    record_and_write("core_curated", CORE_PC, CORE_PP, "hardcoded curated anchors", "", None)

    # ---- 3. expanded_curated = paper2_landmark + extra anchors (dedup) ----
    record_and_write("expanded_curated", lm_pc + EXTRA_PC, lm_pp + EXTRA_PP,
                     "paper2_landmark + curated extras", "", None)

    # ---- 4-7. data-driven from the ranked Paper 2 hepatocyte zonation table ----
    rows = load_table(); p2 = set(g for g, *_ in rows)
    sel = [t for t in rows if t[1] < Q_THR and t[3] >= EXPR_THR]
    pc_ranked = [g for g, q, c, m in sorted([t for t in sel if t[2] < COM_MID], key=lambda t: t[2])]
    pp_ranked = [g for g, q, c, m in sorted([t for t in sel if t[2] > COM_MID], key=lambda t: -t[2])]
    src = f"supplementary_table_8 (q<{Q_THR}, max_expr>={EXPR_THR:g}), ranked by |COM|"
    note = f"qValue available; ranked by Center_of_Mass; expr floor {EXPR_THR:g}"
    for n, name in [(50, "paper2_top50"), (100, "paper2_top100"), (250, "paper2_top250")]:
        record_and_write(name, pc_ranked[:n], pp_ranked[:n], src, note, p2)
    record_and_write("paper2_full", pc_ranked, pp_ranked, src,
                     note + "; all significant zonated genes split by COM sign", p2)

    pd.DataFrame(report).to_csv(config.TABLES / "candidate_set_build_report.csv", index=False)
    print(f"\nwrote {config.TABLES / 'candidate_set_build_report.csv'} ({len(report)} rows)")
    print(f"candidate files in {CAND}")


if __name__ == "__main__":
    main()
