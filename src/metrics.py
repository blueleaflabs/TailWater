"""TailWater step 1: load 15-min USGS records and compute per-site daily metrics.
load(site) is imported by every other script; running this file writes analysis/daily_metrics.csv.
Times are local standard time (PST, UTC-8, no DST) so the clock tracks the sun, not the calendar."""
import sys, os, pathlib; ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'src')); os.chdir(ROOT)  # run from any cwd
import pandas as pd, numpy as np, glob, os
names={'00300':'DO','00010':'T','00060':'Q','00095':'SC'}
LABEL={'11152850':'NF Pacheco ABOVE res','11152870':'NF Pacheco BELOW res','11152880':'SF Pacheco',
 '11152900':'Cedar Ck','11152890':'Pacheco @ Bell Stn','11153000':'Pacheco nr Dunneville','11173200':'Arroyo Hondo'}
# USGS qualifiers. Values flagged DRY were recorded with the sensor out of water and are excluded.
# ZEROFLOW (standing pool, no discharge) and ESTIMATED (discharge only) are retained; LESSTHAN values
# are kept at the reporting limit. See data/DATA.md.
EXCLUDE_QUALIFIERS = ('DRY',)
def load(site):
    """15-min DataFrame (columns DO, T, Q, SC as available) indexed in PST (UTC-8, no daylight saving)."""
    fs=sorted(glob.glob(f'data/USGS-{site}*.csv'))
    df=pd.concat([pd.read_csv(f,dtype={'parameter_code':str,'qualifiers':str},low_memory=False) for f in fs])
    bad=df.qualifiers.fillna('').apply(lambda q: any(x in q for x in EXCLUDE_QUALIFIERS)); df=df[~bad]
    df['t']=pd.to_datetime(df.time_utc,utc=True).dt.tz_convert('Etc/GMT+8').dt.tz_localize(None)
    df['p']=df.parameter_code.map(names); df['value']=pd.to_numeric(df.value,errors='coerce')
    w=df.pivot_table(index='t',columns='p',values='value',aggfunc='mean').sort_index()
    return w.resample('15min').mean()
def main():
    """Write analysis/daily_metrics.csv: one row per site-day with >=86 of 96 DO readings."""
    rows=[]
    for site,label in LABEL.items():
        w=load(site)
        for day,g in w.groupby(w.index.normalize()):
            do=g['DO'].dropna()
            if len(do)<86: continue           # qualifying day: >=86 of 96 slots (89.6%)
            hrs=(do.index-day).total_seconds()/3600
            r=dict(site=site,label=label,date=day,n=len(do),
                   do_min=do.min(),do_max=do.max(),do_mean=do.mean(),
                   t_min=hrs[do.values.argmin()],t_max=hrs[do.values.argmax()])
            r['amp']=r['do_max']-r['do_min']
            for thr in (7,5):
                below=do<thr
                r[f'h_below{thr}']=below.sum()*0.25
                if below.any():
                    r[f'start{thr}']=hrs[np.argmax(below.values)]
                    r[f'end{thr}']=hrs[len(below)-1-np.argmax(below.values[::-1])]
            if 'T' in g:
                T=g['T'].dropna()
                if len(T)>80:
                    r['T_max']=T.max(); r['T_min']=T.min(); r['T_mean']=T.mean()
                    r['tT_max']=((T.index-day).total_seconds()/3600)[T.values.argmax()]
            if 'Q' in g and g['Q'].notna().sum()>80: r['Q_mean']=g['Q'].mean()
            rows.append(r)
    d=pd.DataFrame(rows); d.to_csv('analysis/daily_metrics.csv',index=False)
    print(d.groupby('label').size())

if __name__ == '__main__':
    main()
