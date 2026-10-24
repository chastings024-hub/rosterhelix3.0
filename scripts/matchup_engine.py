"""Leakage-safe opponent adjustment from historical defensive fantasy points allowed.
CSV: season,week,defense_team,position,points_allowed,league_avg_points
Only games strictly before forecast week are eligible.
"""
import csv, argparse, json, pathlib, statistics
POSITIONS={'QB','RB','WR','TE'}
def matchup_factor(rows, season, week, opponent, position, shrink_games=6):
    eligible=[]
    for r in rows:
        try:
            s,w=int(r['season']),int(r['week'])
            if (s,w)>=(int(season),int(week)) or r['defense_team']!=opponent or r['position']!=position: continue
            pts=float(r['points_allowed']); league=float(r['league_avg_points'])
            if league<=0 or pts<0:continue
            eligible.append((s,w,pts/league))
        except (ValueError,KeyError,TypeError):continue
    eligible.sort(key=lambda x:(x[0],x[1]))
    ratios=[r[2] for r in eligible[-12:]]
    if not ratios:return {'factor':1.0,'games':0,'source':'neutral (insufficient history)'}
    # shrink noisy samples to neutral; cap extremes to avoid exaggerated predictions
    raw=statistics.mean(ratios)
    factor=1+(raw-1)*len(ratios)/(len(ratios)+shrink_games)
    return {'factor':round(max(.8,min(1.2,factor)),4),'games':len(ratios),'source':'historical defensive points allowed; unvalidated'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--season',type=int,required=True);p.add_argument('--week',type=int,required=True);p.add_argument('--output',default='data/matchups.json');a=p.parse_args()
    with open(a.input,newline='',encoding='utf8') as f: rows=list(csv.DictReader(f))
    out={'forecast_season':a.season,'forecast_week':a.week,'note':'Historical matchup adjustments only. Requires supplied verified defense stats and future opponent schedule. No injury/weather model.','teams':{}}
    for team in sorted({r.get('defense_team','') for r in rows if r.get('defense_team')}):
        out['teams'][team]={pos:matchup_factor(rows,a.season,a.week,team,pos) for pos in sorted(POSITIONS)}
    dest=pathlib.Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(out,indent=2)+'\n');print(f'Wrote {dest}')
if __name__=='__main__':main()
