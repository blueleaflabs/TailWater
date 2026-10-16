"""TailWater: nightly DO minima on a noon-to-noon window.

A pre-dawn minimum belongs to one night, but a midnight-to-midnight day splits it across two.
This script groups readings from noon of day D to noon of day D+1, labels the row by the morning
date D+1, and records the minimum, its clock hour, the range, hours below 7 and 5 mg/L, and the
previous calendar day's temperature and discharge. Writes analysis/night_metrics.csv.
"""
import sys, os, pathlib; ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'src')); os.chdir(ROOT)  # run from any cwd
import pandas as pd, numpy as np
from metrics import load, LABEL
def main():
    rows=[]
    for site,label in LABEL.items():
        w=load(site)
        if 'DO' not in w: continue
        do=w['DO']
        # night-centred window: noon D -> noon D+1, labelled by the morning date D+1
        shifted=do.copy(); shifted.index=shifted.index-pd.Timedelta(hours=12)
        for day,g in shifted.groupby(shifted.index.normalize()):
            g=g.dropna()
            if len(g)<86: continue
            hrs=(g.index-day).total_seconds()/3600+12   # hours after noon D as clock hours (12..36)
            morning=day+pd.Timedelta(days=1)
            r=dict(site=site,label=label,date=morning,do_min=g.min(),t_min=hrs[g.values.argmin()]%24,
                   do_max=g.max(),t_max=hrs[g.values.argmax()]%24,amp=g.max()-g.min())
            for thr in (7,5):
                b=g<thr; r[f'h_below{thr}']=b.sum()*0.25
                if b.any() and not b.all():
                    r[f'start{thr}']=hrs[np.argmax(b.values)]%24
                    r[f'end{thr}']=hrs[len(b)-1-np.argmax(b.values[::-1])]%24
            # previous-day drivers (calendar day D)
            dd=w.loc[day:day+pd.Timedelta(hours=23,minutes=59)]
            if 'T' in dd and dd['T'].notna().sum()>80: r['T_max_prev']=dd['T'].max(); r['T_min_prev']=dd['T'].min()
            if 'Q' in dd and dd['Q'].notna().sum()>80: r['Q_prev']=dd['Q'].mean()
            rows.append(r)
    pd.DataFrame(rows).to_csv('analysis/night_metrics.csv', index=False)

if __name__ == '__main__':
    main()
