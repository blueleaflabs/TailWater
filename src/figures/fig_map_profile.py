"""Note Figure 1: schematic gauge map with California inset, and DO against channel distance
from the dam for the 2024 and 2025 station-comparison windows.
Writes paper/figs/fig4_map_profile.png."""
import sys, os, pathlib; ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / 'src')); os.chdir(ROOT)  # run from any cwd
import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from metrics import load
from figstyle import COLORS as C, INK, MUTED, GRID, SURF
import figstyle; figstyle.apply()
# site: (label, lat, lon, channel km from dam, color)
S={'11152850':('Above reservoir',37.0867,-121.2876,-5.0,C['above']),
   '11152870':('Below dam',37.0495,-121.2911,0.1,C['below']),
   '11152890':('Bell Station',37.0348,-121.3101,3.0,C['bell']),
   '11153000':('Dunneville',36.9800,-121.3803,13.0,C['dunn'])}
T={'11152880':('South Fork (trib.)',37.0437,-121.2759),'11152900':('Cedar Creek (trib.)',37.0499,-121.3274)}
DAM=(37.0498,-121.2921); RES=(37.062,-121.292)
seasons=[('2024','2024-05-01','2024-09-30','o'),('2025','2025-04-01','2025-08-04','s')]
stats={}
for yr,a,z,mk in seasons:
    for s,(lab,la,lo,km,col) in S.items():
        w=load(s)[a:z]['DO']; d=w.resample('D').agg(['count','mean','min']); d=d[d['count']>=86]
        stats[(yr,s)]=(d['mean'].median(), d['min'].quantile(.10), d['mean'].quantile(.25), d['mean'].quantile(.75))
fig,(axm,axp)=plt.subplots(1,2,figsize=(7.4,3.3),dpi=300,gridspec_kw={'width_ratios':[1,1.35]})
# --- map
axm.grid(False)
order=['11152850','11152870','11152890','11153000']
axm.plot([S[s][2] for s in order[1:]],[S[s][1] for s in order[1:]],color='#c3c2b7',lw=1.2,zorder=1)
axm.plot([S['11152850'][2],RES[1],DAM[1]],[S['11152850'][1],RES[0],DAM[0]],color='#c3c2b7',lw=1.2,ls=':',zorder=1)
axm.scatter([RES[1]],[RES[0]],s=260,marker='o',color='#cde2fb',edgecolor='none',zorder=1); axm.text(RES[1]+0.004,RES[0],'Pacheco\nReservoir',fontsize=6.5,color=MUTED,va='center')
axm.plot([DAM[1]-0.003,DAM[1]+0.003],[DAM[0],DAM[0]],color=INK,lw=2.2,zorder=3); axm.text(DAM[1]-0.004,DAM[0]+0.003,'dam',fontsize=6.5,color=INK,ha='right')
for s,(lab,la,lo,km,col) in S.items():
    axm.scatter([lo],[la],s=46,color=col,edgecolor=SURF,linewidth=0.8,zorder=4)
    off={'11152850':(-0.006,0.0,'right'),'11152870':(0.012,-0.014,'left'),'11152890':(-0.005,-0.002,'right'),'11153000':(0.006,0.0,'left')}[s]
    axm.text(lo+off[0],la+off[1],lab,fontsize=7,color=INK,zorder=5,ha=off[2],va='center')
    if s=='11152870': axm.plot([lo+0.002,lo+0.011],[la-0.003,la-0.012],color=INK,lw=0.5,zorder=4)
for s,(lab,la,lo) in T.items():
    axm.scatter([lo],[la],s=22,color=C['trib'],edgecolor='none',zorder=3); axm.text(lo-0.004 if 'Cedar' in lab else lo+0.003, la+0.004 if 'Cedar' in lab else la+0.007, lab,fontsize=6,color=MUTED,ha='right' if 'Cedar' in lab else 'left')
axm.set_xlim(-121.405,-121.225); axm.set_ylim(36.925,37.105); axm.set_aspect(1/np.cos(np.radians(37.04)))
axm.set_xticks([]); axm.set_yticks([]); 
for sp in axm.spines.values(): sp.set_visible(True); sp.set_color('#c3c2b7')
axm.plot([-121.395,-121.395+0.0225],[36.935,36.935],color=INK,lw=1.5); axm.text(-121.395+0.011,36.939,'2 km',ha='center',fontsize=6.5,color=INK)
axm.text(0.02,0.97,'N ↑',transform=axm.transAxes,fontsize=7,va='top',color=MUTED)

# --- California locator inset
CA=[(-124.2,42.0),(-120.0,42.0),(-120.0,39.0),(-114.6,35.0),(-114.7,32.7),(-117.1,32.5),(-117.3,33.1),(-118.5,34.0),(-119.7,34.4),(-120.6,34.5),(-120.9,35.4),(-121.9,36.3),(-122.0,36.95),(-122.5,37.8),(-123.0,38.3),(-123.7,39.0),(-124.4,40.4),(-124.2,41.0),(-124.2,42.0)]
axi=axm.inset_axes([0.62,0.02,0.36,0.36]); axi.grid(False)
axi.fill([c[0] for c in CA],[c[1] for c in CA],color='#f0efec',edgecolor='#898781',lw=0.6)
axi.plot([-121.29],[37.05],marker='o',color=INK,ms=3); axi.text(-121.0,37.6,'study\narea',fontsize=5.5,color=INK,ha='left',va='bottom')
axi.set_xlim(-125,-114); axi.set_ylim(32,42.5); axi.set_aspect(1/np.cos(np.radians(37))); axi.set_xticks([]); axi.set_yticks([]); axi.set_facecolor(SURF)
for sp in axi.spines.values(): sp.set_visible(False)
axi.text(0.02,0.03,'California',transform=axi.transAxes,fontsize=5.5,color=MUTED)
axm.set_title('Gauge locations (connections schematic)',fontsize=8.5,loc='left',color=INK)
# --- profile
for yr,a,z,mk in seasons:
    off=-0.25 if yr=='2024' else 0.25
    xs=[S[s][3]+off for s in order]; med=[stats[(yr,s)][0] for s in order]; p10=[stats[(yr,s)][1] for s in order]; q1=[stats[(yr,s)][2] for s in order]; q3=[stats[(yr,s)][3] for s in order]
    axp.plot(xs[1:],med[1:],color='#c3c2b7',lw=0.9,ls='-' if yr=='2024' else ':',zorder=1)
    for s,x,m,lo,hi,p in zip(order,xs,med,q1,q3,p10):
        axp.errorbar([x],[m],yerr=[[m-lo],[hi-m]],fmt=mk,color=S[s][4],ms=5.5,capsize=2.5,lw=1.1,zorder=3,alpha=1 if yr=='2024' else 0.6)
        axp.scatter([x],[p],marker='v',color=S[s][4],s=24,zorder=3,alpha=1 if yr=='2024' else 0.6)
axp.axvspan(-6,0,color='#f0efec',zorder=0); axp.text(-5.6,11.3,'upstream of\nreservoir',fontsize=6.5,color=MUTED,va='top')
axp.axvline(0,color=INK,lw=1.2); axp.text(0.3,11.3,'dam',fontsize=7,color=INK,va='top',ha='left')
axp.axhline(7,color=MUTED,lw=0.8,ls='--'); axp.text(13.2,7.1,'7 mg/L',ha='right',va='bottom',color=MUTED,fontsize=7)
axp.axhline(5,color=MUTED,lw=0.8,ls=':'); axp.text(13.2,5.1,'5 mg/L',ha='right',va='bottom',color=MUTED,fontsize=7)
axp.set_xlim(-6,14); axp.set_ylim(0,12); axp.set_xlabel('Channel distance from dam (km, approx.)'); axp.set_ylabel('Dissolved oxygen (mg/L)')
axp.set_xticks([-5,0,3,13]); axp.set_xticklabels(['−5','0','3','13'])
axp.plot([],[],'o',color=INK,label='2024 median daily mean'); axp.plot([],[],'s',color=INK,alpha=0.6,label='2025 median daily mean'); axp.plot([],[],'v',color=INK,label='10th pct. of daily minimum'); axp.plot([],[],'|',color=INK,label='bar = middle half of days')
axp.legend(frameon=False,fontsize=6.3,loc='center',bbox_to_anchor=(0.66,0.17),handlelength=1.2)
axp.set_title('Dissolved oxygen by distance from dam',fontsize=9,loc='left',color=INK)
fig.tight_layout(w_pad=1.5); fig.savefig('paper/figs/fig4_map_profile.png'); print('ok')
