#!/usr/bin/env python3
"""Build defense report for the next unplayed week using past observations only."""
import csv,json,pathlib,datetime,argparse
from matchup_engine import matchup_factor
ROOT=pathlib.Path(__file__).resolve().parents[1]
def report(rows,season,week):
    teams=sorted({r['defense_team'] for r in rows if r.get('defense_team')})
    return {'forecast_season':season,'forecast_week':week,'source':'Derived from nflverse weekly opponent_team + PPR points','note':'Defensive points allowed are observational, not predictive guarantees. No future opponent mapping or injury information.','teams':{t:{p:matchup_factor(rows,season,week,t,p) for p in ('QB','RB','WR','TE')} for t in teams}}
def main():
    p=argparse.ArgumentParser();p.add_argument('--input',default=str(ROOT/'data/defense_allowed.csv'));p.add_argument('--output',default=str(ROOT/'data/matchups.json'));p.add_argument('--season',type=int);p.add_argument('--week',type=int);a=p.parse_args()
    with open(a.input,newline='',encoding='utf8') as f:rows=list(csv.DictReader(f))
    if not rows:raise RuntimeError('Empty defense report')
    season=a.season or max(int(r['season']) for r in rows)
    week=a.week or max(int(r['week']) for r in rows if int(r['season'])==season)+1
    result=report(rows,season,week)
    pathlib.Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print('Wrote',a.output)
if __name__=='__main__':main()
