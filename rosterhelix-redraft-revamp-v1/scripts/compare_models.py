"""Leakage-safe, paired historical baseline vs defensive-matchup comparison."""
import argparse,collections,csv,json,math,statistics
from pathlib import Path
from backtest import estimate,points
from history_store import read_rows
from matchup_engine import matchup_factor

def metrics(errors):
 if not errors:return {'n':0,'mae':None,'rmse':None,'bias':None}
 return {'n':len(errors),'mae':round(statistics.mean(map(abs,errors)),3),'rmse':round(math.sqrt(statistics.mean(x*x for x in errors)),3),'bias':round(statistics.mean(errors),3)}

def compare(rows,scoring=1,min_history=2):
 """Only earlier games enter either player history or defensive context."""
 ordered=sorted((r for r in rows if r.get('position') in ('QB','RB','WR','TE')),key=lambda r:(int(r['season']),int(r['week']),r.get('player_id','')))
 player_history=collections.defaultdict(list)
 defense_rows=[];baseline_errors=[];adjusted_errors=[];by_pos=collections.defaultdict(lambda:[[],[]]);samples=[]
 weeks=collections.defaultdict(list)
 for r in ordered:weeks[(int(r['season']),int(r['week']))].append(r)
 for (season,week),games in sorted(weeks.items()):
  for r in games:
   pid=r.get('player_id') or r.get('player_name');pos=r['position'];hist=player_history[(season,pid)]
   actual=points(r,scoring);base=estimate(hist,pos,scoring) if len(hist)>=min_history else None
   opponent=(r.get('opponent_team') or '').strip().upper()
   if base is not None and actual is not None and opponent:
    m=matchup_factor(defense_rows,season,week,opponent,pos)
    adjusted=base*m['factor'];e0=base-actual;e1=adjusted-actual
    baseline_errors.append(e0);adjusted_errors.append(e1);by_pos[pos][0].append(e0);by_pos[pos][1].append(e1)
    samples.append({'season':season,'week':week,'player_id':pid,'position':pos,'opponent':opponent,'actual':round(actual,2),'baseline':round(base,2),'adjusted':round(adjusted,2),'defense_games':m['games']})
  # Commit entire week only AFTER predicting all games in that week.
  totals=collections.defaultdict(float)
  for r in games:
   player_history[(season,r.get('player_id') or r.get('player_name'))].append(r)
   opp=(r.get('opponent_team') or '').strip().upper()
   p=points(r,scoring)
   if opp and p is not None:totals[(opp,r['position'])]+=p
  league=collections.defaultdict(list)
  for (opp,pos),total in totals.items():league[pos].append(total)
  for (opp,pos),total in totals.items():
   avg=statistics.mean(league[pos]);
   if avg>0:defense_rows.append({'season':season,'week':week,'defense_team':opp,'position':pos,'points_allowed':total,'league_avg_points':avg})
 b=metrics(baseline_errors);a=metrics(adjusted_errors)
 return {'source':'locally imported history; source authenticity not independently verified','evaluation':'paired walk-forward; both models evaluated on identical player-games; no current/future-week data used','scoring':scoring,'baseline':b,'matchup_adjusted':a,'mae_improvement':round(b['mae']-a['mae'],3) if b['n'] else None,'by_position':{k:{'baseline':metrics(v[0]),'matchup_adjusted':metrics(v[1])} for k,v in sorted(by_pos.items())},'defense_adjusted_games':sum(x['defense_games']>0 for x in samples),'sample_predictions':samples[:100]}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input');p.add_argument('--output',default='data/model_comparison.json');p.add_argument('--scoring',choices=['ppr','half','standard'],default='ppr');a=p.parse_args()
 if a.input:
  with open(a.input,encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
 else:rows=read_rows()
 report=compare(rows,{'ppr':1,'half':.5,'standard':0}[a.scoring]);dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='sample_predictions'},indent=2))
