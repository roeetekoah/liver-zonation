"""Simpson-paradox reveal figure for the deck: the legacy PC-PP anti-correlation 'collapse' is a
sampling-mode jump (needle biopsy vs deceased-donor organ cube), not a within-biopsy disease trajectory.
Reads legacy_simpson.csv (per-donor anti-corr + naive stage index). Deck palette."""
import os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
TEAL='#1B6E78'; AMBER='#C0561B'; INK='#16242B'; MUTE='#5c6e73'; LINE='#d8d2c8'
D=pd.read_csv(os.path.join(str(config.ANALYSIS_TABLES),'legacy_simpson.csv'))
xlab={0:'Healthy',1:'F0',2:'F1',3:'F2',4:'F3',5:'F4',6:'End-stage'}
rng=np.random.RandomState(1)
fig,ax=plt.subplots(figsize=(10.6,5.4),dpi=200)
ax.axhline(0,color=LINE,lw=1.2,zorder=1)
for _,r in D.iterrows():
    cube = r['source'] in ('healthy','end-stage')
    c = AMBER if cube else TEAL
    x = r['stage_idx'] + rng.uniform(-0.16,0.16)
    ax.scatter(x, r['anti'], s=70, color=c, edgecolor='white', linewidth=0.8, zorder=3, alpha=0.92)
# per-stage median markers
for i in range(7):
    s=D[D.stage_idx==i]
    if len(s): ax.plot([i-0.22,i+0.22],[s['anti'].median()]*2,color=INK,lw=2.4,zorder=4)
# pooled "collapse" trend arrow
ax.annotate('', xy=(6,0.06), xytext=(0.2,-0.22),
            arrowprops=dict(arrowstyle='-|>',color=MUTE,lw=2.0,ls=(0,(5,4))),zorder=2)
ax.text(2.0,-0.02,'pooled "collapse"\nSpearman +0.44, p=0.002',color=MUTE,fontsize=11,style='italic',ha='center')
# biopsy band
ax.axvspan(0.55,5.45,color=TEAL,alpha=0.05,zorder=0)
ax.text(3.0,-0.52,'within needle-biopsy F0–F4:  +0.29,  p=0.078  (n.s.)',color=TEAL,fontsize=11,ha='center',weight='bold')
ax.set_xticks(range(7)); ax.set_xticklabels([xlab[i] for i in range(7)],fontsize=11.5)
ax.set_ylabel('per-donor PC–PP anti-correlation\n(more negative = more zonated)',fontsize=11.5,color=INK)
ax.set_ylim(-0.62,0.16)
ax.set_title('The "collapse" is a sampling-mode jump, not a disease trajectory',fontsize=13.5,color=INK,weight='bold',pad=10)
# legend
from matplotlib.lines import Line2D
leg=[Line2D([0],[0],marker='o',color='w',markerfacecolor=TEAL,markersize=10,label='needle biopsy (disease F0–F4)'),
     Line2D([0],[0],marker='o',color='w',markerfacecolor=AMBER,markersize=10,label='deceased-donor organ cube (healthy + end-stage)')]
ax.legend(handles=leg,loc='lower left',fontsize=10,frameon=False)
for sp in ['top','right']: ax.spines[sp].set_visible(False)
for sp in ['left','bottom']: ax.spines[sp].set_color(LINE)
ax.tick_params(colors=MUTE)
plt.tight_layout()
out=os.path.join(str(config.PROJECT_ROOT) if hasattr(config,'PROJECT_ROOT') else '.','results','figures','h2','simpson_anticorr.png')
os.makedirs(os.path.dirname(out),exist_ok=True)
plt.savefig(out,dpi=200,bbox_inches='tight',facecolor='white')
print('wrote',out)
