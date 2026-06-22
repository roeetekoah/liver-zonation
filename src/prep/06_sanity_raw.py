"""SANITY CHECKS for the raw-count extraction (raw_panel_counts.csv from prep/05).
Each check is an explicit, falsifiable assertion that the data we pulled means what we think it means:
RAW RNA-assay UMI counts (NOT the SCT-corrected assay). Run: python src/prep/06_sanity_raw.py
"""
import os, sys
import numpy as np, pandas as pd, scipy.sparse as sp
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
P1=str(config.PAPER1)
ok=lambda b: "PASS" if b else "**FAIL**"

def main():
    df=pd.read_csv(os.path.join(P1,'raw_panel_counts.csv'),low_memory=False)
    genes=[c for c in df.columns if c not in ('cell_id','donor','stage','lobe','annotation','E_raw','nCount_RNA_md')]
    G=df[genes].values
    print(f"rows(cells): {len(df):,}   panel genes: {len(genes)}")
    print("\n=== Sanity checks (each should PASS) ===")

    # 1. counts are non-negative INTEGERS (raw UMIs); SCT 'data'/'scale.data' would be non-integer
    integer = np.allclose(G, np.round(G)) and (G.min()>=0)
    print(f"[1] panel values are non-negative integers (raw UMIs)            : {ok(integer)}  (min={G.min()}, max={G.max():.0f})")

    # 2. E_raw == recorded nCount_RNA (the authors' RAW RNA library size) exactly
    e_eq = np.array_equal(df['E_raw'].values, df['nCount_RNA_md'].values)
    print(f"[2] E_raw == metadata nCount_RNA exactly (= raw RNA library)     : {ok(e_eq)}")

    # 3. library size spans the RAW range (~900..50k), NOT the squeezed SCT band (~3-5.7k)
    lo,hi=df['E_raw'].min(),df['E_raw'].max()
    raw_band = (lo<1500) and (hi>20000)
    print(f"[3] library size spans raw range, not the SCT ~3-5.7k band       : {ok(raw_band)}  (E_raw {lo:.0f}..{hi:.0f})")

    # 4. these are NOT the SCT matrix: compare panel gene values to counts.npz (SCT) for shared cells
    M=sp.load_npz(os.path.join(P1,'counts.npz')).tocsr()
    allg=np.array([g.strip() for g in open(os.path.join(P1,'genes.txt'))])
    bars=np.array([b.strip() for b in open(os.path.join(P1,'barcodes.txt'))])
    g2i={g:i for i,g in enumerate(allg)}; b2i={b:i for i,b in enumerate(bars)}
    hep=df[df['annotation']=='Hepatocytes']
    test_cells=hep['cell_id'].values[:200]; test_genes=[g for g in ['CYP2E1','ALB','GLUL','PCK1'] if g in g2i]
    diffs=0; comps=0
    for c in test_cells:
        if c not in b2i: continue
        for g in test_genes:
            raw=hep.loc[hep.cell_id==c,g].values[0]; sct=M[g2i[g],b2i[c]]
            comps+=1; diffs+= (raw!=sct)
    not_sct = diffs>0
    print(f"[4] RNA-panel counts DIFFER from the SCT counts.npz (not SCT)    : {ok(not_sct)}  ({diffs}/{comps} of compared (cell,gene) differ)")
    # and E_raw != SCT library
    sct_tot=np.asarray(M.sum(0)).ravel()
    sct_e=pd.Series(sct_tot,index=bars)
    shared=[c for c in hep['cell_id'].values[:2000] if c in b2i]
    e_raw=hep.set_index('cell_id').loc[shared,'E_raw']; e_sct=sct_e.loc[shared]
    print(f"    E_raw(RNA) median={e_raw.median():.0f}  vs  SCT colsum median={e_sct.median():.0f}  (should differ; RNA>SCT)")

    # 5. biology check: ALB (albumin) dominates the hepatocyte transcriptome (highest-burden gene)
    burden={g: 1e4*hep[g].sum()/hep['E_raw'].sum() for g in genes}
    top=sorted(burden.items(),key=lambda x:-x[1])[:4]
    alb_top = ('ALB' in [g for g,_ in top[:2]])
    print(f"[5] ALB is among the top-burden hepatocyte genes (sanity)        : {ok(alb_top)}  top: " + ", ".join(f"{g}={v:.0f}/10k" for g,v in top))

    # 6. panel-gene sum per cell <= E_raw (panel is a subset of the transcriptome)
    panel_le = (hep[genes].sum(axis=1).values <= hep['E_raw'].values + 1e-6).all()
    print(f"[6] per-cell panel-gene sum <= E_raw (panel is a subset)         : {ok(panel_le)}")

    # 7. hepatocyte count matches the paper (~69,426)
    nhep=len(hep)
    print(f"[7] hepatocyte nuclei == paper's 69,426                          : {ok(nhep==69426)}  (n={nhep:,})")

    # 8. detection rates are plausible (housekeeping high, sparse genes low) — not all-or-nothing
    det={g:(hep[g]>0).mean() for g in ['ALB','CYP2E1','GLUL','LGR5']}
    plausible = det['ALB']>0.8 and det['GLUL']<0.5
    print(f"[8] detection plausible (ALB high, GLUL/LGR5 sparse)             : {ok(plausible)}  ALB={det['ALB']:.2f} CYP2E1={det['CYP2E1']:.2f} GLUL={det['GLUL']:.2f} LGR5={det['LGR5']:.2f}")

    # 9. no SILENT gene drop: all analysis-critical genes present; RPLP0 is the only expected absence
    #    (Paper 1 QC removed mitochondrial + ribosomal protein-coding genes; RPLP0 is ribosomal).
    critical=['GLUL','CYP3A4','CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3','ASS1','CPS1','PCK1','HAL','ALDOB','ARG1',
              'FOS','JUN','HSPA1A','VEGFA','KRT19','EPCAM','SOX4','ALB','ACTB','GAPDH','B2M']
    miss=[g for g in critical if g not in genes]
    print(f"[9] all analysis-critical genes present (no silent drop)         : {ok(not miss)}  "
          f"(n_panel={len(genes)}; missing critical: {miss or 'none'}; RPLP0 expected-absent: ribosomal, removed by Paper-1 QC)")

    print("\nAll PASS => the extracted panel is the RAW RNA-assay UMI counts (not SCT/data/scale.data).")

if __name__=='__main__': main()
