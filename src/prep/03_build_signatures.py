#!/usr/bin/env python3
"""Build the data-driven signature sets from Paper 2's hepatocyte zonation table.

Produces:
  signatures/{pericentral,periportal}_full.txt      transcriptome-wide PRIMARY (q<0.05, expressed)
  signatures/{pericentral,periportal}_expanded.txt  landmark + core + top-ranked (mid-size)

Source: data/raw/2025-01-01424E-s1/supplementary_table_8.xlsx, sheet 'Hepatocyte'
        (Paper 2 single-nucleus, hepatocyte-specific zonation; same platform as Paper 1).
        Columns used: Gene_Name, qValue, Center_of_Mass, Max_expression.
Axis orientation (verified): zone 1 = pericentral (low Center_of_Mass), zone 8 = periportal.

The 'core' and 'paper2_landmark' sets are committed by hand and not built here.
Run:  python src/prep/03_build_signatures.py
"""
import os, sys, numpy as np, openpyxl
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import config

XLSX  = config.DATA_RAW / "2025-01-01424E-s1" / "supplementary_table_8.xlsx"
SHEET = "Hepatocyte"
Q_FULL = 0.05          # significance for the full transcriptome-wide program
EXPR_PCTL = 90         # expression floor (Max_expression percentile) to drop snRNA dropout noise
N_EXPANDED = 80        # top-N per side for the mid-size 'expanded' set

def readlist(p): return [l.strip() for l in open(p) if l.strip()]

def load_table():
    wb = openpyxl.load_workbook(XLSX, read_only=True); ws = wb[SHEET]
    hdr = None; rows = []
    for r in ws.iter_rows(min_row=1, values_only=True):
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
    p1 = set(g.strip() for g in open(config.PAPER1 / "genes.txt") if g.strip())
    rows = load_table()
    mx = np.array([t[3] for t in rows]); floor = np.percentile(mx, EXPR_PCTL)

    # ---- FULL: transcriptome-wide program ----
    sel = [t for t in rows if t[1] < Q_FULL and t[3] >= floor and t[0] in p1]
    pc = [g for g, q, c, m in sorted([t for t in sel if t[2] < 4.5], key=lambda t: t[2])]
    pp = [g for g, q, c, m in sorted([t for t in sel if t[2] > 4.5], key=lambda t: -t[2])]
    (config.SIGNATURES / "pericentral_full.txt").write_text("\n".join(pc) + "\n")
    (config.SIGNATURES / "periportal_full.txt").write_text("\n".join(pp) + "\n")
    print(f"full: pericentral {len(pc)} + periportal {len(pp)} = {len(pc)+len(pp)}")

    # ---- EXPANDED: landmark + core + top-ranked ----
    lm_pc = readlist(config.SIGNATURES / "pericentral_paper2_landmark.txt")
    lm_pp = readlist(config.SIGNATURES / "periportal_paper2_landmark.txt")
    co_pc = readlist(config.SIGNATURES / "pericentral_core.txt")
    co_pp = readlist(config.SIGNATURES / "periportal_core.txt")
    exp_pc = list(dict.fromkeys(lm_pc + co_pc + pc[:N_EXPANDED]))
    exp_pp = list(dict.fromkeys(lm_pp + co_pp + pp[:N_EXPANDED]))
    (config.SIGNATURES / "pericentral_expanded.txt").write_text("\n".join(exp_pc) + "\n")
    (config.SIGNATURES / "periportal_expanded.txt").write_text("\n".join(exp_pp) + "\n")
    print(f"expanded: pericentral {len(exp_pc)} + periportal {len(exp_pp)}")

if __name__ == "__main__":
    main()
