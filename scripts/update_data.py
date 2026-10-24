#!/usr/bin/env python3
"""Import current nflverse stats_player weekly CSV into the FourthDown Analytics canonical schema.
Never overwrite a successful dataset with an empty or malformed response.
"""
import argparse,csv,io,json,os,pathlib,urllib.request,datetime,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
FIELDS=['player_id','player_name','position','recent_team','opponent_team','season','week','fantasy_points_ppr','receptions','receiving_targets','rushing_attempts','passing_yards','passing_tds','passing_interceptions','rushing_yards','rushing_tds','receiving_yards','receiving_tds','rushing_fumbles_lost','receiving_fumbles_lost','sack_fumbles_lost']
URL='https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_{season}.csv'
def normalize(content,season):
 reader=csv.DictReader(io.StringIO(content.decode('utf-8-sig')))
 if not reader.fieldnames or not {'season','week','position'}.issubset(reader.fieldnames):raise ValueError('Unrecognized nflverse stats_player schema')
 rows=[]
 for r in reader:
  if str(r.get('season',''))!=str(season) or (r.get('season_type') or 'REG')!='REG' or r.get('position') not in ('QB','RB','WR','TE'):continue
  name=r.get('player_display_name') or r.get('player_name') or r.get('player_name_full') or r.get('full_name') or ''
  pid=r.get('player_id') or r.get('gsis_id') or ''
  if not name or not pid:continue
  item={k:r.get(k,'') for k in FIELDS};item['player_name']=name;item['player_id']=pid;item['recent_team']=r.get('recent_team') or r.get('team') or '';item['opponent_team']=r.get('opponent_team') or ''
  if not item['fantasy_points_ppr']:
   # New stats_player release may omit precomputed fantasy points: derive from raw offense totals.
   def n(k):
    try:return float(r.get(k) or 0)
    except ValueError:return 0
   fumbles=n('rushing_fumbles_lost')+n('receiving_fumbles_lost')+n('sack_fumbles_lost')
   item['fantasy_points_ppr']=str(round(n('passing_yards')/25+4*n('passing_tds')-2*n('passing_interceptions')+n('rushing_yards')/10+6*n('rushing_tds')+n('receiving_yards')/10+6*n('receiving_tds')+n('receptions')-2*fumbles,3))
  rows.append(item)
 if not rows:raise RuntimeError('No player game rows found for season '+str(season))
 rows.sort(key=lambda r:(int(r['week']),r['player_name']))
 return rows

def main():
 p=argparse.ArgumentParser();p.add_argument('--source');p.add_argument('--season',type=int,default=datetime.datetime.now(datetime.timezone.utc).year);a=p.parse_args()
 source=a.source or (os.environ.get('FOURTHDOWN_STATS_URL') or os.environ.get('SNAPEDGE_STATS_URL')) or URL.format(season=a.season)
 if source.startswith(('https://','http://')):
  if not source.startswith('https://'):raise ValueError('HTTPS required for remote sources')
  req=urllib.request.Request(source,headers={'User-Agent':'FourthDownAnalytics/0.7 (public historical data importer)'})
  with urllib.request.urlopen(req,timeout=75) as resp:content=resp.read(90_000_001)
 else:content=pathlib.Path(source).read_bytes()
 if len(content)>90_000_000:raise ValueError('CSV exceeds 90 MB')
 rows=normalize(content,a.season)
 out=ROOT/'data';out.mkdir(exist_ok=True)
 with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='',dir=out,delete=False) as f:
  writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows);tmp=f.name
 os.replace(tmp,out/'player_stats.csv')
 meta={'source':source,'season':a.season,'rows':len(rows),'latest_week':max(int(r['week']) for r in rows),'updated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'dataset':'nflverse weekly offensive player statistics','includes_snap_share':False,'includes_routes':False,'includes_injuries':False,'has_opponent_data':any(r.get('opponent_team') for r in rows),'verified_live':False}
 (out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2))
if __name__=='__main__':main()
