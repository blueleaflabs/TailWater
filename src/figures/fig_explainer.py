"""Explainer figures 1-3 (fig1_two_gauges, fig2_monthly_below5, fig3_longitudinal).
fig2_monthly_below5.png is also Note Figure 3 (monthly share of readings >= 5 mg/L, four gauges).
Writes to paper/figs/."""
import sys, os, pathlib; ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / 'src')); os.chdir(ROOT)  # run from any cwd
import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from metrics import load
from figstyle import COLORS as C, INK, MUTED, GRID, SURF
import figstyle; figstyle.apply()
A=load('11152850'); B=load('11152870'); S=load('11152890'); D=load('11153000')

# ---- Fig 1: three months, above vs below, 15-min
a,z='2024-06-01','2024-08-31'
fig,ax=plt.subplots(figsize=(7.2,3.4),dpi=300)
ax.plot(A[a:z].index,A[a:z]['DO'],color=C['above'],lw=0.9,label='Above reservoir (USGS 11152850)')
ax.plot(B[a:z].index,B[a:z]['DO'],color=C['below'],lw=0.9,label='Below dam, 0.1 km (USGS 11152870)')
ax.axhline(7,color=MUTED,lw=0.8,ls='--'); ax.text(pd.Timestamp('2024-07-08'),7.15,'7 mg/L cold-water objective',ha='left',va='bottom',color=MUTED,fontsize=7)
ax.axhline(5,color=MUTED,lw=0.8,ls=':'); ax.text(pd.Timestamp('2024-07-08'),5.15,'5 mg/L warm-water objective',ha='left',va='bottom',color=MUTED,fontsize=7)
ax.annotate('upstream reach dries;\ngauge record ends',xy=(pd.Timestamp('2024-07-05'),9.2),xytext=(pd.Timestamp('2024-07-12'),12.6),fontsize=6.5,color=MUTED,arrowprops=dict(arrowstyle='-',color=MUTED,lw=0.7))
ax.annotate('release tapers to a trickle',xy=(pd.Timestamp('2024-07-10'),0.6),xytext=(pd.Timestamp('2024-06-14'),3.3),fontsize=6.5,color=INK,arrowprops=dict(arrowstyle='-',color=MUTED,lw=0.7))
ax.annotate('sustained release resumes',xy=(pd.Timestamp('2024-07-28'),4.3),xytext=(pd.Timestamp('2024-07-30'),8.6),fontsize=6.5,color=INK,arrowprops=dict(arrowstyle='-',color=MUTED,lw=0.7))
ax.set_ylim(0,14); ax.set_ylabel('Dissolved oxygen (mg/L)'); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax.set_title('North Fork Pacheco Creek, June\u2013August 2024: the same creek above and below the dam',fontsize=9.5,color=INK,loc='left')
ax.legend(frameon=False,loc='upper right',fontsize=7.5); fig.tight_layout(); fig.savefig('paper/figs/fig1_two_gauges.png'); plt.close()

# ---- Fig 2: monthly share of readings below 5 mg/L, four mainstem sites
sites=[('Above reservoir',A,C['above']),('Below dam (0.1 km)',B,C['below']),('Bell Station (~3 km)',S,C['bell']),('Dunneville (~13 km)',D,C['dunn'])]
months=pd.period_range('2024-03','2025-09',freq='M')
fig,axes=plt.subplots(4,1,figsize=(7.2,5.2),dpi=300,sharex=True)
for ax,(lab,w,col) in zip(axes,sites):
    do=w['DO']; vals=[]
    for m in months:
        g=do[(do.index.to_period('M')==m)].dropna(); vals.append(100*(g>=5).mean() if len(g)>=500 else np.nan)
    x=np.arange(len(months)); ax.bar(x,vals,color=col,width=0.72)
    ax.set_ylim(0,100); ax.set_yticks([0,50,100]); ax.set_ylabel('% \u2265 5 mg/L',fontsize=8)
    ax.text(-0.005,1.02,lab,transform=ax.transAxes,fontsize=8,color=INK,ha='left',va='bottom')
    for xi,v in zip(x,vals):
        if np.isnan(v): ax.text(xi,4,'insufficient data',ha='center',fontsize=5,color=MUTED,rotation=90)
axes[-1].set_xticks(np.arange(len(months))); axes[-1].set_xticklabels([m.strftime('%b\n%y') for m in months],fontsize=7)
fig.suptitle('Share of 15-min readings at or above 5 mg/L, by month',fontsize=9.5,color=INK,x=0.085,ha='left',y=0.995)
fig.tight_layout(h_pad=1.2,rect=(0,0,1,0.97)); fig.savefig('paper/figs/fig2_monthly_below5.png'); plt.close()

# ---- Fig 3: release-season daily-mean DO by site, 2024 and 2025 side by side
seasons=[('2024','2024-05-01','2024-09-30'),('2025','2025-04-01','2025-08-04')]
fig,ax=plt.subplots(figsize=(7.2,3.4),dpi=300)
pos=[];data=[];cols=[];hatch=[]
for i,(lab,w,col) in enumerate(sites):
    for j,(yr,a,z) in enumerate(seasons):
        d=w[a:z]['DO'].resample('D').agg(['count','mean']); d=d[d['count']>=86]['mean']
        pos.append(i*3+j*0.9); data.append(d.values); cols.append(col); hatch.append(j)
bp=ax.boxplot(data,positions=pos,patch_artist=True,widths=0.7,medianprops=dict(color=INK,lw=1.2),whiskerprops=dict(color=MUTED),capprops=dict(color=MUTED),flierprops=dict(marker='.',markersize=3,markerfacecolor=MUTED,markeredgecolor='none'))
for p,c,h in zip(bp['boxes'],cols,hatch):
    p.set_facecolor(c); p.set_edgecolor(c if h else 'none'); p.set_alpha(0.85 if h==0 else 0.45); p.set_linewidth(1.2)
ax.set_xticks([i*3+0.45 for i in range(4)]); ax.set_xticklabels([l for l,_,_ in sites],fontsize=8); ax.tick_params(axis='x',pad=4)
for i in range(4):
    ax.text(i*3,11.75,'2024',ha='center',va='top',fontsize=6.5,color=MUTED); ax.text(i*3+0.9,11.75,'2025',ha='center',va='top',fontsize=6.5,color=MUTED)
ax.set_ylabel('Daily mean DO (mg/L)'); ax.set_ylim(0,12)
ax.axhline(7,color=MUTED,lw=0.8,ls='--'); ax.text(10.9,7.1,'7 mg/L',ha='right',va='bottom',color=MUTED,fontsize=7.5)
ax.axhline(5,color=MUTED,lw=0.8,ls=':'); ax.text(10.9,5.1,'5 mg/L',ha='right',va='bottom',color=MUTED,fontsize=7.5)
ax.set_title('Daily mean dissolved oxygen along Pacheco Creek, release seasons 2024 (solid) and 2025 (light)',fontsize=9.5,color=INK,loc='left')
fig.tight_layout(); fig.savefig('paper/figs/fig3_longitudinal.png'); plt.close()
print('ok')
