"""Note Figure 2: two-year daily DO (above reservoir vs below dam) with min-max bands,
longest low-oxygen episodes, and the daily water-temperature range below the dam.
Writes paper/figs/note_fig2_timeseries.png."""
import sys, os, pathlib; ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / 'src')); os.chdir(ROOT)  # run from any cwd
import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from metrics import load
from figstyle import COLORS as C, INK, MUTED, GRID, SURF
import figstyle; figstyle.apply()
A=load('11152850'); B=load('11152870')
def daily(w,col):
    d=w[col].resample('D').agg(['count','mean','min','max']); return d[d['count']>=86]
bd=daily(B,'DO'); ad=daily(A,'DO'); bt=daily(B,'T')
full=pd.date_range('2024-03-01','2025-10-01',freq='D'); bd=bd.reindex(full); ad=ad.reindex(full); bt=bt.reindex(full)
a,z=pd.Timestamp('2024-03-01'),pd.Timestamp('2025-10-02')
fig,(ax1,ax2)=plt.subplots(2,1,figsize=(7.2,4.6),dpi=300,sharex=True,gridspec_kw={'height_ratios':[2.4,1]})
# stratified-season shading
for yr in (2024,2025): ax1.axvspan(pd.Timestamp(f'{yr}-04-01'),pd.Timestamp(f'{yr}-11-01'),color='#f0efec',zorder=0); ax2.axvspan(pd.Timestamp(f'{yr}-04-01'),pd.Timestamp(f'{yr}-11-01'),color='#f0efec',zorder=0)
ax1.fill_between(ad.index,ad['min'],ad['max'],color=C['above'],alpha=0.18,lw=0,step=None)
ax1.plot(ad.index,ad['mean'],color=C['above'],lw=1.1,label='Above reservoir: daily mean (band = daily min–max)')
ax1.fill_between(bd.index,bd['min'],bd['max'],color=C['below'],alpha=0.25,lw=0)
ax1.plot(bd.index,bd['mean'],color=C['below'],lw=1.1,label='Below dam: daily mean (band = daily min–max)')
ax1.axhline(7,color=MUTED,lw=0.8,ls='--'); ax1.axhline(5,color=MUTED,lw=0.8,ls=':'); ax1.axhline(3,color=MUTED,lw=0.8,ls='-.')
ax1.text(z,7.1,'7',ha='right',va='bottom',color=MUTED,fontsize=7); ax1.text(z,5.1,'5',ha='right',va='bottom',color=MUTED,fontsize=7); ax1.text(z,3.1,'3 mg/L',ha='right',va='bottom',color=MUTED,fontsize=7)
# episodes
for s,e,lab,y,side in [('2024-06-12','2024-07-28','46 d < 3 mg/L',-0.25,'l'),('2025-05-01','2025-07-04','65 d < 3 mg/L',-0.25,'l'),('2025-05-14','2025-06-29','46 d < 1 mg/L',-0.65,'r'),('2024-07-12','2024-07-25','13 d < 1 mg/L',-0.65,'r')]:
    S_,E_=pd.Timestamp(s),pd.Timestamp(e)
    ax1.plot([S_,E_],[y,y],color=INK,lw=1.4,solid_capstyle='butt',clip_on=False)
    if side=='c': ax1.text(S_+(E_-S_)/2,y-0.1,lab,ha='center',va='top',fontsize=6,color=INK,clip_on=False)
    elif side=='l': ax1.text(S_-pd.Timedelta(days=4),y,lab,ha='right',va='center',fontsize=6,color=INK,clip_on=False)
    else: ax1.text(E_+pd.Timedelta(days=4),y,lab,ha='left',va='center',fontsize=6,color=INK,clip_on=False)
ax1.set_ylim(-0.9,14); ax1.set_yticks(range(0,15,2)); ax1.set_ylabel('Dissolved oxygen (mg/L)')
ax1.legend(frameon=False,fontsize=7,loc='upper center',bbox_to_anchor=(0.40,1.0))
ax2.plot(bt.index,bt['max']-bt['min'],color=C['below'],lw=1.0)
ax2.set_ylabel('Daily water temperature\nrange, below dam (°C)',fontsize=8); ax2.set_ylim(0,14); ax2.set_yticks([0,4,8,12])
ax2.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1,4,7,10])); ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y')); ax2.set_xlim(a,z)
fig.tight_layout(h_pad=0.6); fig.savefig('paper/figs/note_fig2_timeseries.png'); print('ok')
