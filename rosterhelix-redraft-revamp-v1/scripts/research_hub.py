"""Player trends and transparent, historical-only lineup insights."""
from collections import defaultdict
from statistics import mean,pstdev

def profiles(rows,season=None):
 if not rows:return []
 if season is None:season=max(int(r['season']) for r in rows)
 groups=defaultdict(list)
 for r in rows:
  try:
   if int(r['season'])!=season or r.get('position') not in ('QB','RB','WR','TE'):continue
   w=int(r['week']);pts=float(r['fantasy_points_ppr'])
   if not 1<=w<=18 or not -100<=pts<=150:continue
  except (ValueError,TypeError,KeyError):continue
  pid=r.get('player_id')
  if pid:groups[pid].append((w,pts,r))
 out=[]
 for pid,games in groups.items():
  games.sort(key=lambda x:x[0]);latest=games[-1][2]
  pts=[x[1] for x in games];recent=pts[-5:]
  def avg_field(key):
   nums=[]
   for _,_,r in games[-5:]:
    try:
     if r.get(key) not in (None,''):nums.append(float(r[key]))
    except (TypeError,ValueError):pass
   return round(mean(nums),1) if nums else None
  out.append({'id':pid,'name':latest.get('player_name',''),'position':latest['position'],
   'team':latest.get('recent_team',''),'season':season,'games':len(games),
   'season_ppg':round(mean(pts),2),'recent_ppg':round(mean(recent),2),
   'volatility':round(pstdev(pts),2),'targets_pg':avg_field('receiving_targets'),
   'carries_pg':avg_field('rushing_attempts'),
   'logs':[{'week':w,'points':round(pt,2),'opponent':r.get('opponent_team','')} for w,pt,r in games]})
 return sorted(out,key=lambda r:(-r['recent_ppg'],r['name']))

def insights(rows,roster,season=None):
 all_players=profiles(rows,season)
 by_id={p['id']:p for p in all_players}
 team=[];missing=[]
 for pl in roster['players']:
  found=by_id.get(pl['id'])
  if found:team.append(found)
  else:missing.append(pl['name'])
 # Greedy lineup selection based on recorded recent averages; never claims a forecast.
 chosen=[];remaining=sorted(team,key=lambda x:-x['recent_ppg'])
 for pos in ('QB','RB','WR','TE'):
  for pl in [x for x in remaining if x['position']==pos][:roster['slots'][pos]]:
   chosen.append({'slot':pos,**pl});remaining.remove(pl)
 for pl in [x for x in remaining if x['position'] in ('RB','WR','TE')][:roster['slots']['FLEX']]:
  chosen.append({'slot':'FLEX',**pl});remaining.remove(pl)
 required=sum(roster['slots'].values())
 return {'season':season or (max((p['season'] for p in all_players),default=None)),
  'starters':chosen,'bench':remaining,'missing':missing,'filled_slots':len(chosen),'required_slots':required,
  'roster_size':len(roster['players']),'data_players':len(all_players),
  'warning':'Historical recent PPR points per game only. Not injury-aware, schedule-aware, or a validated lineup recommendation. K/DST not scored.'}
