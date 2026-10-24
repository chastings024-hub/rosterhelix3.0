"""Explainable, retrospective fantasy decision support. No live injury or schedule claims."""
from collections import defaultdict
from statistics import mean,pstdev
import math
POSITIONS=('QB','RB','WR','TE')

def _num(row,key):
 try:
  value=row.get(key)
  return float(value) if value not in ('',None) and math.isfinite(float(value)) else None
 except (TypeError,ValueError,OverflowError):return None

def _round(x):return round(x,2)

def player_cards(rows,season=None,through_week=None,scoring='ppr',window=5):
 if scoring not in ('ppr','half','standard'):raise ValueError('Invalid scoring')
 if not 1<=window<=12:raise ValueError('Window must be 1–12')
 years=[]
 for r in rows:
  try:years.append(int(r['season']))
  except (ValueError,TypeError,KeyError):pass
 if not years:return {'season':season,'players':[],'replacement':{},'warning':'No imported historical games'}
 if season is None:season=max(years)
 grouped=defaultdict(list)
 for r in rows:
  try:
   if int(r['season'])!=season or r.get('position') not in POSITIONS:continue
   week=int(r['week']);ppr=_num(r,'fantasy_points_ppr')
   if not 1<=week<=18 or (through_week is not None and week>=through_week) or ppr is None or not -100<=ppr<=150:continue
   pid=str(r.get('player_id') or '').strip()
   if not pid:continue
   rec=_num(r,'receptions')
   pts=ppr-(1 if scoring=='standard' else .5 if scoring=='half' else 0)*(rec or 0)
   grouped[pid].append((week,pts,r))
  except (ValueError,TypeError,KeyError):continue
 players=[]
 for pid,games in grouped.items():
  games.sort(key=lambda g:g[0]);games=games[-18:];recent=games[-window:];latest=games[-1][2]
  vals=[g[1] for g in games];rv=[g[1] for g in recent]
  def avg_field(field):
   a=[v for _,_,r in recent if (v:=_num(r,field)) is not None]
   return _round(mean(a)) if a else None
  season_avg=mean(vals);recent_avg=mean(rv);sample=len(games)
  blend=min(.65,len(recent)/(len(recent)+4))
  center=(1-blend)*season_avg+blend*recent_avg
  volatility=pstdev(vals) if len(vals)>1 else 0
  # Lower certainty for limited samples; uncertainty is descriptive, not calibrated probability.
  confidence='low' if sample<4 else 'moderate' if sample<8 else 'historical sample'
  players.append({'id':pid,'name':latest.get('player_name',''),'position':latest['position'],'team':latest.get('recent_team',''),
   'games':sample,'last_week':games[-1][0],'season_ppg':_round(season_avg),'recent_ppg':_round(recent_avg),
   'estimate':_round(center),'volatility':_round(volatility),'targets_pg':avg_field('receiving_targets'),
   'carries_pg':avg_field('rushing_attempts'),'receptions_pg':avg_field('receptions'),
   'trend':_round(recent_avg-season_avg),'confidence':confidence,
   'floor_observed':_round(min(vals)),'ceiling_observed':_round(max(vals)),
   'median_ppg':_round(__import__('statistics').median(vals)),
   'boom_rate':_round(sum(v>=({'QB':20,'RB':15,'WR':15,'TE':10}[latest['position']]) for v in vals)/sample*100),
   'bust_rate':_round(sum(v<({'QB':12,'RB':8,'WR':8,'TE':5}[latest['position']]) for v in vals)/sample*100),
   'p25':_round(sorted(vals)[max(0,math.ceil(.25*sample)-1)]),
   'p75':_round(sorted(vals)[max(0,math.ceil(.75*sample)-1)]),
   'opportunities_pg':_round((avg_field('receiving_targets') or 0)+(avg_field('rushing_attempts') or 0)) if avg_field('receiving_targets') is not None or avg_field('rushing_attempts') is not None else None,
   'targets_season_pg':_round(mean([v for _,_,r in games if (v:=_num(r,'receiving_targets')) is not None])) if any(_num(r,'receiving_targets') is not None for _,_,r in games) else None,
   'carries_season_pg':_round(mean([v for _,_,r in games if (v:=_num(r,'rushing_attempts')) is not None])) if any(_num(r,'rushing_attempts') is not None for _,_,r in games) else None})
 replacement={}
 for pos in POSITIONS:
  pool=sorted((p['estimate'] for p in players if p['position']==pos),reverse=True)
  # 12-team league approximations; only use as an explicit heuristic, not market trade values.
  rank={'QB':13,'RB':31,'WR':37,'TE':13}[pos]
  replacement[pos]=_round(pool[min(rank-1,len(pool)-1)]) if pool else 0
 for p in players:p['above_replacement']=_round(p['estimate']-replacement[p['position']])
 return {'season':season,'scoring':scoring,'through_week':through_week,'players':sorted(players,key=lambda x:-x['estimate']),
  'replacement':replacement,'warning':'Retrospective statistical estimates, NOT verified upcoming projections. No live injuries, bye weeks, snap shares, routes, weather, or confirmed opponents. Missing receptions cause half/standard scoring to be approximate.'}

def _matchup(rows,season,week,position,opponent):
 """Shrink position-level historical points allowed toward league mean.

 The defense sample contains games before the target week, never the target game.
 """
 if not opponent:return {'factor':1.0,'games':0,'label':'No opponent selected'}
 opp=opponent.strip().upper()
 if not (2<=len(opp)<=4 and opp.isalpha()):raise ValueError('Invalid opponent abbreviation')
 # Each team's defensive total must be aggregated per week, rather than
 # weighting games by the number of offensive players recorded.
 totals=defaultdict(float)
 for r in rows:
  try:
   if int(r['season'])!=season or r.get('position')!=position:continue
   w=int(r['week'])
   if week is not None and w>=week:continue
   pts=_num(r,'fantasy_points_ppr')
   if pts is None or not -100<=pts<=150:continue
   defense=(r.get('opponent_team') or '').upper().strip()
   if defense:totals[(w,defense)]+=pts
  except (KeyError,ValueError,TypeError):continue
 chosen=[v for (w,d),v in totals.items() if d==opp]
 overall=list(totals.values())
 if len(chosen)<4 or len(overall)<20 or mean(overall)<=0:
  return {'factor':1.0,'games':len(chosen),'label':'Insufficient defensive sample'}
 raw=mean(chosen)/mean(overall)
 factor=max(.85,min(1.15,1+(raw-1)*len(chosen)/(len(chosen)+12)))
 return {'factor':_round(factor),'games':len(chosen),'label':'Historical position-level defense adjustment (shrunk and capped)'}

def _view(p,matchup=None):
 result=dict(p)
 result['matchup']=matchup or {'factor':1.0,'games':0,'label':'No opponent selected'}
 result['adjusted_estimate']=_round(p['estimate']*result['matchup']['factor'])
 return result

def start_sit(cards,player_a,player_b,rows=None,opponent_a='',opponent_b=''):
 by_id={p['id']:p for p in cards['players']}
 if player_a not in by_id or player_b not in by_id:raise ValueError('Select two players present in the imported season')
 a,b=by_id[player_a],by_id[player_b]
 if player_a==player_b:raise ValueError('Select two different players')
 ma=_matchup(rows,cards['season'],cards.get('through_week'),a['position'],opponent_a) if rows is not None else None
 mb=_matchup(rows,cards['season'],cards.get('through_week'),b['position'],opponent_b) if rows is not None else None
 a,b=_view(a,ma),_view(b,mb)
 gap=_round(a['adjusted_estimate']-b['adjusted_estimate']);lead=a if gap>=0 else b
 noise=math.sqrt(a['volatility']**2/max(a['games'],1)+b['volatility']**2/max(b['games'],1))
 strength='small / uncertain' if abs(gap)<max(2,noise) else 'meaningful historical gap'
 reasons=[f"Adjusted historical estimates: {a['adjusted_estimate']} vs {b['adjusted_estimate']} PPG (gap {abs(gap):.2f})",
  f"Recent vs season scoring: {a['recent_ppg']}/{a['season_ppg']} vs {b['recent_ppg']}/{b['season_ppg']} PPG",
  f"Median: {a['median_ppg']} vs {b['median_ppg']} PPG; observed 25th–75th percentile: {a['p25']}–{a['p75']} vs {b['p25']}–{b['p75']}",
  f"Recent targets/game: {a['targets_pg'] if a['targets_pg'] is not None else 'N/A'} vs {b['targets_pg'] if b['targets_pg'] is not None else 'N/A'}; carries/game: {a['carries_pg'] if a['carries_pg'] is not None else 'N/A'} vs {b['carries_pg'] if b['carries_pg'] is not None else 'N/A'}",
  f"Observed bust frequency: {a['bust_rate']}% vs {b['bust_rate']}% (position-dependent threshold); {a['games']} vs {b['games']} games",
  f"Defensive adjustment: ×{a['matchup']['factor']} ({a['matchup']['games']} games) vs ×{b['matchup']['factor']} ({b['matchup']['games']} games)"]
 if a['opportunities_pg'] is not None and b['opportunities_pg'] is not None:reasons.append(f"Recent touches + targets/game: {a['opportunities_pg']} vs {b['opportunities_pg']} (not equivalent opportunities across positions).")
 if a['games']<4 or b['games']<4:reasons.append('Small sample: at least one player has fewer than four games.')
 return {'a':a,'b':b,'gap':gap,'lean':lead['id'],'strength':strength,'reasons':reasons,'warning':cards['warning']}

def trade(cards,side_a,side_b,league_size=12):
 if not isinstance(league_size,int) or not 8<=league_size<=20:raise ValueError('League size must be 8–20')
 by_id={p['id']:p for p in cards['players']}
 if not side_a or not side_b or len(side_a)>6 or len(side_b)>6:raise ValueError('Select 1–6 players on each side')
 if len(set(side_a+side_b))!=len(side_a+side_b):raise ValueError('A player cannot appear twice')
 if any(pid not in by_id for pid in side_a+side_b):raise ValueError('Unknown player in trade')
 # Replacement ranks scale with league size, rather than assuming 12 teams.
 replacement={}
 for pos,per_team in [('QB',1.1),('RB',2.6),('WR',3.1),('TE',1.1)]:
  pool=sorted((p['estimate'] for p in cards['players'] if p['position']==pos),reverse=True)
  rank=max(1,round(league_size*per_team))
  replacement[pos]=pool[min(rank-1,len(pool)-1)] if pool else 0
 def calc(ids):
  group=[by_id[x] for x in ids]
  surplus=sum(max(0,p['estimate']-replacement[p['position']]) for p in group)
  # A multi-player side can look inflated even when only one acquired player
  # would enter the starting lineup; show top-three concentration separately.
  top3=sum(sorted((max(0,p['estimate']-replacement[p['position']]) for p in group),reverse=True)[:3])
  return {'players':group,'sum_estimate':_round(sum(p['estimate'] for p in group)),
   'replacement_surplus':_round(surplus),'top_three_surplus':_round(top3),
   'sample_warning':any(p['games']<4 for p in group),
   'best_single_surplus':_round(max((max(0,p['estimate']-replacement[p['position']]) for p in group),default=0))}
 a,b=calc(side_a),calc(side_b)
 return {'a':a,'b':b,'league_size':league_size,'replacement':{k:_round(v) for k,v in replacement.items()},
 'surplus_difference':_round(a['replacement_surplus']-b['replacement_surplus']),
 'notes':[f'Replacement baselines use approximate {league_size}-team roster depth, not live waiver availability.',
  'Review the top-three surplus metric when a trade includes several bench players.',
  'Roster fit, open lineup slots, injuries, byes, keeper value and rest-of-season projections are NOT included.',
  'A historical surplus advantage is not an actual market price or a predicted trade outcome.'],
 'warning':cards['warning']}
