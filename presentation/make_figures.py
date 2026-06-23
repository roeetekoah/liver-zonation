"""
Generate all figures for the 8-minute deck from REAL data tables (donor-level where possible).
Outputs PNGs to reports/deck/assets/. Color scheme per the deck spec.
Run from repo root: python reports/deck/make_figures.py
"""
import os, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

T   = "results/tables/analysis"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"); os.makedirs(OUT, exist_ok=True)

# ---- palette: data = meaning colors; chrome aligned to the deck (cream / teal / ink) ----
PC="#1D4ED8"; PP="#E0701C"; DUAL="#7C5CD8"; NULL="#A8A29E"
BIOPSY="#1B6E78"; CONFOUND="#B0413C"; ENDSTAGE="#8A2C6B"; STRESS="#C0392B"; BILIARY="#7C5CD8"
INK="#1B2B31"; MUTE="#5C6E73"; GRID="#E8E2D6"; EDGE="#CFC8BA"
plt.rcParams.update({
    "font.family":"sans-serif", "font.sans-serif":["Arial","Helvetica","Liberation Sans","DejaVu Sans"],
    "font.size":14, "axes.titlesize":16, "axes.titleweight":"bold", "axes.titlecolor":INK, "axes.titlelocation":"left",
    "axes.titlepad":12, "axes.labelsize":13, "axes.labelcolor":MUTE, "axes.labelpad":7,
    "axes.edgecolor":EDGE, "axes.linewidth":1.0,
    "xtick.color":MUTE, "ytick.color":MUTE, "xtick.labelsize":13, "ytick.labelsize":12,
    "xtick.major.size":0, "ytick.major.size":0, "xtick.major.pad":8, "ytick.major.pad":5,
    "axes.spines.top":False, "axes.spines.right":False,
    "axes.grid":True, "axes.grid.axis":"y", "axes.axisbelow":True, "grid.color":"#EBE5D8", "grid.linewidth":1.0,
    "figure.dpi":300, "savefig.dpi":300,
    "figure.facecolor":"none", "axes.facecolor":"none", "savefig.transparent":True,
    "legend.frameon":False, "legend.fontsize":12.5, "legend.handlelength":1.3, "legend.handletextpad":0.5})
STAGES=["F0","F1","F2","F3","F4"]
from matplotlib.lines import Line2D

def clean(ax):   # consistent minimalist axes: light spines, no ticks, soft y-grid only
    for sp in ("left","bottom"): ax.spines[sp].set_color(EDGE); ax.spines[sp].set_linewidth(1.0)
    ax.tick_params(length=0); ax.grid(axis="y", color="#EBE5D8", lw=1.0); ax.grid(axis="x", visible=False)
    ax.set_axisbelow(True)
def donor_legend(ax, color, loc="upper left"):
    ax.legend(handles=[Line2D([0],[0],marker="o",ls="",mfc=color,mec="none",ms=8,alpha=0.55,label="donor"),
                       Line2D([0],[0],color=color,lw=3,label="median")], loc=loc, fontsize=11.5)

def jitter(n, w=0.13): return (np.random.RandomState(0).rand(n)-0.5)*2*w

lb = pd.read_csv(f"{T}/load_bearing_donor_table.csv")
lb["Fs"]="F"+lb["F"].astype(int).astype(str)
for c in ["PC","PP","dual2","null"]: lb[c+"_f"]=lb[c+"_n"]/lb["N_thin"]
lb["pppc"]=lb["PP_n"]/lb["PC_n"].replace(0,np.nan)
bio = lb[lb.source=="biopsy"].copy()

# ===================== FIG 1 — stress by source + cross-lineage =====================
sd = pd.read_csv("findings/stress_and_panel_by_stage/stress_per_donor_alllobe.csv")
SG=["FOS","JUN","JUNB","JUND","ATF3","DUSP1","HSPA1A","HSPA1B"]
mod = (sd[sd.gene.isin(SG)].groupby(["donor","source"])["dm_mean"].sum().reset_index())
order=["needle_biopsy","healthy(deceased-donor)","explant"]; labels=["Needle biopsy\n(F0–F4)","Healthy\ndeceased-donor","End-stage\nexplant"]
cols=[BIOPSY,CONFOUND,ENDSTAGE]
fig,(ax,ax2)=plt.subplots(1,2,figsize=(11.6,5.5),gridspec_kw={"width_ratios":[1.2,1.85]})
means=[]
for i,s in enumerate(order):
    v=mod[mod.source==s]["dm_mean"].values; means.append(v.mean())
    ax.scatter(np.full(len(v),i)+jitter(len(v)), v, s=70, color=cols[i],
               edgecolor="white", linewidth=0.8, zorder=3, alpha=0.9)
    ax.plot([i-0.25,i+0.25],[v.mean()]*2, color=cols[i], lw=3, zorder=4)
ax.set_xticks(range(3)); ax.set_xticklabels(labels)
ax.set_ylabel("Stress module  (mean UMIs / nucleus,\ndown-thinned to 1,500)")
ax.set_title("Procurement stress by tissue source", fontweight="bold", loc="left")
ax.annotate(f"{means[1]/means[0]:.1f}×", (1, means[1]), xytext=(1.15,means[1]+0.15), color=CONFOUND, fontweight="bold")
ax.annotate(f"{means[2]/means[0]:.0f}× biopsy", (2, means[2]), xytext=(1.55,means[2]-0.15), color=ENDSTAGE, fontweight="bold")
ax.text(0.02,0.96,"donor = point", transform=ax.transAxes, fontsize=11, color=MUTE, va="top")
# cross-lineage IEG stress: ALL 6 lineages, biopsy vs end-stage (F5)
bl=pd.read_csv("findings/stress_celltype_segmented/by_lineage.csv")
ig=bl[bl.program=="IEG"].pivot_table(index="cell_type",columns="source",values="dm_mean")
ig["fold"]=ig["explant"]/ig["biopsy"]; ig=ig.sort_values("fold",ascending=False)
short={"Hepatocytes":"Hepatocyte","Endothelial":"Endothelial","Stellate":"Stellate","Cholangiocytes":"Cholangiocyte","Macrophages":"Macrophage","Lymphocytes":"Lymphocyte"}
names=[short.get(c,c) for c in ig.index]; xx=np.arange(len(ig)); w=0.38
ax2.bar(xx-w/2, ig["biopsy"], w, color=BIOPSY, label="biopsy")
ax2.bar(xx+w/2, ig["explant"], w, color=ENDSTAGE, label="end-stage")
for i,(c,row) in enumerate(ig.iterrows()):
    ax2.text(i+w/2, row["explant"]+0.03, f"{row['fold']:.0f}×", ha="center", fontsize=11, fontweight="bold", color=ENDSTAGE)
ax2.set_xticks(xx); ax2.set_xticklabels(names, fontsize=10.5, rotation=20, ha="right")
ax2.set_ylabel("Immediate-early stress\n(mean UMIs / nucleus)")
ax2.set_title("Elevated in EVERY lineage at end-stage (3–18×) — organ-wide, not zonation-specific",
              fontweight="bold", loc="left", fontsize=12)
ax2.legend(frameon=False, fontsize=11, loc="upper right")
ax2.text(0.5,-0.42,"hepatocyte 18× ≈ endothelial 18× (a non-zonated lineage)   ·   finding F5",
         transform=ax2.transAxes, ha="center", fontsize=10, color=MUTE)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_stress.png", bbox_inches="tight"); plt.close(fig)

# ===================== FIG 2 — anchor 2x2 (biopsy F0-F4) =====================
def panel(ax, col, color, title, pct=True, ratio=False):
    top=0
    for i,st in enumerate(STAGES):
        v=bio[bio.Fs==st][col].values
        if pct and not ratio: v=v*100
        top=max(top,v.max())
        ax.scatter(np.full(len(v),i)+jitter(len(v)), v, s=40, color=color, alpha=0.4, edgecolor="none", zorder=3)
        med=np.median(v); ax.plot([i-0.3,i+0.3],[med]*2,color=color,lw=3,solid_capstyle="round",zorder=4)
        lbl=f"{med:.0f}" if (pct and not ratio) else f"{med:.2f}"
        ax.annotate(lbl,(i,med),xytext=(0,7),textcoords="offset points",ha="center",va="bottom",
                    fontsize=10.5,fontweight="bold",color=color,zorder=6)
    ax.set_xticks(range(5)); ax.set_xticklabels(STAGES); ax.set_xlim(-0.6,4.6); ax.set_ylim(0,top*1.18)
    ax.set_title(title, loc="left", fontsize=14.5); clean(ax)
fig,axes=plt.subplots(2,2,figsize=(11.5,7.4))
panel(axes[0,0],"PC_f",PC,"No pericentral depletion"); axes[0,0].set_ylabel("PC-anchor %")
panel(axes[0,1],"dual2_f",DUAL,"Co-expression stays rare"); axes[0,1].set_ylabel("Dual (≥2 UMI) %")
axes[0,1].axhline(2.9, color=CONFOUND, ls="--", lw=1.5)
axes[0,1].text(4.0,2.9,"confounded explants ≈2.9%  (~7×)", color=CONFOUND, fontsize=10, va="bottom", ha="right")
panel(axes[1,0],"null_f",NULL,"No zonal turn-off"); axes[1,0].set_ylabel("Null %")
panel(axes[1,1],"pppc","#B45309","No composition shift", ratio=True); axes[1,1].set_ylabel("PP : PC ratio")
fig.suptitle("Across biopsy F0–F4, no large de-zonation route appears   ·   donor = point, line = median",
             fontsize=13, color=MUTE, x=0.5, y=1.005)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_anchor2x2.png", bbox_inches="tight"); plt.close(fig)

# ---- two-panel headline result (PC-anchor + dual, enlarged) ----
fig,(a1,a2)=plt.subplots(1,2,figsize=(11,5.2))
def bigpanel(ax,col,color,title,ylab):
    for i,st in enumerate(STAGES):
        v=bio[bio.Fs==st][col].values*100
        ax.scatter(np.full(len(v),i)+jitter(len(v),0.12), v, s=85, color=color, alpha=0.55,
                   edgecolor="white", linewidth=0.8, zorder=3)
        ax.plot([i-0.3,i+0.3],[np.median(v)]*2,color=color,lw=4,zorder=4)
    ax.set_xticks(range(5)); ax.set_xticklabels(STAGES, fontsize=15)
    ax.set_title(title, fontweight="bold", loc="left", fontsize=17); ax.set_ylabel(ylab, fontsize=15)
    ax.grid(axis="y", color=GRID); ax.set_axisbelow(True)
bigpanel(a1,"PC_f",PC,"No pericentral depletion","PC-anchor % of hepatocyte nuclei")
bigpanel(a2,"dual2_f",DUAL,"Co-expression stays rare","Dual (≥2 UMI) %")
a2.axhline(2.9, color=CONFOUND, ls="--", lw=2)
a2.text(4.05,2.95,"confounded explants ≈ 2.9%  (~7×)", color=CONFOUND, fontsize=12, va="bottom", ha="right", fontweight="bold")
a1.text(0.02,0.97,"donor = point, line = median", transform=a1.transAxes, fontsize=12, color=MUTE, va="top")
fig.tight_layout(); fig.savefig(f"{OUT}/fig_result2.png", bbox_inches="tight"); plt.close(fig)

# ---- headline result v3: PC depletion + PP depletion + dual, F1-F4 (F0 n=2 dropped), value-labelled ----
SR=["F1","F2","F3","F4"]
fig,axs=plt.subplots(1,3,figsize=(12.4,5.7))
def rpanel(ax,col,color,title,ylab,explant_line=None,dec=0,legend=False):
    top=0
    for i,st in enumerate(SR):
        v=bio[bio.Fs==st][col].values*100; top=max(top,v.max())
        ax.scatter(np.full(len(v),i)+jitter(len(v),0.13), v, s=46, color=color, alpha=0.4,
                   edgecolor="none", zorder=3)
        med=np.median(v); ax.plot([i-0.34,i+0.34],[med]*2,color=color,lw=3.2,solid_capstyle="round",zorder=4)
        ax.annotate(f"{med:.{dec}f}%",(i,med),xytext=(0,8),textcoords="offset points",
                    ha="center",va="bottom",fontsize=12,fontweight="bold",color=color,zorder=6)
    ax.set_xticks(range(4)); ax.set_xticklabels(SR)
    ax.set_xlim(-0.6,3.6); ax.set_ylim(0, top*1.15)
    ax.set_title(title, loc="left"); ax.set_ylabel(ylab)
    clean(ax)
    if explant_line is not None:
        ax.axhline(explant_line, color=CONFOUND, ls=(0,(4,3)), lw=1.6)
        ax.text(3.45,explant_line,"  explants ≈ 2.9% (~7×)",color=CONFOUND,fontsize=11,va="center",ha="right",fontweight="bold")
    if legend: donor_legend(ax,color,"upper left")
rpanel(axs[0],"PC_f",PC,"No pericentral depletion","PC-anchor %", legend=True)
rpanel(axs[1],"PP_f",PP,"No periportal depletion","PP-anchor %")
rpanel(axs[2],"dual2_f",DUAL,"Co-expression stays rare","Dual (≥2 UMI) %",explant_line=2.9,dec=1)
fig.suptitle("Matched biopsy fibrosis F1–F4   ·   each point = one donor   (F0 n=2 omitted; full F0–F4 in backup)",
             fontsize=12.5, color=MUTE, x=0.5, y=1.005, ha="center")
fig.tight_layout(rect=(0,0,1,0.97)); fig.savefig(f"{OUT}/fig_result3.png", bbox_inches="tight", pad_inches=0.15); plt.close(fig)

# ===================== FIG 3 — TOST equivalence (F4 vs F1 PC-anchor) =====================
eq=pd.read_csv(f"{T}/equivalence_bound.csv")
r=eq[(eq.contrast=="F1vF4")&(eq.metric=="PC_anchor_fraction")].iloc[0]
est,lo,hi=r["diff"],r["t_ci90_lo"],r["t_ci90_hi"]
ri=eq[(eq.contrast=="F1vF3")&(eq.metric=="PC_anchor_fraction")].iloc[0]
fig,ax=plt.subplots(figsize=(8.4,4.2))
ax.axvspan(-0.5,-0.20, color=CONFOUND, alpha=0.07); ax.axvspan(0.20,0.5, color=CONFOUND, alpha=0.07)
ax.axvspan(-0.10,0.10, color=BIOPSY, alpha=0.08)
ax.axvline(0, color="#94A3B8", lw=1)
ax.errorbar([est],[1], xerr=[[est-lo],[hi-est]], fmt="o", color=PC, ms=13, lw=2.5, capsize=6, zorder=5)
ax.errorbar([ri['diff']],[0.45], xerr=[[ri['diff']-ri['t_ci90_lo']],[ri['t_ci90_hi']-ri['diff']]],
            fmt="s", color="#0EA5E9", ms=10, lw=2, capsize=5, zorder=5)
ax.text(est,1.16,f"F4 vs F1:  +{est*100:.1f} pp", ha="center", color=PC, fontweight="bold")
ax.text(ri['diff'],0.62,f"F1→F3 interior", ha="center", color="#0369A1", fontsize=11)
ax.text(0.30,1.0,"large shift\n(~20 pp) excluded", color=CONFOUND, fontsize=11, va="center")
ax.text(0,0.05,"subtle drift ≤10 pp not excluded", color=BIOPSY, ha="center", fontsize=11)
ax.set_yticks([]); ax.set_ylim(-0.1,1.45); ax.set_xlim(-0.5,0.5)
ax.set_xlabel("Change in pericentral-anchor fraction  (90% CI)")
ax.set_title("We exclude a large shift, not subtle drift", fontweight="bold", loc="left")
ax.set_xticks([-0.4,-0.2,0,0.2,0.4]); ax.set_xticklabels(["−40 pp","−20 pp","0","+20 pp","+40 pp"])
fig.tight_layout(); fig.savefig(f"{OUT}/fig_tost.png", bbox_inches="tight"); plt.close(fig)

# ===================== FIG 4 — volcano (edgeR F4 vs F1) =====================
d=pd.read_csv(f"{T}/dge_planA_F4vsF1.csv"); d=d.rename(columns={d.columns[0]:"gene"})
d["nl"]=-np.log10(d["FDR"].clip(lower=1e-12))
BIL=["EPCAM","GRHL2","SPINT2","SOX4","SOX9","B3GNT3"]; ZON=["GLUL","CYP3A4","CYP2E1","ASS1","CPS1","ALDOB"]
fig,ax=plt.subplots(figsize=(9.2,6))
ns=d[d.FDR>=0.05]; ax.scatter(ns.logFC, ns.nl, s=9, color="#CBD5E1", alpha=0.6, zorder=1)
sig=d[(d.FDR<0.05)&(~d.gene.isin(BIL+["CXCL10"]))]; ax.scatter(sig.logFC,sig.nl,s=16,color="#475569",alpha=0.7,zorder=2)
for g in BIL:
    row=d[d.gene==g]
    if len(row): ax.scatter(row.logFC,row.nl,s=80,color=BILIARY,edgecolor="white",lw=0.8,zorder=4)
cx=d[d.gene=="CXCL10"]; ax.scatter(cx.logFC,cx.nl,s=90,color=STRESS,edgecolor="white",lw=0.8,zorder=4,marker="D")
for g in ZON:
    row=d[d.gene==g]
    if len(row):
        c=PC if g in ["GLUL","CYP3A4","CYP2E1"] else PP
        ax.scatter(row.logFC,row.nl,s=70,color=c,edgecolor="white",lw=0.8,zorder=3)
ax.axhline(-np.log10(0.05), color="#94A3B8", ls="--", lw=1.2); ax.text(ax.get_xlim()[0]+0.2,-np.log10(0.05)+0.05,"FDR = 0.05",fontsize=10,color=MUTE)
# labels
import numpy as _np
for g,dx,dy in [("EPCAM",.3,.2),("GRHL2",.3,.0),("SPINT2",.3,.1),("SOX4",-.2,.4),("SOX9",.3,-.1),("B3GNT3",.3,.0),("CXCL10",.3,.2),("GLUL",-1.1,.3),("CYP3A4",-1.2,.0),("ASS1",-1.0,.2)]:
    row=d[d.gene==g]
    if len(row):
        c=BILIARY if g in BIL else (STRESS if g=="CXCL10" else (PC if g in ["GLUL","CYP3A4"] else PP))
        ax.annotate(g,(row.logFC.values[0],row.nl.values[0]),xytext=(row.logFC.values[0]+dx,row.nl.values[0]+dy),
                    fontsize=11,color=c,fontweight="bold")
ax.set_xlabel("log2 fold-change  (cirrhotic F4 vs F1)"); ax.set_ylabel("−log10 FDR")
ax.text(0.02,0.97,"purple = biliary/ductular\nblue/orange = zonation (flat)\nred = CXCL10 (inflammation)\n64 genes FDR<0.05",
        transform=ax.transAxes, ha="left", va="top", fontsize=11, color=MUTE)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_volcano.png", bbox_inches="tight"); plt.close(fig)

# ===================== FIG 5 — compositional (3 panels) =====================
comp=pd.read_csv(f"{T}/dge_planA_compositional.csv")
fig,(a,b,c)=plt.subplots(1,3,figsize=(12.6,5.4))
# A lollipop chol/hep fold
g6=["GRHL2","EPCAM","B3GNT3","SOX9","SPINT2","SOX4"]
sub=comp[comp.gene.isin(g6)].set_index("gene").loc[g6]
y=range(len(g6))
a.hlines(list(y), 0, sub["nonhep_over_hep"], color=BILIARY, lw=2)
a.scatter(sub["nonhep_over_hep"], list(y), color=BILIARY, s=90, zorder=3)
for i,(gn,val) in enumerate(zip(g6,sub["nonhep_over_hep"])): a.text(val+2,i,f"{val:.0f}×",va="center",fontsize=11,color=BILIARY,fontweight="bold")
a.set_yticks(list(y)); a.set_yticklabels(g6); a.set_xlabel("cholangiocyte / hepatocyte\nabundance fold")
a.set_title("A · Biliary genes are\ncholangiocyte genes", fontweight="bold", loc="left", fontsize=13)
a.invert_yaxis(); a.grid(axis="x", color=GRID); a.set_axisbelow(True)
# B decontX funnel
b.bar([0,1],[64,34], color=[BILIARY,"#A78BFA"], width=0.55)
for i,v in enumerate([64,34]): b.text(i,v+1,str(v),ha="center",fontweight="bold",fontsize=14)
b.set_xticks([0,1]); b.set_xticklabels(["before\ndecontX","after\ndecontX"]); b.set_ylabel("genes FDR<0.05")
b.set_title("B · Ambient removal\nhalves the hits", fontweight="bold", loc="left", fontsize=13)
b.text(0.5,-0.30,"SOX4/SOX9 drop below significance;\nEPCAM/B3GNT3/SPINT2/CXCL10 survive", transform=b.transAxes,
       ha="center", fontsize=10, color=MUTE)
# C cholangiocyte fraction by stage (computed from metadata) + co-expression callout
try:
    md=pd.read_csv("data/processed/paper1/metadata_all_cells.csv", usecols=["Patient.ID","cell.annotation"], low_memory=False)
    md["donor"]=md["Patient.ID"].astype(str)
    fmap=lb.set_index(lb.donor.astype(str))["F"].to_dict(); smap=lb.set_index(lb.donor.astype(str))["source"].to_dict()
    md["F"]=md.donor.map(fmap); md["src"]=md.donor.map(smap)
    md=md[(md.src=="biopsy")&md.F.notna()]
    md["chol"]=md["cell.annotation"].str.contains("holangio", case=False, na=False)
    frac=md.groupby(["donor","F"])["chol"].mean().reset_index()
    frac["Fs"]="F"+frac.F.astype(int).astype(str)
    for i,st in enumerate(STAGES):
        v=frac[frac.Fs==st]["chol"].values*100
        c.scatter(np.full(len(v),i)+jitter(len(v)), v, s=45, color="#0E7490", alpha=0.6, edgecolor="white", lw=0.5, zorder=3)
        if len(v): c.plot([i-0.28,i+0.28],[np.median(v)]*2,color="#0E7490",lw=3,zorder=4)
    c.set_xticks(range(5)); c.set_xticklabels(STAGES); c.set_ylabel("cholangiocyte % of nuclei")
except Exception as e:
    c.text(0.5,0.5,f"(cholangiocyte fraction\nfrom metadata)\n{e}",ha="center",transform=c.transAxes,fontsize=9)
c.set_title("C · Ductular reaction:\ncholangiocytes rise at F4", fontweight="bold", loc="left", fontsize=13)
c.grid(axis="y", color=GRID); c.set_axisbelow(True)
c.text(0.5,-0.30,"only ~0.4% of hepatocyte nuclei co-express\n≥2 biliary markers (summary stat)", transform=c.transAxes,
       ha="center", fontsize=10, color=MUTE)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_compositional.png", bbox_inches="tight"); plt.close(fig)

# ===================== FIG 6 (backup) — lobe invariance =====================
lo=pd.read_csv("findings/lobe_invariance/lobe_invariance.csv")
g3=["GLUL","ALDOB","CPS1"]; sub=lo[lo.gene.isin(g3)].set_index("gene").loc[g3]
fig,ax=plt.subplots(figsize=(7.5,4.4)); x=np.arange(3); w=0.25
for j,(lb_,cc) in enumerate(zip(["Right","Caudate","Left"],["#0D9488","#5EEAD4","#115E59"])):
    ax.bar(x+(j-1)*w, sub[f"frac_{lb_}"], w, label=lb_, color=cc)
ax.set_xticks(x); ax.set_xticklabels(g3); ax.set_ylabel("detection rate (UMI>0)")
ax.set_title("End-stage zonation detection is lobe-invariant", fontweight="bold", loc="left")
ax.legend(title="lobe", frameon=False); ax.grid(axis="y", color=GRID); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_lobe.png", bbox_inches="tight"); plt.close(fig)

# ===================== FIG 7 (backup) — explant heterogeneity =====================
ex=lb[lb.source=="explant"].copy().set_index("donor")
order_e=["CL104","CL18","CL103","CL17","CL16"]; ex=ex.loc[[d for d in order_e if d in ex.index]]
fig,ax=plt.subplots(figsize=(8.6,4.6)); bottom=np.zeros(len(ex))
for cls,color,nm in [("PC_f",PC,"PC-anchor"),("PP_f",PP,"PP-anchor"),("dual2_f",DUAL,"dual"),("null_f",NULL,"null")]:
    ax.bar(ex.index, ex[cls]*100, bottom=bottom*100, color=color, label=nm); bottom=bottom+ex[cls].values
ax.set_ylabel("% of hepatocyte nuclei"); ax.set_ylim(0,104)
# PP:PC ratio just above each bar's own total (not a fixed y — that collided with the title/legend)
tot=(ex["PC_f"]+ex["PP_f"]+ex["dual2_f"]+ex["null_f"]).values*100
for i,(dn,row) in enumerate(ex.iterrows()): ax.text(i, tot[i]+1.5, f"PP:PC {row['pppc']:.2f}", ha="center", fontsize=9, color=MUTE)
# title comes from the slide headline + figure caption; legend gets the cleared top strip
ax.legend(frameon=False, ncol=4, loc="lower center", bbox_to_anchor=(0.5,1.01))
fig.tight_layout(); fig.savefig(f"{OUT}/fig_explant.png", bbox_inches="tight"); plt.close(fig)

print("wrote figures to", OUT)
for f in sorted(os.listdir(OUT)): print("  ", f)
