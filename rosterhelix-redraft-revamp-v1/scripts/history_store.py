"""Historical player/matchup importer and indexed read helpers. Standard library only."""
import csv,io,json,os,tempfile,datetime
from pathlib import Path
from collections import defaultdict
from update_data import normalize,FIELDS
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; HISTORY=DATA/'history_player_stats.csv'
MAX_BYTES=35_000_000

def parse(content,source='canonical',season=None):
 if len(content)>MAX_BYTES:raise ValueError('CSV exceeds 35 MB')
 if source=='nflverse':
  if season is None:raise ValueError('Specify season for nflverse imports')
  rows=normalize(content,int(season))
 else:
  reader=csv.DictReader(io.StringIO(content.decode('utf-8-sig')))
  names=set(reader.fieldnames or [])
  if not {'season','week','position'}.issubset(names) or not ('player_id' in names and ('player_name' in names or 'player_display_name' in names)):
   raise ValueError('CSV needs season, week, position, player_id and player_name')
  if 'fantasy_points_ppr' not in names:raise ValueError('CSV needs fantasy_points_ppr')
  rows=[]
  for r in reader:
   if r.get('position') not in {'QB','RB','WR','TE'}:continue
   item={k:r.get(k,'') for k in FIELDS};item['player_name']=r.get('player_name') or r.get('player_display_name') or ''
   rows.append(item)
 if not rows:raise ValueError('No supported player records')
 seen=set()
 for r in rows:
  try:
   y=int(r['season']);w=int(r['week']);p=float(r['fantasy_points_ppr'])
   if not 1999<=y<=datetime.date.today().year or not 1<=w<=18 or not -100<=p<=150:raise ValueError()
   if not r['player_id'] or not r['player_name']:raise ValueError()
  except (TypeError,ValueError):raise ValueError('Invalid season, week, player or fantasy points')
  k=(r['season'],r['week'],r['player_id'])
  if k in seen:raise ValueError('Duplicate player-season-week in uploaded CSV')
  seen.add(k)
 return rows

def read_rows():
 if not HISTORY.exists():return []
 with HISTORY.open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))

def atomic_csv(path,rows):
 path.parent.mkdir(exist_ok=True,parents=True)
 with tempfile.NamedTemporaryFile('w',encoding='utf8',newline='',dir=path.parent,delete=False) as f:
  writer=csv.DictWriter(f,fieldnames=FIELDS,extrasaction='ignore');writer.writeheader();writer.writerows(rows);temp=f.name
 os.replace(temp,path)

def merge(rows):
 old=read_rows(); indexed={(r['season'],r['week'],r['player_id']):r for r in old}
 for r in rows:indexed[(r['season'],r['week'],r['player_id'])]=r
 merged=sorted(indexed.values(),key=lambda r:(int(r['season']),int(r['week']),r['player_name']))
 atomic_csv(HISTORY,merged)
 # Keep the active current-season dataset synchronized for the existing analytics UI.
 current=max(int(r['season']) for r in merged)
 active=[r for r in merged if int(r['season'])==current]
 atomic_csv(DATA/'player_stats.csv',active)
 meta={'source':'imported historical CSV (source not independently verified)','season':current,'rows':len(active),'history_rows':len(merged),'seasons':sorted({int(r['season']) for r in merged}),'latest_week':max(int(r['week']) for r in active),'updated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'includes_snap_share':False,'includes_routes':False,'includes_injuries':False,'has_opponent_data':any(r.get('opponent_team') for r in active),'verified_live':False}
 (DATA/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
 return meta

def query(rows,season=None,player=None,position=None,opponent=None,week=None,limit=300):
 out=[]
 for r in reversed(rows):
  if season and int(r['season'])!=season:continue
  if player and player.lower() not in (r['player_name']+' '+r['player_id']).lower():continue
  if position and r['position']!=position:continue
  if opponent and r.get('opponent_team','').upper()!=opponent.upper():continue
  if week and int(r['week'])!=week:continue
  out.append(r)
  if len(out)>=limit:break
 return out

def matchups(rows,season=None,opponent=None,position=None):
 games=defaultdict(lambda:{'points':0.,'players':0,'targets':0.,'carries':0.})
 for r in rows:
  if season and int(r['season'])!=season:continue
  team=r.get('opponent_team','').upper().strip()
  if not team or (opponent and team!=opponent.upper()) or (position and r['position']!=position):continue
  key=(int(r['season']),int(r['week']),team,r['position']);g=games[key]
  g['points']+=float(r['fantasy_points_ppr']);g['players']+=1
  for field,dest in [('receiving_targets','targets'),('rushing_attempts','carries')]:
   try:g[dest]+=float(r.get(field) or 0)
   except ValueError:pass
 return [dict(season=k[0],week=k[1],defense=k[2],position=k[3],points_allowed=round(v['points'],2),player_games=v['players'],targets_allowed=v['targets'],carries_allowed=v['carries']) for k,v in sorted(games.items(),reverse=True)]
