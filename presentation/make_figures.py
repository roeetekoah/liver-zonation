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
from matplotlib.patches import Patch
from matplotlib.colors import to_rgba

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
panel(axes[0,0],"PC_f",PC,"Pericentral anchor"); axes[0,0].set_ylabel("PC-anchor %")
panel(axes[0,1],"dual2_f",DUAL,"Dual co-expression"); axes[0,1].set_ylabel("Dual (≥2 UMI) %")
axes[0,1].axhline(2.9, color=CONFOUND, ls="--", lw=1.5)
axes[0,1].text(4.0,2.9,"confounded explants ≈2.9%  (~7×)", color=CONFOUND, fontsize=10, va="bottom", ha="right")
panel(axes[1,0],"null_f",NULL,"Null (double-negative)"); axes[1,0].set_ylabel("Null %")
panel(axes[1,1],"pppc","#B45309","PP : PC balance", ratio=True); axes[1,1].set_ylabel("PP : PC ratio")
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
bigpanel(a1,"PC_f",PC,"Pericentral anchor","PC-anchor % of hepatocyte nuclei")
bigpanel(a2,"dual2_f",DUAL,"Dual co-expression","Dual (≥2 UMI) %")
a2.axhline(2.9, color=CONFOUND, ls="--", lw=2)
a2.text(4.05,2.95,"confounded explants ≈ 2.9%  (~7×)", color=CONFOUND, fontsize=12, va="bottom", ha="right", fontweight="bold")
a1.text(0.02,0.97,"donor = point, line = median", transform=a1.transAxes, fontsize=12, color=MUTE, va="top")
fig.tight_layout(); fig.savefig(f"{OUT}/fig_result2.png", bbox_inches="tight"); plt.close(fig)

# ---- headline result v3: PC depletion + PP depletion + dual, F1-F4 (F0 n=2 dropped) — BOX PLOTS ----
SR=["F1","F2","F3","F4"]

def boxpanel(ax,col,color,title,ylab,scale=100,explant_line=None,dec=0,
             legend=False,box_legend=False,top_pad=1.20):
    """Per-donor dots with the stage MEAN and its standard error
    (SEM = SD/sqrt(n); donor = the replicate). scale=100 -> percent; scale=1 -> raw ratio."""
    data=[bio[bio.Fs==st][col].values*scale for st in SR]
    top=max((v.max() if len(v) else 0) for v in data)
    for i,v in enumerate(data):
        n=len(v)
        ax.scatter(np.full(n,i)+jitter(n,0.11), v, s=40, color=color, alpha=0.45,
                   edgecolor="white", linewidth=0.6, zorder=3)
        if n:
            m=float(np.mean(v))
            sem=float(np.std(v,ddof=1)/np.sqrt(n)) if n>1 else 0.0
            ax.errorbar(i, m, yerr=sem, fmt="none", ecolor=color, elinewidth=2.2,
                        capsize=7, capthick=2.2, zorder=5)
            ax.plot([i-0.19,i+0.19],[m,m], color=color, lw=3.2, solid_capstyle="round", zorder=6)
            ax.annotate(f"{m:.{dec}f}%" if scale==100 else f"{m:.{dec}f}",
                        (i,m),xytext=(0.46,0),textcoords="offset fontsize",
                        ha="left",va="center",fontsize=11.5,fontweight="bold",color=color,zorder=7)
        ax.annotate(f"n={n}",(i,0),xytext=(0,-20),textcoords="offset points",
                    ha="center",va="top",fontsize=10,color=MUTE,zorder=6)
    ax.set_xticks(range(len(SR))); ax.set_xticklabels(SR)
    ax.set_xlim(-0.6,len(SR)-0.4); ax.set_ylim(0, top*top_pad)
    ax.set_title(title, loc="left"); ax.set_ylabel(ylab)
    clean(ax)
    if explant_line is not None:
        ax.axhline(explant_line, color=CONFOUND, ls=(0,(4,3)), lw=1.6)
        ax.text(len(SR)-0.55,explant_line,"  explants ≈ 2.9% (~7×)",color=CONFOUND,
                fontsize=10.5,va="bottom",ha="right",fontweight="bold")
    if legend:
        ax.legend(handles=[Line2D([0],[0],marker="o",ls="",mfc=color,mec="white",ms=8,
                                  alpha=0.7,label="donor"),
                           Line2D([0],[0],color=color,lw=3.2,label="stage mean"),
                           Line2D([0],[0],color=color,lw=2.2,label="± SEM")],
                  loc="upper left", fontsize=11)

fig,axs=plt.subplots(1,3,figsize=(12.4,5.9))
boxpanel(axs[0],"PC_f",PC,"Pericentral anchor","PC-anchor %", legend=True)
boxpanel(axs[1],"PP_f",PP,"Periportal anchor","PP-anchor %")
boxpanel(axs[2],"dual2_f",DUAL,"Dual co-expression","Dual (≥2 UMI) %",explant_line=2.9,dec=1)
fig.suptitle("Matched biopsy fibrosis F1–F4   ·   each point = one donor; bar = stage mean ± SEM   (F0 n=2 omitted; full F0–F4 in backup)",
             fontsize=12.5, color=MUTE, x=0.5, y=1.005, ha="center")
fig.tight_layout(rect=(0,0,1,0.97)); fig.savefig(f"{OUT}/fig_result3.png", bbox_inches="tight", pad_inches=0.15); plt.close(fig)

# ===================== FIG SECONDARY — null fraction + PP:PC ratio (box, F1-F4) =====================
fig,(s1,s2)=plt.subplots(1,2,figsize=(9.6,5.5))
boxpanel(s1,"null_f",NULL,"Null (double-negative)","Null (double-negative) %", legend=True)
boxpanel(s2,"pppc",DUAL,"PP : PC balance","PP : PC anchor ratio", scale=1, dec=2, top_pad=1.22)
s2.axhline(1.0, color=MUTE, ls=(0,(4,3)), lw=1.2, zorder=1)
s2.text(len(SR)-0.55, 1.0, "  balanced (1:1)", color=MUTE, fontsize=10.5, va="bottom", ha="right")
fig.suptitle("Secondary endpoints across biopsy F1–F4   ·   each point = one donor; bar = stage mean ± SEM",
             fontsize=12.5, color=MUTE, x=0.5, y=1.005, ha="center")
fig.tight_layout(rect=(0,0,1,0.97)); fig.savefig(f"{OUT}/fig_secondary.png", bbox_inches="tight", pad_inches=0.15); plt.close(fig)

# ===================== FIG GRADIENT SCHEMATIC — anti-diagonal compression vs dimming =====================
TEAL="#2C7A86"; AMBER="#E0701C"
def _poles(rng,n):
    """Two clouds at the poles of the anti-diagonal: bottom-right (PC-anchors) and top-left (PP-anchors)."""
    a=np.column_stack([rng.normal(0.78,0.07,n), rng.normal(0.22,0.07,n)])   # high PC / low PP
    b=np.column_stack([rng.normal(0.22,0.07,n), rng.normal(0.78,0.07,n)])   # low PC / high PP
    return np.vstack([a,b])
rng=np.random.RandomState(3); N=140
before=_poles(rng,N)
# compression: drift toward the MIDDLE of the anti-diagonal (one central cloud)
mid=np.array([0.5,0.5]); compress=before+(mid-before)*0.72+rng.normal(0,0.05,before.shape)
# dimming: pull toward the ORIGIN, keeping anti-diagonal orientation
dim=before*0.42+rng.normal(0,0.05,before.shape)
fig,(g1,g2)=plt.subplots(1,2,figsize=(11.0,5.6))
def _grad_ax(ax,after,after_color,title,after_label):
    ax.plot([0.05,0.95],[0.95,0.05],color=EDGE,ls="--",lw=1.4,zorder=1)   # anti-diagonal axis
    ax.text(0.07,0.07,"zonation gradient\n(anti-diagonal)",color=MUTE,fontsize=9.5,
            ha="left",va="bottom",style="italic",rotation=-45,rotation_mode="anchor")
    ax.scatter(before[:,0],before[:,1],s=26,color=NULL,alpha=0.45,edgecolor="none",zorder=2,label="intact (before)")
    ax.scatter(after[:,0],after[:,1],s=30,color=after_color,alpha=0.75,edgecolor="white",lw=0.4,zorder=3,label=after_label)
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.set_aspect("equal")
    ax.set_xticks([0,0.5,1]); ax.set_yticks([0,0.5,1])
    ax.set_xlabel("pericentral program"); ax.set_ylabel("periportal program")
    ax.set_title(title, loc="left")
    for sp in ("left","bottom"): ax.spines[sp].set_color(EDGE)
    ax.tick_params(length=0); ax.grid(False)
    ax.legend(loc="upper right", fontsize=10.5, markerscale=1.1)
_grad_ax(g1,compress,TEAL,"Compression","compressed (after)")
g1.annotate("",xy=(0.5,0.5),xytext=(0.78,0.22),arrowprops=dict(arrowstyle="->",color=TEAL,lw=1.6,alpha=0.7))
g1.annotate("",xy=(0.5,0.5),xytext=(0.22,0.78),arrowprops=dict(arrowstyle="->",color=TEAL,lw=1.6,alpha=0.7))
g1.text(0.5,0.40,"poles → middle",color=TEAL,fontsize=10,ha="center",fontweight="bold")
_grad_ax(g2,dim,AMBER,"Dimming","dimmed (after)")
g2.annotate("",xy=(0.30,0.085),xytext=(0.78,0.22),arrowprops=dict(arrowstyle="->",color=AMBER,lw=1.6,alpha=0.7))
g2.annotate("",xy=(0.085,0.30),xytext=(0.22,0.78),arrowprops=dict(arrowstyle="->",color=AMBER,lw=1.6,alpha=0.7))
g2.text(0.30,0.22,"poles → origin",color=AMBER,fontsize=10,ha="left",fontweight="bold")
fig.suptitle("Two de-zonation modes in anchor-program space   ·   SCHEMATIC (illustrative, synthetic cells)",
             fontsize=12.5, color=MUTE, x=0.5, y=1.01, ha="center")
fig.tight_layout(rect=(0,0,1,0.96)); fig.savefig(f"{OUT}/fig_gradient_schematic.png", bbox_inches="tight", pad_inches=0.12); plt.close(fig)

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

# ===================== FIG GRADIENT (stretch) — per-cell zonal balance, deck style =====================
# Regenerates results/figures/h2/gradient_polarization_dist.png in the clean deck aesthetic.
# x = per-cell PC/(PC+PP) program balance after binomial down-thinning to 1,500 UMIs/nucleus (8-draw avg),
# donor-balanced (<=300 informative nuclei/donor). y = fraction of cells per bin. Biopsy F1-F4 + explant.
try:
    Bz=1500; NDRAW=8; CAP=300
    PCprog=["GLUL","CYP3A4","CYP2E1","CYP1A2","ADH4","AKR1D1","SLCO1B3"]
    PPprog=["CPS1","ASS1","ALDOB","PCK1","HAL","ARG1"]
    dfc=pd.read_csv("data/processed/paper1/raw_panel_counts.csv",low_memory=False); dfc["donor"]=dfc["donor"].astype(str)
    mdc=pd.read_csv("data/processed/paper1/metadata_all_cells.csv",
                    usecols=["Patient.ID","Fibrosis.score..F0.4."],low_memory=False).rename(
                    columns={"Patient.ID":"donor","Fibrosis.score..F0.4.":"F"})
    mdc["donor"]=mdc["donor"].astype(str); mdc["F"]=pd.to_numeric(mdc["F"],errors="coerce")
    dfc=dfc.merge(mdc.groupby("donor")["F"].first().reset_index(),on="donor",how="left")
    hep=dfc[dfc["annotation"]=="Hepatocytes"].copy()
    hep["grp"]=np.where(hep["donor"].str.startswith("CL"),"Explant",
               np.where(hep["stage"]=="Healthy control","Healthy",hep["F"].map({0:"F0",1:"F1",2:"F2",3:"F3",4:"F4"})))
    h=hep[hep["E_raw"]>=Bz].copy(); E=h["E_raw"].values; rng=np.random.RandomState(0); p=Bz/E
    def _thin(genes):
        acc=np.zeros(len(h))
        for g in genes:
            if g in h:
                a=np.zeros(len(h))
                for _ in range(NDRAW): a+=rng.binomial(h[g].values.astype(int),p)
                acc+=a/NDRAW
        return acc
    PCv=_thin(PCprog); PPv=_thin(PPprog); tot=PCv+PPv
    h["frac"]=np.where(tot>0,PCv/np.maximum(tot,1),np.nan); h["inf"]=tot>=3
    panels=["F1","F2","F3","F4","Explant"]
    pcols={"F1":BIOPSY,"F2":BIOPSY,"F3":BIOPSY,"F4":BIOPSY,"Explant":CONFOUND}
    fig,axes=plt.subplots(1,5,figsize=(15.5,4.0),sharey=True); bins=np.linspace(0,1,21); bc=(bins[:-1]+bins[1:])/2
    def _panel(grp):
        s=h[(h["grp"]==grp)&(h["inf"])]
        parts=[g.sample(min(len(g),CAP),random_state=1) for _,g in s.groupby("donor")]
        sb=pd.concat(parts) if parts else s; v=sb["frac"].dropna().values
        return sb,v,np.histogram(v,bins=bins,weights=np.ones(len(v))/max(len(v),1))[0]
    _,_,hF1=_panel("F1")   # F1 reference distribution — overlaid on every panel to show it barely moves
    for ax,grp in zip(axes.ravel(),panels):
        sb,v,_=_panel(grp); col=pcols[grp]
        ax.hist(v,bins=bins,weights=np.ones(len(v))/max(len(v),1),color=to_rgba(col,0.85),edgecolor="white",linewidth=0.5,zorder=3)
        if grp!="F1":   # the "does the cloud move?" cue: same F1 outline on every later stage
            ax.plot(bc,hF1,color=INK,lw=1.5,ls=(0,(3,2)),drawstyle="steps-mid",zorder=5)
        ax.axvline(0.5,color=EDGE,ls=(0,(4,3)),lw=1.1,zorder=2)
        ax.set_title(f"{grp}\n(donors={sb['donor'].nunique()}, n={len(v):,})",loc="left",fontsize=12.5)
        ax.set_xlim(0,1); ax.set_xticks([0,0.5,1]); ax.set_xticklabels(["0","0.5","1"]); clean(ax); ax.grid(axis="x",visible=False)
    axes[0].set_ylabel("fraction of cells in bin")
    axes[4].legend(handles=[Line2D([0],[0],color=INK,lw=1.5,ls=(0,(3,2)),label="F1 reference")],loc="upper right",fontsize=10.5,frameon=False)
    fig.text(0.5,-0.01,"per-cell zonal balance   PC / (PC + PP)      ( 0 = periportal  ·  1 = pericentral )",ha="center",fontsize=12.5,color=MUTE)
    fig.suptitle("Per-cell zonal balance by stage — the distribution barely moves across biopsy F1–F4 (dashed = F1 reference); only the confounded explant collapses to one pole",
                 fontsize=12.5, color=MUTE, x=0.5, y=1.04, ha="center")
    fig.tight_layout(rect=(0,0,1,0.96)); fig.savefig(f"{OUT}/fig_gradient.png", bbox_inches="tight", pad_inches=0.12); plt.close(fig)
    print("wrote fig_gradient.png (per-cell data found)")
except Exception as e:
    print("SKIPPED fig_gradient.png (blocked):", e)

# ===================== FIG DIMMING — within-PC detox output + gene-set result =====================
try:
    UP="#C0561B"   # up-with-fibrosis colour
    wd=pd.read_csv(f"{T}/geneset_verify_within_pc_detox.csv")
    st=wd[wd["stage"].isin(["F0","F1","F2","F3","F4"])].copy()
    st["x"]=st["stage"].map({"F0":0,"F1":1,"F2":2,"F3":3,"F4":4})
    cam=pd.read_csv(f"{T}/geneset_camera.csv").set_index("gene_set")
    fig,(a1,a2)=plt.subplots(1,2,figsize=(12.4,4.6),gridspec_kw={"width_ratios":[1.0,1.18]})
    # LEFT — within-PC detox output by stage (mean +/- sd; F0 faded, n=2)
    for _,r in st.iterrows():
        fz=(r["stage"]=="F0")
        a1.errorbar(r["x"],r["mean"],yerr=r["sd"],fmt="o",ms=10,color=(MUTE if fz else BIOPSY),
                    ecolor=(GRID if fz else to_rgba(BIOPSY,0.45)),elinewidth=2.2,capsize=4,zorder=4,alpha=(0.45 if fz else 1))
    bio=st[st["stage"]!="F0"]; m,b=np.polyfit(bio["x"],bio["mean"],1); xx=np.array([1,4])
    a1.plot(xx,m*xx+b,color=CONFOUND,lw=2,ls=(0,(4,3)),zorder=3)
    a1.set_xticks([0,1,2,3,4]); a1.set_xticklabels(["F0","F1","F2","F3","F4"]); a1.set_xlim(-0.4,4.4)
    a1.set_ylabel("detox transcripts per PC nucleus\n(depth-matched to 1,500 UMIs)")
    a1.set_title("Within-PC detox output falls with fibrosis",loc="left",fontsize=14)
    a1.annotate("ρ = −0.48,  p = 0.003\n(donor-level trend)",xy=(0.96,0.95),xycoords="axes fraction",
                ha="right",va="top",fontsize=12.5,color=CONFOUND,fontweight="bold")
    a1.annotate("F0 faded (n=2)",xy=(0.03,0.05),xycoords="axes fraction",fontsize=10,color=MUTE)
    clean(a1)
    # RIGHT — gene-set programs, signed significance
    order=["xenobiotic_CYP","pericentral_anchors","detox_phase2","cholangiocyte_ductular","CTRL_EMT","CTRL_interferon","CTRL_ER_stress"]
    lab={"xenobiotic_CYP":"PC detox (CYP)","pericentral_anchors":"PC landmark set","detox_phase2":"PC detox (phase-II)",
         "cholangiocyte_ductular":"biliary / ductular","CTRL_EMT":"fibrogenesis  ctrl","CTRL_interferon":"inflammation  ctrl","CTRL_ER_stress":"ER-stress  ctrl"}
    ys=np.arange(len(order))[::-1]
    for y,gs in zip(ys,order):
        row=cam.loc[gs]; sl=(-1 if row["Direction"]=="Down" else 1)*(-np.log10(max(row["FDR"],1e-30)))
        col=BIOPSY if row["Direction"]=="Down" else UP
        if row["FDR"]>0.05: col=MUTE
        a2.barh(y,sl,color=col,height=0.62,zorder=3)
    a2.axvline(0,color=INK,lw=1)
    a2.set_yticks(ys); a2.set_yticklabels([lab[g] for g in order],fontsize=11.5)
    a2.set_xlabel(r"signed  $-\log_{10}$(FDR)      ←  down with fibrosis      up  →")
    a2.set_title("Gene-set: detox dims hardest; identity gates held",loc="left",fontsize=14)
    a2.text(0.025,0.32,"Gating genes GLUL/CYP3A4\nflat → identity held",
            transform=a2.transAxes,fontsize=9.5,color=MUTE,va="center",ha="left",style="italic")
    clean(a2); a2.grid(axis="x",visible=True,color=GRID); a2.grid(axis="y",visible=False)
    fig.tight_layout(); fig.savefig(f"{OUT}/fig_dimming.png",bbox_inches="tight",pad_inches=0.12); plt.close(fig)
    print("wrote fig_dimming.png")
except Exception as e:
    print("SKIPPED fig_dimming.png:",e)

# single clean panel — within-PC detox decline (the per-cell, composition-immune evidence for the dimming slide)
try:
    wd=pd.read_csv(f"{T}/geneset_verify_within_pc_detox.csv")
    st=wd[wd["stage"].isin(["F0","F1","F2","F3","F4"])].copy()
    st["x"]=st["stage"].map({"F0":0,"F1":1,"F2":2,"F3":3,"F4":4})
    fig,a1=plt.subplots(figsize=(7.6,4.7))
    for _,r in st.iterrows():
        fz=(r["stage"]=="F0")
        a1.errorbar(r["x"],r["mean"],yerr=r["sd"],fmt="o",ms=12,color=(MUTE if fz else BIOPSY),
                    ecolor=(GRID if fz else to_rgba(BIOPSY,0.45)),elinewidth=2.6,capsize=5,zorder=4,alpha=(0.45 if fz else 1))
    bio=st[st["stage"]!="F0"]; m,b=np.polyfit(bio["x"],bio["mean"],1); xx=np.array([1,4])
    a1.plot(xx,m*xx+b,color=CONFOUND,lw=2.6,ls=(0,(4,3)),zorder=3)
    a1.set_xticks([0,1,2,3,4]); a1.set_xticklabels(["F0","F1","F2","F3","F4"],fontsize=12); a1.set_xlim(-0.4,4.4)
    a1.set_ylabel("detox transcripts per PC nucleus\n(depth-matched to 1,500 UMIs)")
    a1.set_title("Within pericentral cells, detox output falls with fibrosis",loc="left",fontsize=14)
    a1.annotate("ρ = −0.48,  p = 0.003\n(donor-level trend)",xy=(0.96,0.95),xycoords="axes fraction",
                ha="right",va="top",fontsize=13.5,color=CONFOUND,fontweight="bold")
    a1.annotate("measured on detox genes separate from the GLUL/CYP3A4 gates",xy=(0.03,0.06),xycoords="axes fraction",fontsize=10.5,color=MUTE,style="italic")
    clean(a1)
    fig.tight_layout(); fig.savefig(f"{OUT}/fig_within_pc_detox.png",bbox_inches="tight",pad_inches=0.12); plt.close(fig)
    print("wrote fig_within_pc_detox.png")
except Exception as e:
    print("SKIPPED fig_within_pc_detox:",e)

# gene-set robustness landscape — competitive (camera, x) vs self-contained (roast, y); one point per program
try:
    cam=pd.read_csv(f"{T}/geneset_camera.csv").set_index("gene_set")
    ro=pd.read_csv(f"{T}/geneset_verify_roast.csv").set_index("gene_set")
    META={"xenobiotic_CYP":("PC detox (CYP)",PC,1),"pericentral_anchors":("PC identity",PC,0),
          "detox_phase2":("phase-II detox",PC,0),"urea_cycle":("urea cycle",PP,0),
          "periportal_anchors":("PP identity",PP,0),"cholangiocyte_ductular":("biliary",BILIARY,0),
          "CTRL_EMT":("fibrogenesis",MUTE,0),"CTRL_interferon":("inflammation",MUTE,0),
          "CTRL_ER_stress":("ER-stress",MUTE,0),"bile_acid_lipid":("bile/lipid",MUTE,0)}
    def sxy(gs):
        cd=cam.loc[gs]; rd=ro.loc[gs]
        x=(-1 if cd["Direction"]=="Down" else 1)*(-np.log10(max(cd["FDR"],1e-30)))
        y=(-1 if rd["Direction"]=="Down" else 1)*(-np.log10(max(rd["FDR"],1e-30)))
        return x,y
    thr=-np.log10(0.05); xlim=(-6.9,6.3); ylim=(-2.7,2.7)
    fig,ax=plt.subplots(figsize=(8.9,5.4)); ax.grid(False)
    ax.add_patch(plt.Rectangle((xlim[0],-thr),-thr-xlim[0],2*thr,facecolor=to_rgba(CONFOUND,0.14),edgecolor=CONFOUND,lw=1.4,ls=(0,(5,3)),zorder=0))   # competitive-only band (red)
    ax.add_patch(plt.Rectangle((xlim[0],ylim[0]),-thr-xlim[0],-thr-ylim[0],facecolor=to_rgba("#15803D",0.20),edgecolor="#15803D",lw=2.0,zorder=1))     # ROBUST corner (green)
    ax.add_patch(plt.Rectangle((thr,thr),xlim[1]-thr,ylim[1]-thr,facecolor=to_rgba(MUTE,0.10),edgecolor="none",lw=0,zorder=0))                         # controls-up corner (faint)
    ax.axvline(0,color="#9AA6A4",lw=1,zorder=1); ax.axhline(0,color="#9AA6A4",lw=1,zorder=1)
    for v in (thr,-thr):
        ax.axvline(v,color="#C7CFCE",ls=(0,(3,3)),lw=1,zorder=1); ax.axhline(v,color="#C7CFCE",ls=(0,(3,3)),lw=1,zorder=1)
    for gs,(lab,col,hi) in META.items():
        if gs not in cam.index or gs not in ro.index: continue
        x,y=sxy(gs); x=min(max(x,xlim[0]+0.2),xlim[1]-0.2); y=min(max(y,ylim[0]+0.2),ylim[1]-0.2)
        ax.scatter(x,y,s=(300 if hi else 150),color=col,edgecolor=("#16242B" if hi else "white"),linewidth=(1.6 if hi else 1.1),zorder=6,alpha=0.96)
    for gs,(dx,dy,ha) in {"xenobiotic_CYP":(13,6,"left"),"pericentral_anchors":(0,12,"center"),"detox_phase2":(8,-12,"left")}.items():
        x,y=sxy(gs); ax.annotate(META[gs][0],(x,y),xytext=(dx,dy),textcoords="offset points",fontsize=11,fontweight="bold",color=PC,ha=ha,zorder=7)
    ax.text(xlim[0]+0.22,ylim[0]+0.18,"ROBUST ↓",fontsize=12.5,fontweight="bold",color="#15803D",va="bottom",ha="left",zorder=8)
    ax.text(xlim[0]+0.22,0.12,"competitive only — weak lean:\nPC identity · phase-II",fontsize=10.5,fontweight="bold",color=CONFOUND,va="bottom",ha="left",style="italic",zorder=8)
    ax.text(4.65,1.46,"biliary + fibrogenesis ↑",fontsize=10,color=MUTE,va="top",ha="center",style="italic",zorder=8)
    ax.text(2.85,0.42,"inflammation ↑",fontsize=10,color=MUTE,va="top",ha="center",style="italic",zorder=8)
    ax.text(0.2,-0.16,"flat: urea · bile/lipid · ER-stress",fontsize=9.5,color=MUTE,va="top",ha="left",style="italic",zorder=5)
    from matplotlib.lines import Line2D as _L2D
    _leg=[_L2D([0],[0],marker='o',color='w',markerfacecolor=PC,markersize=8,label='pericentral'),
          _L2D([0],[0],marker='o',color='w',markerfacecolor=PP,markersize=8,label='periportal'),
          _L2D([0],[0],marker='o',color='w',markerfacecolor=MUTE,markersize=8,label='control'),
          _L2D([0],[0],marker='o',color='w',markerfacecolor=BILIARY,markersize=8,label='biliary')]
    ax.legend(handles=_leg,loc='upper left',frameon=False,fontsize=9.5,handletextpad=0.15,labelspacing=0.2,borderpad=0.2)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_xlabel("Competitive test (camera) — signed −log10 FDR        ← down   ·   up →")
    ax.set_ylabel("Self-contained test (roast)\n← down   ·   up →")
    ax.set_title("Of every program tested, only pericentral detox is robust in both tests")
    for sp in ("top","right"): ax.spines[sp].set_visible(False)
    fig.tight_layout(); fig.savefig(f"{OUT}/fig_geneset_landscape.png",bbox_inches="tight",pad_inches=0.14); plt.close(fig)
    print("wrote fig_geneset_landscape.png")
except Exception as e:
    print("SKIPPED fig_geneset_landscape:",e)

# landmark-set decomposition: the "identity" set is >half detox by construction; its dip is the detox members
try:
    import glob as _g
    _ff=_g.glob("data/signatures/**/pericentral_paper2_landmark.txt",recursive=True)+_g.glob("data/signatures/pericentral_paper2_landmark.txt")
    land=[x.strip() for x in open(_ff[0]) if x.strip() and not x.startswith("#")]
    DETOX={"CYP2E1","CYP1A2","CYP3A4","CYP3A5","CYP3A43","CYP2C8","CYP2C9","CYP2C19","CYP2B6","CYP1A1","CYP2A6","CYP2D6","CYP4F12",
           "UGT1A1","UGT2B4","UGT2B7","GSTA1","GSTA2","SULT2A1","SULT1A1","AKR1D1","AKR1C1","ADH1A","ADH1B","ADH4","ALDH1L1","FMO3","AOX1","AMACR"}
    dge=pd.read_csv(f"{T}/dge_planA_F4vsF1.csv"); gc=dge.columns[0]
    lcc=[c for c in dge.columns if c.lower()=="logfc"][0]; dd=dge.set_index(gc)[lcc]
    rows=sorted([(g,dd.get(g,np.nan),(g in DETOX)) for g in land if g in dd.index],key=lambda r:r[1])
    fig,ax=plt.subplots(figsize=(8.6,5.7)); ax.grid(axis="x",color=GRID); ax.grid(axis="y",visible=False)
    ys=np.arange(len(rows))
    for y,(g,lf,isd) in zip(ys,rows):
        ax.barh(y,lf,color=(AMBER if isd else PC),height=0.72,zorder=3,alpha=0.92)
    ax.axvline(0,color=INK,lw=1.1,zorder=4)
    ax.set_yticks(ys); ax.set_yticklabels([g for g,_,_ in rows],fontsize=10.5)
    for y,(g,lf,isd) in zip(ys,rows):
        t=ax.get_yticklabels()[y]; t.set_color(AMBER if isd else PC); t.set_fontweight("bold")
    nd=[lf for _,lf,isd in rows if isd]; npos=[lf for _,lf,isd in rows if not isd]
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=AMBER,label=f"detox enzyme ({len(nd)} of 20) — mean {np.mean(nd):+.2f}"),
                       Patch(color=PC,label=f"positional marker ({len(npos)} of 20) — mean {np.mean(npos):+.2f}")],
              loc="upper left",frameon=False,fontsize=11.5)
    ax.set_xlabel("log2 fold-change   (cirrhotic F4 vs early F1)        ← down")
    ax.set_title("The “identity” landmark set’s dip is its detox genes — the positional markers hold")
    ax.set_ylim(-0.7,len(rows)-0.3)
    for sp in ("top","right"): ax.spines[sp].set_visible(False)
    fig.tight_layout(); fig.savefig(f"{OUT}/fig_landmark_decomp.png",bbox_inches="tight",pad_inches=0.14); plt.close(fig)
    print("wrote fig_landmark_decomp.png")
except Exception as e:
    print("SKIPPED fig_landmark_decomp:",e)

print("wrote figures to", OUT)
for f in sorted(os.listdir(OUT)): print("  ", f)
