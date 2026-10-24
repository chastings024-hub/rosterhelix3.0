#!/usr/bin/env python3
"""Derive weekly defense-vs-position points allowed from canonical player game logs.
Only meaningful if opponent_team is populated by the source. No fabricated schedule.
"""
import csv, json, argparse, pathlib, collections, datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
def build(rows):
    sums=collections.defaultdict(float)
    for r in rows:
        try:
            opponent=(r.get('opponent_team') or '').strip().upper()
            pos=r.get('position')
            if not opponent or pos not in {'QB','RB','WR','TE'}:continue
            season,week=int(r['season']),int(r['week'])
            if not 1<=week<=22:continue
            key=(season,week,opponent,pos)
            sums[key]+=float(r['fantasy_points_ppr'])
        except (ValueError,TypeError,KeyError):continue
    averages=collections.defaultdict(list)
    for (season,week,defense,pos),pts in sums.items():averages[(season,week,pos)].append(pts)
    out=[]
    for (season,week,defense,pos),pts in sorted(sums.items()):
        pool=averages[(season,week,pos)]
        # Weekly average across observed defensive opponents; do not treat missing data as zero.
        avg=sum(pool)/len(pool)
        if avg<=0:continue
        out.append({'season':season,'week':week,'defense_team':defense,'position':pos,'points_allowed':round(pts,3),'league_avg_points':round(avg,3)})
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',default=str(ROOT/'data/player_stats.csv'));p.add_argument('--output',default=str(ROOT/'data/defense_allowed.csv'));a=p.parse_args()
    with open(a.input,newline='',encoding='utf8') as f:rows=list(csv.DictReader(f))
    out=build(rows)
    if not out:raise RuntimeError('No opponent_team data; cannot calculate defense metrics. Existing data left unchanged.')
    dest=pathlib.Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True)
    import io,os,tempfile
    with tempfile.NamedTemporaryFile('w',encoding='utf8',newline='',dir=dest.parent,delete=False) as f:
        writer=csv.DictWriter(f,fieldnames=['season','week','defense_team','position','points_allowed','league_avg_points']);writer.writeheader();writer.writerows(out);tmp=f.name
    os.replace(tmp,dest);print(f'Wrote {len(out)} observed defense-position weeks to {dest}')
if __name__=='__main__':main()
