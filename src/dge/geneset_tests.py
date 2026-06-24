"""GENE-SET / PATHWAY ENRICHMENT across the biopsy fibrosis axis (F0-F4).

Question this settles
---------------------
Per-gene pseudobulk DGE (src/dge/dge_genomewide.py -> dge_genomewide.csv) found NO single
zonation/detox gene moving with fibrosis (all FDR > 0.79). The deck's standing caveat is:
"a weak COORDINATED program (many genes each shifting a little, same direction) could exist
that per-gene FDR missed." This script runs a competitive gene-set test (GSEA pre-rank) on
the EXISTING ranked gene list to look for exactly that coordinated shift.

Method (self-contained, reuses the already-computed DGE statistics)
-------------------------------------------------------------------
- Ranking metric = signed Spearman rho of log2-CPM vs fibrosis stage F (column `rho_F` in
  dge_genomewide.csv), one value per gene. This is the donor-level (n=38 biopsy donors,
  F0-F4 = 2/8/12/12/4) trend statistic. Positive rho = gene rises with fibrosis; negative =
  falls. Ranking by rho is the standard fgsea/GSEA-prerank input.
- Test = gseapy.prerank (weighted Kolmogorov-Smirnov enrichment score + gene-set permutation,
  10,000 perms). Competitive: asks whether a set's genes cluster at one end of the
  fibrosis-trend ranking more than random sets of the same size. NES = normalised enrichment
  score (sign = direction of coordinated shift), with a permutation p and a BH-FDR.
- Pre-specified sets only (no fishing). Defined below from the project's own anchor files plus
  literature-standard metabolic modules and 3 generic controls. Every gene listed; sources
  documented inline.

Inference unit is the DONOR (the rho came from a donor-level test). Cohort is biopsy-only
(F0-F4); the deceased-donor/explant ends were already excluded upstream in dge_genomewide.py.

Output: results/tables/analysis/geneset_tests.csv
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import gseapy as gp

SIG = config.SIGNATURES
DGE = os.path.join(str(config.ANALYSIS_TABLES), 'dge_genomewide.csv')
OUT = os.path.join(str(config.ANALYSIS_TABLES), 'geneset_tests.csv')


def read_sig(fname):
    with open(os.path.join(str(SIG), fname)) as fh:
        return [l.strip() for l in fh if l.strip() and not l.startswith('#')]


def build_sets():
    """Pre-specified gene sets. Returns dict name -> (gene_list, source_string).
    Zonation anchors come from the project's own signature files (verified by reading them).
    Metabolic modules and controls are literature-standard cores (documented per set)."""
    pc_lm = read_sig('pericentral_paper2_landmark.txt')   # 20 genes, Paper 2 PC landmarks
    pp_lm = read_sig('periportal_paper2_landmark.txt')    # 20 genes, Paper 2 PP landmarks
    plasticity = read_sig('plasticity.txt')               # cholangiocyte/biphenotypic markers

    sets = {
        # --- ZONATION ANCHORS (the preserved-zonation claim) -----------------------------
        'pericentral_anchors': (pc_lm,
            "data/signatures/pericentral_paper2_landmark.txt (Paper 2 hepatocyte PC landmark genes, verbatim)"),
        'periportal_anchors': (pp_lm,
            "data/signatures/periportal_paper2_landmark.txt (Paper 2 hepatocyte PP landmark genes, verbatim)"),
        # --- XENOBIOTIC / DETOX (the detox-dimming sub-story) -----------------------------
        'xenobiotic_CYP': (
            ['CYP2E1','CYP1A2','CYP3A4','CYP3A5','CYP3A43','CYP2C8','CYP2C9','CYP2C19',
             'CYP2B6','CYP1A1','CYP2A6','CYP2D6','CYP4F12'],
            "Cytochrome-P450 xenobiotic family (canonical pericentral detox; HGNC CYP cluster)"),
        'detox_phase2': (
            ['UGT1A1','UGT2B4','UGT2B7','GSTA1','GSTA2','SULT2A1','SULT1A1','AKR1D1','AKR1C1',
             'ADH1A','ADH1B','ADH4','ALDH1L1','FMO3','AOX1','AMACR'],
            "Phase-II conjugation + alcohol/aldehyde detox enzymes (UGT/GST/SULT/ADH/ALDH families)"),
        # --- UREA CYCLE (periportal nitrogen metabolism) ---------------------------------
        'urea_cycle': (
            ['CPS1','OTC','ASS1','ASL','ARG1','NAGS','SLC25A13','GLS2','GLUL'],
            "Urea-cycle + ammonia-disposal enzymes (KEGG hsa00220; GLUL = pericentral glutamine synthetase)"),
        # --- BILE-ACID / LIPID METABOLISM ------------------------------------------------
        'bile_acid_lipid': (
            ['SLCO1B3','SLCO1B1','BAAT','CYP7A1','CYP8B1','CYP27A1','SLC10A1','ABCB11','ABCC2',
             'NR1H4','APOA1','APOA5','APOB','APOC3','FABP1','SREBF1','FASN','MLXIPL','GPAM','PLIN1'],
            "Bile-acid synthesis/transport + lipoprotein/lipogenesis genes (KEGG bile secretion + lipid)"),
        # --- CHOLANGIOCYTE / DUCTULAR (expected to light up if biliary burden bleeds in) -
        'cholangiocyte_ductular': (
            plasticity + ['KRT7','KRT19','KRT23','EPCAM','CFTR','HNF1B','SPP1','ANXA4','DEFB1',
                          'PKHD1','CLDN4','TACSTD2','MMP7'],
            "data/signatures/plasticity.txt (KRT7/KRT19/SOX9/SOX4/KRT23/NCAM1) + canonical cholangiocyte markers"),
        # --- GENERIC CONTROLS (should behave per their known biology) ---------------------
        'CTRL_interferon': (
            ['STAT1','IRF1','ISG15','IFI6','IFI27','IFI44','IFIT1','IFIT3','MX1','MX2','OAS1',
             'OAS2','OAS3','IFITM3','B2M','GBP1','GBP2','RSAD2','XAF1','BST2'],
            "Interferon-response core (MSigDB Hallmark IFN-alpha/gamma overlap)"),
        'CTRL_EMT': (
            ['FN1','VIM','COL1A1','COL1A2','COL3A1','COL5A2','TIMP1','TIMP3','SPARC','TAGLN',
             'ACTA2','BGN','LUM','DCN','THBS1','POSTN','FBN1','MMP2','LOX','TPM1'],
            "Epithelial-mesenchymal-transition / fibrogenic core (MSigDB Hallmark EMT)"),
        'CTRL_ER_stress': (
            ['HSPA5','DDIT3','ATF4','XBP1','HERPUD1','DNAJB9','EDEM1','SEC61B','PDIA4','PDIA6',
             'HYOU1','MANF','CALR','HSP90B1','SDF2L1','DNAJC3','ERN1','ATF6','SEL1L','SYVN1'],
            "Unfolded-protein-response / ER-stress core (MSigDB Hallmark UPR)"),
    }
    return sets


def main():
    dge = pd.read_csv(DGE)
    assert {'gene', 'rho_F', 'p_trend'}.issubset(dge.columns), "dge_genomewide.csv missing gene/rho_F/p_trend"
    n_tested = len(dge)
    dge = dge.dropna(subset=['rho_F', 'p_trend']).drop_duplicates('gene').copy()
    # PRIMARY metric: signed -log10(p_trend). Continuous (rho_F is rounded to 3dp -> many ties,
    # which makes the KS walk order arbitrary); the signed-p score breaks those ties using the
    # actual trend significance while preserving direction (sign of rho). Both metrics reported.
    dge['signed_logp'] = np.sign(dge['rho_F']) * -np.log10(dge['p_trend'].clip(lower=1e-300))
    rnk = dge[['gene', 'signed_logp']].rename(columns={'signed_logp': 'score'})
    rnk = rnk.sort_values('score', ascending=False).reset_index(drop=True)
    rnk_rho = dge[['gene', 'rho_F']].sort_values('rho_F', ascending=False).reset_index(drop=True)
    print(f"ranked list: {len(rnk)} genes (of {n_tested} DGE-tested)")
    print("  PRIMARY metric = signed -log10(p_trend) (continuous); robustness = signed Spearman rho")

    sets = build_sets()
    # restrict each set to genes actually in the ranked (tested) universe; record coverage
    universe = set(rnk['gene'])
    gmt = {}
    coverage = {}
    sources = {}
    for name, (genes, src) in sets.items():
        present = sorted(set(genes) & universe)
        gmt[name] = present
        coverage[name] = (len(present), len(set(genes)))
        sources[name] = src

    def run_prerank(ranklist):
        pre = gp.prerank(
            rnk=ranklist, gene_sets=gmt, permutation_num=10000, min_size=3,
            max_size=2000, seed=0, no_plot=True, outdir=None, threads=4,
        )
        r = pre.res2d.copy(); r.columns = [c.strip() for c in r.columns]
        return r.set_index('Term')[['NES', 'NOM p-val', 'FDR q-val']].astype(
            {'NES': float}).rename(columns={'NOM p-val': 'p', 'FDR q-val': 'fdr'})

    # PRIMARY (signed-logp) + ROBUSTNESS (rho) runs
    res = None
    res_primary = run_prerank(rnk)
    res_rho = run_prerank(rnk_rho)
    # back-compat: keep res for the row-building loop below (use primary)
    res = res_primary.reset_index().rename(
        columns={'NES': 'NES', 'p': 'NOM p-val', 'fdr': 'FDR q-val'})
    res.columns = ['Term', 'NES', 'NOM p-val', 'FDR q-val']
    res2 = res.copy()
    # normalise column names across gseapy versions
    term_col = 'Term'
    nes_col = 'NES'; p_col = 'NOM p-val'; fdr_col = 'FDR q-val'
    # build tidy output
    rows = []
    for _, r in res.iterrows():
        name = r[term_col]
        nes = float(r[nes_col])
        try: p = float(r[p_col])
        except Exception: p = np.nan
        try: fdr = float(r[fdr_col])
        except Exception: fdr = np.nan
        npres, ntot = coverage.get(name, (np.nan, np.nan))
        direction = ('up_with_fibrosis' if nes > 0 else 'down_with_fibrosis') if abs(nes) > 0 else 'flat'
        # robustness (rho-ranked) values
        rr = res_rho.loc[name] if name in res_rho.index else None
        rows.append(dict(gene_set=name, n_genes_in_set=ntot, n_genes_tested=npres,
                         NES=round(nes, 3), p_perm=p, FDR=fdr, direction=direction,
                         NES_rho=round(float(rr['NES']), 3) if rr is not None else np.nan,
                         p_rho=float(rr['p']) if rr is not None else np.nan,
                         FDR_rho=float(rr['fdr']) if rr is not None else np.nan,
                         source=sources.get(name, '')))
    out = pd.DataFrame(rows).sort_values('p_perm').reset_index(drop=True)
    out.to_csv(OUT, index=False)

    pd.set_option('display.width', 200, 'display.max_columns', 20)
    print("\n=== GENE-SET ENRICHMENT vs fibrosis (donor-level, biopsy F0-F4) ===")
    print(out[['gene_set', 'n_genes_in_set', 'n_genes_tested', 'NES', 'p_perm', 'FDR', 'direction']].to_string(index=False))
    sig = out[(out.FDR < 0.05)]
    print(f"\nsets passing FDR < 0.05: {len(sig)}")
    if len(sig):
        print(sig[['gene_set', 'NES', 'p_perm', 'FDR', 'direction']].to_string(index=False))
    print(f"\nwrote {OUT}")


if __name__ == '__main__':
    main()
