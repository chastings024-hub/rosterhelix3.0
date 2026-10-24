#!/usr/bin/env python3
"""Import NFL schedule, retaining only valid regular season games and atomic writes."""
import argparse,csv,io,json,os,pathlib,tempfile,urllib.request,datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
URL='https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv'
FIELDS=['season','week','home_team','away_team','gameday','gametime']
def normalize(content,season):
 reader=csv.DictReader(io.StringIO(content.decode('utf-8-sig')))
 if not reader.fieldnames or not {'season','week','home_team','away_team'}.issubset(reader.fieldnames):raise ValueError('Unrecognized schedule CSV schema')
 result=[];seen=set()
 for r in reader:
  if str(r.get('season'))!=str(season) or (r.get('game_type') or 'REG')!='REG':continue
  try:w=int(r['week'])
  except (TypeError,ValueError):continue
  home=(r.get('home_team') or '').strip();away=(r.get('away_team') or '').strip()
  if not 1<=w<=18 or not home or not away or home==away:continue
  key=(w,home,away)
  if key in seen:continue
  seen.add(key);result.append({'season':str(season),'week':str(w),'home_team':home,'away_team':away,'gameday':r.get('gameday') or '', 'gametime':r.get('gametime') or ''})
 if not result:raise RuntimeError('No regular-season games for requested season')
 return sorted(result,key=lambda r:(int(r['week']),r['gameday'],r['home_team']))
def main():
 p=argparse.ArgumentParser();p.add_argument('--season',type=int,default=datetime.datetime.now(datetime.timezone.utc).year);p.add_argument('--source');a=p.parse_args()
 source=a.source or (os.getenv('FOURTHDOWN_SCHEDULE_URL') or os.getenv('SNAPEDGE_SCHEDULE_URL')) or URL
 if source.startswith('http'):
  if not source.startswith('https://'):raise ValueError('HTTPS required')
  with urllib.request.urlopen(urllib.request.Request(source,headers={'User-Agent':'FourthDownAnalytics/0.9'}),timeout=40) as resp:content=resp.read(5_000_001)
 else:content=pathlib.Path(source).read_bytes()
 if len(content)>5_000_000:raise ValueError('Schedule exceeds size limit')
 rows=normalize(content,a.season);out=ROOT/'data';out.mkdir(exist_ok=True)
 with tempfile.NamedTemporaryFile('w',encoding='utf8',newline='',dir=out,delete=False) as f:
  writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows);tmp=f.name
 os.replace(tmp,out/'schedule.csv');print('Imported',len(rows),'scheduled games for',a.season)
if __name__=='__main__':main()
