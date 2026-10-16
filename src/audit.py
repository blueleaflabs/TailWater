"""TailWater: regenerate every quantitative statement in the Note and the explainer.

Reads the frozen 15-minute records in data/ through metrics.load() and writes analysis/AUDIT.md.
Sections mirror the papers: data counts, April-October assessment window, Table 1
(station-comparison windows), matched days, low-oxygen episodes, downstream recovery,
flow context, temperature signature, and the EIR habitat-model shares (typed from Table 7-1).
If a number in the papers does not match this file, the papers are wrong.

    python3 src/audit.py
"""
import sys, os, pathlib; ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'src')); os.chdir(ROOT)  # run from any cwd
import pandas as pd, numpy as np, glob
from metrics import load, LABEL, EXCLUDE_QUALIFIERS
def dosat(T):
    Tk=T+273.15; return np.exp(-139.34411+1.575701e5/Tk-6.642308e7/Tk**2+1.243800e10/Tk**3-8.621949e11/Tk**4)
out=[]; P=lambda *a: out.append(' '.join(str(x) for x in a))
A=load('11152850'); B=load('11152870'); S=load('11152890'); D=load('11153000'); CED=load('11152900')
P("# Audit of quantitative claims — regenerated", pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'), "\n")
P("## Data section"); 
raw=pd.concat([pd.read_csv(f,dtype=str) for f in glob.glob('data/USGS-11152870*.csv')]); do_raw=raw[raw.parameter_code=='00300']
P("- below-dam DO rows in file (incl. valueless placeholders):", len(do_raw), "| Approved:", (do_raw.approval=='Approved').sum(), "| LESSTHAN flags:", do_raw.qualifiers.fillna('').str.contains('LESSTHAN').sum(), "| DISCONTINUED flags:", do_raw.qualifiers.fillna('').str.contains('DISCONTINUED').sum(), "| last row timestamp (placeholder):", do_raw.time_utc.max()[:10])
appr=do_raw[(do_raw.time_utc>='2024-04-01')&(do_raw.time_utc<'2025-10-01')]; P("- Apr 2024–Sep 2025 approved share:", f"{100*(appr.approval=='Approved').mean():.1f}%")
val=do_raw[do_raw.value.notna()]; ph=do_raw[do_raw.value.isna()]
P("- below-dam DO rows WITH a value:", len(val), "| all Approved:", bool((val.approval=='Approved').all()), "| first:", val.time_utc.min()[:16], "| last:", val.time_utc.max()[:16])
P("- below-dam placeholder rows (no value):", len(ph), "| qualifiers:", sorted(ph.qualifiers.fillna('').unique()), "| span:", ph.time_utc.min()[:10], "..", ph.time_utc.max()[:10])
tot=0
for s in ['11152850','11152870','11152880','11152890','11152900','11153000','11173200']:
    n=sum(len(pd.read_csv(f,dtype=str).query("parameter_code=='00300'")) for f in glob.glob(f'data/USGS-{s}*.csv')); tot+=n
P("- total DO readings across 7 Pacheco gauges (incl. Arroyo Hondo):", tot)
P("\n## Qualifiers and record ends (numeric DO values, raw files)")
for s_ in ['11152850','11152870','11152880','11152890','11152900','11153000']:
    r_=pd.concat([pd.read_csv(f,dtype=str) for f in glob.glob(f'data/USGS-{s_}*.csv')]); r_=r_[(r_.parameter_code=='00300')&r_.value.notna()]
    q_=r_.qualifiers.fillna('[]').value_counts().to_dict(); t_=pd.to_datetime(r_.time_utc,utc=True).dt.tz_convert('Etc/GMT+8')
    P(f"- {s_}: n={len(r_)}; qualifiers {q_}; approved {100*(r_.approval=='Approved').mean():.1f}%; first {t_.min():%Y-%m-%d %H:%M}; last {t_.max():%Y-%m-%d %H:%M} PST")
P("- loader excludes qualifiers:", EXCLUDE_QUALIFIERS, "(DRY = sensor out of water); ZEROFLOW/ESTIMATED retained; LESSTHAN kept at reporting limit")
cov=[]
for lab_,w_ in [('above',A),('below',B),('bell',S),('dunneville',D)]:
    c_=w_['DO'].dropna().resample('MS').count(); 
    for m_,n_ in c_.items(): cov.append(dict(site=lab_,month=f"{m_:%Y-%m}",readings=int(n_),possible=m_.days_in_month*96,coverage_pct=round(100*n_/(m_.days_in_month*96),1)))
pd.DataFrame(cov).to_csv('analysis/monthly_coverage.csv',index=False); P("- monthly DO coverage per gauge written to analysis/monthly_coverage.csv")
P("\n## Abstract / headline window (below dam, 1 Apr–31 Oct)")
for yr in (2024,2025):
    g=B[f'{yr}-04-01':f'{yr}-10-31 23:59']['DO'].dropna(); poss=len(pd.date_range(f'{yr}-04-01',f'{yr}-11-01',freq='15min'))-1
    P(f"- {yr}: n={len(g)} of {poss} ({100*len(g)/poss:.1f}%); <7 {100*(g<7).mean():.1f}%; <5 {100*(g<5).mean():.1f}%; <3 {100*(g<3).mean():.1f}%; <1 {100*(g<1).mean():.1f}%; <=0.1 {100*(g<=0.1).mean():.1f}%; median {g.median():.2f}")
g=B['2025-06-01':'2025-06-30 23:59']['DO'].dropna(); P(f"- June 2025 at reporting limit (<=0.1): {100*(g<=0.1).mean():.1f}% of {len(g)}; daily range median {B.loc['2025-06','DO'].resample('D').agg(lambda x:x.max()-x.min()).median():.2f}")
P("\n## Table 1 (release-season windows)")
for lab,w,a,z in [('Above 2024',A,'2024-05-01','2024-09-30'),('Above 2025',A,'2025-04-01','2025-08-04'),('Below 2024',B,'2024-05-01','2024-09-30'),('Below 2025',B,'2025-04-01','2025-08-04'),('Bell 2024',S,'2024-05-01','2024-09-30'),('Bell 2025',S,'2025-04-01','2025-08-04'),('Dunneville 2024',D,'2024-05-01','2024-09-30'),('Dunneville 2025',D,'2025-04-01','2025-08-04')]:
    ww=w[a:z+' 23:59']; d=ww['DO'].resample('D').agg(['count','mean','min','max']); d=d[d['count']>=86]
    g=ww['DO'].dropna(); g=g[g.index.normalize().isin(d.index)]                      # observed readings on qualifying days
    T=ww['T'].dropna(); T=T[T.index.normalize().isin(d.index)]
    Td=T.resample('D').agg(['count','mean']); Td=Td[Td['count']>=80]['mean']           # daily mean T on days with >=80 T readings
    inst=100*(g/dosat(T.reindex(g.index))).dropna(); satd=inst.resample('D').mean().dropna()   # daily mean of instantaneous % saturation
    allg=ww['DO'].dropna()
    P(f"- {lab}: days {len(d)}; median daily mean {d['mean'].median():.1f}; median daily min {d['min'].median():.1f}; median range {(d['max']-d['min']).median():.1f}; <7 {100*(g<7).mean():.0f}%; <5 {100*(g<5).mean():.0f}%; <3 {100*(g<3).mean():.0f}%; %sat (median of daily means, {len(satd)} d) {satd.median():.0f}; T (median of daily means, {len(Td)} d) {Td.median():.1f}")
    P(f"    all observed readings in window incl. non-qualifying days: n={len(allg)}; <7 {100*(allg<7).mean():.1f}%; <5 {100*(allg<5).mean():.1f}%; count <5 = {(allg<5).sum()}; min {allg.min():.1f}")
P("\n## Table 2 (matched days)")
for yr in (2024,2025):
    a=A.loc[str(yr),'DO'].resample('D').agg(['count','mean','min']); b=B.loc[str(yr),'DO'].resample('D').agg(['count','mean','min'])
    aT=A.loc[str(yr),'T'].resample('D').mean(); bT=B.loc[str(yr),'T'].resample('D').mean()
    c=a[a['count']>=86].index.intersection(b[b['count']>=86].index); c=c[(c.month>=4)&(c.month<=10)]
    diff=a.loc[c,'mean']-b.loc[c,'mean']
    P(f"- {yr}: {len(c)} days {c.min().date()}..{c.max().date()}; mean DO {a.loc[c,'mean'].median():.1f}/{b.loc[c,'mean'].median():.1f}; diff median {diff.median():.1f} IQR {diff.quantile(.25):.1f}-{diff.quantile(.75):.1f}; below<above {(b.loc[c,'mean']<a.loc[c,'mean']).sum()}/{len(c)}; min DO {a.loc[c,'min'].median():.1f}/{b.loc[c,'min'].median():.1f}; T {aT.reindex(c).median():.1f}/{bT.reindex(c).median():.1f}; T diff {(aT.reindex(c)-bT.reindex(c)).median():.1f}")
    ab=pd.concat([A.loc[str(yr),'DO'].rename('a'),B.loc[str(yr),'DO'].rename('b')],axis=1).dropna(); ab=ab[ab.index.normalize().isin(c)]
    P(f"  common 15-min n={len(ab)}: <7 {100*(ab.a<7).mean():.0f}%/{100*(ab.b<7).mean():.0f}%; <5 {100*(ab.a<5).mean():.0f}%/{100*(ab.b<5).mean():.0f}%; <3 {100*(ab.a<3).mean():.0f}%/{100*(ab.b<3).mean():.0f}%")
P("\n## Figure 2 / Result 2 (monthly share >=5 mg/L, below dam)")
m=B['DO'].resample('MS').agg(lambda x: 100*(x.dropna()>=5).mean() if x.notna().sum()>=500 else np.nan).round(0)   # observed-reading denominator; >=500 rule as in Figure 3
P("- " + ", ".join(f"{k:%b %y}:{v:.0f}" for k,v in m['2024-03':'2025-09'].items()))
mm=B['DO'].resample('MS').median(); P(f"- monthly median DO Aug 2024 {mm['2024-08-01']:.1f}, Jul 2025 {mm['2025-07-01']:.1f}, Jun–Jul 2024 {mm['2024-06-01']:.1f}/{mm['2024-07-01']:.1f}, May–Jun 2025 {mm['2025-05-01']:.1f}/{mm['2025-06-01']:.1f}")
P("\n## Episodes (below dam)")
do=B['DO'].dropna()
def eps(thr,maxgap):
    runs=[]; start=None; prev=None
    for t,v in do.items():
        below=v<thr
        if start is not None and ((not below) or (t-prev)>maxgap): runs.append((start,prev)); start=None
        if below and start is None: start=t
        prev=t
    if start is not None: runs.append((start,prev))
    return sorted([(s,e,(e-s).total_seconds()/86400) for s,e in runs],key=lambda r:-r[2])
for thr in (3,1):
    L=eps(thr,pd.Timedelta(hours=1)); St=eps(thr,pd.Timedelta(minutes=15))
    for s,e,d in L[:2]:
        seg=do[s:e]; exp=int((e-s)/pd.Timedelta(minutes=15))+1; gaps=seg.index.to_series().diff().dropna()
        P(f"- <{thr}: {s:%Y-%m-%d %H:%M}..{e:%Y-%m-%d %H:%M} {d:.1f} d; readings {len(seg)}/{exp}; max gap {gaps.max()}; max DO {seg.max()}")
    P(f"  strict longest: {St[0][2]:.1f} d ({St[0][0]:%Y-%m-%d}..{St[0][1]:%Y-%m-%d}); sum of episode spans <{thr}: {sum(r[2] for r in L):.1f} d; observation-days <{thr} (readings/96): {(do<thr).sum()/96:.1f}")
P("\n## Result 3 / reaeration")
b=B['DO'].resample('D').mean(); bT=B['T'].resample('D').mean(); s=S['DO'].resample('D').mean(); sT=S['T'].resample('D').mean()
df=pd.DataFrame({'DOb':b,'Tb':bT,'DOs':s,'Ts':sT})['2024-06-01':'2024-08-31'].dropna(); df['D0']=dosat(df.Tb)-df.DOb; df['D1']=dosat(df.Ts)-df.DOs; df=df[(df.D0>0.5)&(df.D1>0.05)]
r=np.log(df.D0/df.D1); P(f"- n={len(df)} days; D0 median {df.D0.median():.1f}; D1 median {df.D1.median():.1f}; ln ratio median {r.median():.2f}; k2 at 0.2/0.4 m/s over 3 km: {r.median()/(3000/0.2/86400):.0f}/{r.median()/(3000/0.4/86400):.0f} per day")
sb=S['2024-05-01':'2024-09-30']['DO'].dropna(); P(f"- Bell Station 2024 release season: <7 {100*(sb<7).mean():.0f}%; <5 {100*(sb<5).mean():.1f}%")
db=D['2024-05-01':'2024-09-30']['DO'].dropna(); P(f"- Dunneville 2024: <7 {100*(db<7).mean():.0f}%; <5 {100*(db<5).mean():.0f}%; median daily range {D['2024-05-01':'2024-09-30']['DO'].resample('D').agg(lambda x:x.max()-x.min()).median():.1f}")
P("\n## Release inference / flows")
q=D['Q'].resample('MS').median(); c=CED['Q'].resample('MS').agg(['median','max'])
P(f"- Dunneville Q median: Apr 2024 {q['2024-04-01']:.1f}; Aug 2024 {q['2024-08-01']:.1f}; Jul 2025 {q['2025-07-01']:.1f}; Feb 2025 peak {D['Q']['2025-02'].max():.0f}")
P(f"- Cedar Ck Q Aug 2024 median/max {c.loc['2024-08-01','median']:.2f}/{c.loc['2024-08-01','max']:.2f}; Jul 2025 {c.loc['2025-07-01','median']:.2f}/{c.loc['2025-07-01','max']:.2f}")
wk=D['Q']['2024-06-01':'2024-07-07'].resample('W').median(); P(f"- Dunneville weekly median Q early June → end June 2024: {wk.iloc[0]:.1f} → {wk.iloc[-2]:.2f}")
P("\n## Temperature signature (below dam monthly median daily T range)")
r=B['T'].resample('D').agg(lambda x: x.max()-x.min() if x.notna().sum()>80 else None).dropna().resample('MS').median().round(2)
P("- " + ", ".join(f"{k:%b %y}:{v}" for k,v in r['2024-03':'2025-09'].items()))
for yr,a,z in [(2024,'2024-05-01','2024-09-30'),(2025,'2025-04-01','2025-08-04')]:
    P(f"- summer Tmax below dam {yr}: median daily max {B[a:z]['T'].resample('D').max().median():.1f}; above reservoir {A[a:z]['T'].resample('D').max().median():.1f}; Cedar {CED[a:z]['T'].resample('D').max().median():.1f}")
P("\n## EIR Table 7-1 (DEIR Modeling Appendix p. 7-6; an EXAMPLE calculation for one month, typed values; not a habitat allocation)")
v=[1848,1819,1495,1445,1440,1235,999,922,930]; P(f"- temp-adjusted WUA sum {sum(v)}; top two {v[0]+v[1]} = {100*(v[0]+v[1])/sum(v):.0f}%; top one {100*v[0]/sum(v):.0f}%")
open('analysis/AUDIT.md','w').write('\n'.join(out)); print('\n'.join(out))
