#!/usr/bin/env python3
"""Walk-forward evaluation. Uses ONLY games before each prediction week."""
import argparse,csv,collections,json,math,pathlib,statistics
ROOT=pathlib.Path(__file__).resolve().parents[1]
DECAY={'QB':.86,'RB':.74,'WR':.78,'TE':.82}
def numeric(v):
 try:return float(v)
 except (ValueError,TypeError):return None
def points(row,scoring=1):
 p=numeric(row.get('fantasy_points_ppr')); r=numeric(row.get('receptions'))
 return None if p is None else p-(1-scoring)*(r or 0)
def estimate(rows,pos,scoring=1):
 vals=[points(r,scoring) for r in rows[-5:]];vals=[v for v in vals if v is not None]
 if len(vals)<2:return None
 decay=DECAY.get(pos,.8);weights=[decay**(len(vals)-i-1) for i in range(len(vals))]
 return sum(v*w for v,w in zip(vals,weights))/sum(weights)
def evaluate(rows,scoring=1):
 groups=collections.defaultdict(list)
 for r in rows:
  if r.get('position') not in DECAY:continue
  try:key=(int(r['season']),int(r['week']))
  except (KeyError,ValueError):continue
  groups[(r.get('player_id') or r.get('player_name'),int(r['season']))].append((key,r))
 errors=[]; by_pos=collections.defaultdict(list);out=[]
 for (_,season), games in groups.items():
  games.sort(key=lambda x:x[0]);history=[]
  for (_,week),r in games:
   actual=points(r,scoring);pred=estimate(history,r['position'],scoring)
   if pred is not None and actual is not None:
    err=pred-actual;errors.append(err);by_pos[r['position']].append(err)
    out.append({'season':season,'week':week,'player_id':r.get('player_id'),'position':r['position'],'prediction':round(pred,3),'actual':round(actual,3),'error':round(err,3)})
   history.append(r)
 def metrics(es):return {'n':len(es),'mae':round(statistics.mean(map(abs,es)),3),'rmse':round(math.sqrt(statistics.mean(e*e for e in es)),3),'bias':round(statistics.mean(es),3)} if es else {'n':0,'mae':None,'rmse':None,'bias':None}
 return {'overall':metrics(errors),'by_position':{k:metrics(v) for k,v in sorted(by_pos.items())},'method':'walk-forward, previous 2-5 recorded games only, no injury or opponent model','predictions':out}
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',default=str(ROOT/'data/player_stats.csv'));p.add_argument('--output',default=str(ROOT/'data/backtest.json'));p.add_argument('--scoring',type=float,choices=[0,0.5,1],default=1);a=p.parse_args()
 with open(a.input,encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
 result=evaluate(rows,a.scoring);pathlib.Path(a.output).parent.mkdir(parents=True,exist_ok=True);pathlib.Path(a.output).write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='predictions'},indent=2))
if __name__=='__main__':main()
