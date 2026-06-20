#!/usr/bin/env python3
"""Build signatures/{pericentral,periportal}_expanded.txt from Paper 2's ranked
single-nucleus hepatocyte zonation table (Supplementary Table 8, sheet 'Hepatocyte').

Why Table 8 (snRNA) and not Table 2 (Visium): Table 8 is hepatocyte-SPECIFIC and on the
same platform as Paper 1, so it avoids portal-tract stroma (vessels/fibroblasts/immune)
that contaminate the high-zone end of multi-cell Visium spots.

Axis orientation (verified): zone 1 = pericentral, zone 8 = periportal
  (CYP2E1/GLUL have low center-of-mass; ASS1/HAL high).

Output: ~80 most-polarized genes per end (expressed > 55th pct, present in Paper 1),
unioned with the exact Paper 2 landmark genes (the 'core' baseline).

Run:  python src/prep/03_build_expanded_signatures.py
"""
import os, sys, numpy as np, openpyxl
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import config

XLSX = config.DATA_RAW / "2025-01-01424E-s1" / "supplementary_table_8.xlsx"
SHEET = "Hepatocyte"
N_PER_END = 80
EXPR_PCTL = 55

def readlist(p): return [l.strip() for l in open(p) if l.strip()]

def main():
    # expanded = union(exact Paper 2 landmark, curated core, ranked top-N)
    pc_seed = readlist(config.SIGNATURES / "pericentral_paper2_landmark.txt") + readlist(config.SIGNATURES / "pericentral_core.txt")
    pp_seed = readlist(config.SIGNATURES / "periportal_paper2_landmark.txt") + readlist(config.SIGNATURES / "periportal_core.txt")
    pc_core, pp_core = pc_seed, pp_seed   # used below as the union seed
    p1 = set(g.strip() for g in open(config.PAPER1 / "genes.txt") if g.strip())

    wb = openpyxl.load_workbook(XLSX, read_only=True)
    ws = wb[SHEET]; it = ws.iter_rows(min_row=2, values_only=True); next(it)  # skip header
    G, P = [], []
    for r in it:
        g = r[0]
        if not g or g == "Gene_Name": continue
        try: z = [float(r[i]) if r[i] not in (None, "") else 0.0 for i in range(1, 9)]
        except Exception: continue
        G.append(str(g)); P.append(z)
    wb.close()
    G = np.array(G); P = np.array(P); tot = P.sum(1)
    com = np.where(tot > 0, (P * np.arange(1, 9)).sum(1) / np.where(tot > 0, tot, 1), 4.5)

    # orientation sanity (pericentral should have LOWER center-of-mass)
    def C(m):
        i = np.where(G == m)[0]; return com[i[0]] if len(i) else None
    peri_low = (C("CYP2E1") or 9) < (C("ASS1") or 0)

    thr = np.percentile(tot[tot > 0], EXPR_PCTL)
    ok = (tot >= thr) & np.array([g in p1 for g in G])
    order = np.where(ok)[0][np.argsort(com[np.where(ok)[0]])]   # ascending COM
    low = [G[i] for i in order[:N_PER_END]]
    high = [G[i] for i in order[::-1][:N_PER_END]]
    pc_top, pp_top = (low, high) if peri_low else (high, low)

    pc = list(dict.fromkeys(pc_core + pc_top))
    pp = list(dict.fromkeys(pp_core + pp_top))
    (config.SIGNATURES / "pericentral_expanded.txt").write_text("\n".join(pc) + "\n")
    (config.SIGNATURES / "periportal_expanded.txt").write_text("\n".join(pp) + "\n")
    print(f"pericentral_expanded: {len(pc)}  periportal_expanded: {len(pp)}  (orientation peri_low={peri_low})")

if __name__ == "__main__":
    main()
