"""Schedule-aware player baselines, with cautious historical defense adjustments."""
import csv,statistics
from pathlib import Path
from matchup_engine import matchup_factor

def upcoming_opponent(schedule,season,week,team):
 for g in schedule:
  if int(g['season'])!=season or int(g['week'])!=week:continue
  if g['home_team']==team:return g['away_team']
  if g['away_team']==team:return g['home_team']
 return None

def project(rows,schedule,defense,season,week,scoring='ppr'):
 if scoring not in ('ppr','half','standard') or not 1<=week<=18:raise ValueError('Invalid scoring or week')
 by={}
 for r in rows:
  if int(r['season'])==season and int(r['week'])<week:by.setdefault(r['player_id'],[]).append(r)
 output=[]
 for pid,games in by.items():
  recent=sorted(games,key=lambda r:int(r['week']))[-5:];last=recent[-1]
  pts=[]
  for g in recent:
   ppr=float(g.get('fantasy_points_ppr') or 0);rec=float(g.get('receptions') or 0)
   pts.append(ppr-rec*(1 if scoring=='standard' else .5 if scoring=='half' else 0))
  weights=range(1,len(pts)+1);base=sum(x*w for x,w in zip(pts,weights))/sum(weights)
  team=last['recent_team'];opponent=upcoming_opponent(schedule,season,week,team)
  factor=1.;n=0
  if opponent and defense:
   m=matchup_factor(defense,season,week,opponent,last['position'])
   factor=float(m.get('factor',1));n=int(m.get('games',0)) if m.get('games') is not None else 0
  output.append({'id':pid,'name':last['player_name'],'team':team,'position':last['position'],'opponent':opponent,'bye':opponent is None and bool(schedule),'baseline':round(base,2),'projection':round(base*factor,2) if opponent or not schedule else None,'matchup_factor':round(factor,3),'matchup_adjusted':bool(opponent and n>0),'defense_sample_games':n,'sample_games':len(pts),'stddev':round(statistics.pstdev(pts),2) if len(pts)>1 else None,'week':week,'model':'weighted-five-game-plus-shrunk-defense' if opponent and n>0 else 'weighted-five-game-baseline'})
 return sorted(output,key=lambda r:-(r['projection'] if r['projection'] is not None else -999))
