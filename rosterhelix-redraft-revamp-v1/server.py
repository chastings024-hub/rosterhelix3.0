#!/usr/bin/env python3
"""Zero-dependency local API for RosterHelix; run: python server.py"""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
from pathlib import Path
import json,csv,statistics,math,os,ipaddress,sys,datetime,secrets,urllib.parse
sys.path.insert(0,str(Path(__file__).resolve().parent / "scripts"))
from scripts.history_store import parse as parse_history,merge as merge_history,read_rows as read_history,query as query_history,matchups as historical_matchups
ROOT=Path(__file__).resolve().parent
DATA=Path(os.getenv("ROSTERHELIX_DATA_DIR",str(ROOT/"data")))
DATA.mkdir(parents=True,exist_ok=True)
if DATA != ROOT/"data":
 import shutil
 local=ROOT/"data"
 if local.exists() and not local.is_symlink():
  for f in local.iterdir():
   if f.is_file() and not (DATA/f.name).exists():shutil.copy2(f,DATA/f.name)
  shutil.rmtree(local)
 if not local.exists():local.symlink_to(DATA, target_is_directory=True)
if DATA != ROOT/"data":
 import scripts.history_store as _hs
 _hs.DATA_DIR=DATA if hasattr(_hs,"DATA_DIR") else DATA
import sys
sys.path.insert(0,str(ROOT / "scripts"))
from projection_engine import project
from advanced_engine import opportunity,apply_scenario,rest_of_season,trade_sides
from model_accuracy import report
class Handler(SimpleHTTPRequestHandler):
 def token(self):
  from http.cookies import SimpleCookie
  try:
   c=SimpleCookie();c.load(self.headers.get('Cookie',''));return c['rh_session'].value if 'rh_session' in c else None
  except Exception:return None
 def current_user(self):
  from scripts.public_auth import session
  return session(self.token())
 def is_admin(self):
  u=self.current_user()
  return bool(u and u['email']==os.getenv('ADMIN_EMAIL','').strip().lower() and os.getenv('ADMIN_API_KEY') and secrets.compare_digest(self.headers.get('X-Admin-Key',''),os.getenv('ADMIN_API_KEY',''))) 
 def csrf_ok(self):
  u=self.current_user()
  return bool(u and secrets.compare_digest(self.headers.get('X-CSRF-Token',''),u['csrf']))
 def send_auth(self,obj,status=200,cookie=None):
  body=json.dumps(obj).encode();self.send_response(status)
  self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store')
  self.send_header('X-Content-Type-Options','nosniff')
  self.send_header('Referrer-Policy','strict-origin-when-cross-origin')
  if cookie is not None:
   secure='; Secure' if os.getenv('PUBLIC_SITE','0')=='1' else ''
   self.send_header('Set-Cookie','rh_session='+cookie+'; HttpOnly; SameSite=Lax; Path=/; Max-Age='+str(1209600 if cookie else 0)+secure)
  self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def read_json(self,limit=20000):
  n=int(self.headers.get('Content-Length','0'))
  if n<1 or n>limit:raise ValueError('Invalid request size')
  return json.loads(self.rfile.read(n))
 def do_POST(self):
  origin=self.headers.get('Origin')
  host=self.headers.get('Host','')
  if origin:
   o=urllib.parse.urlparse(origin)
   if o.netloc.lower()!=host.lower() or o.scheme not in ('https','http'):
    return self.send_json({'error':'Cross-origin request blocked'},403)
  elif os.getenv('PUBLIC_SITE')=='1':
   return self.send_json({'error':'Origin required'},403)
  endpoint=urlparse(self.path).path
  if endpoint in ('/api/auth/register','/api/auth/login'):
   from scripts.public_auth import register,login,rate_limit
   client=self.client_address[0]
   if not rate_limit('auth:'+client,12,900):return self.send_json({'error':'Too many attempts; try later'},429)
   try:
    d=self.read_json(4096);email=d.get('email','');password=d.get('password','')
    if not isinstance(email,str) or not isinstance(password,str):raise ValueError('Invalid credentials')
    token,csrf=(register if endpoint.endswith('register') else login)(email,password)
    return self.send_auth({'ok':True,'email':email.lower().strip(),'csrf':csrf},cookie=token)
   except (ValueError,TypeError,json.JSONDecodeError) as exc:return self.send_json({'error':str(exc)},400)
  if endpoint=='/api/auth/logout':
   if not self.csrf_ok():return self.send_json({'error':'Authentication required'},403)
   from scripts.public_auth import logout
   logout(self.token());return self.send_auth({'ok':True},cookie='')
  if endpoint=='/api/workspace' and not self.csrf_ok():return self.send_json({'error':'Sign in and provide CSRF token'},403)
  if endpoint in ('/api/history/sync','/api/history/import') and (not self.is_admin() or not self.csrf_ok()):
   return self.send_json({'error':'Administrator permission required'},403)
  if endpoint=='/api/workspace':
   try:
    from scripts.public_auth import save_workspace
    return self.send_json({'workspace':save_workspace(self.current_user()['id'],self.read_json())})
   except (ValueError,TypeError,json.JSONDecodeError) as exc:return self.send_json({'error':str(exc)},400)
  if endpoint=='/api/history/sync':
   try:
    from scripts.sync_history import sync
    q=parse_qs(urlparse(self.path).query)
    start=int(q.get('start',['2020'])[0]);end=int(q.get('end',[str(__import__('datetime').date.today().year)])[0])
    return self.send_json({'metadata':sync(start,end)})
   except (ValueError,RuntimeError) as exc:return self.send_json({'error':str(exc)},502)
   except Exception as exc:return self.send_json({'error':'Sync unavailable','detail':str(exc)},503)
  if endpoint!='/api/history/import':return self.send_json({'error':'Unknown endpoint'},404)
  try:
   n=int(self.headers.get('Content-Length','0'))
   if n<=0 or n>35_000_000:return self.send_json({'error':'Upload must be a CSV under 35 MB'},413)
   q=parse_qs(urlparse(self.path).query)
   source=q.get('format',['canonical'])[0]
   if source not in ('canonical','nflverse'):raise ValueError('Unknown CSV format')
   season=q.get('season',[None])[0]
   records=parse_history(self.rfile.read(n),source,season)
   meta=merge_history(records)
   return self.send_json({'imported_rows':len(records),'metadata':meta})
  except (ValueError,UnicodeError) as exc:return self.send_json({'error':str(exc)},400)
  except Exception as exc:return self.send_json({'error':'Import failed','detail':str(exc)},500)

 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
 def end_headers(self):
  self.send_header("X-Content-Type-Options","nosniff")
  self.send_header("Referrer-Policy","strict-origin-when-cross-origin")
  self.send_header("X-Frame-Options","DENY")
  super().end_headers()
 def send_json(self,obj,status=200):
  body=json.dumps(obj,allow_nan=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def do_GET(self):
  p=urlparse(self.path)
  if not p.path.startswith('/api/'):
   # Never expose imported datasets, saved rosters, or Python source over HTTP.
   from urllib.parse import unquote
   path=unquote(p.path).replace('\\','/')
   parts=path.split('/')
   if any(part in ('data','scripts','__pycache__','.github') or part.startswith('.') for part in parts if part):
    return self.send_error(403,'Private server files are not served')
   if path not in ('/','/index.html','/analytics.html','/account.html') and not path.startswith('/assets/'):
    return self.send_error(404,'Not found')
   return super().do_GET()
  try:
   if p.path in ('/api/history','/api/history/matchups','/api/history/summary','/api/history/audit'):
    q=parse_qs(p.query);history=read_history()
    season=int(q['season'][0]) if q.get('season') and q['season'][0] else None
    if p.path=='/api/history/audit':
     from scripts.data_audit import audit
     return self.send_json(audit(history))
    if p.path=='/api/history/summary':return self.send_json({'rows':len(history),'seasons':sorted({int(r['season']) for r in history}),'players':len({r['player_id'] for r in history}),'opponents':sorted({r.get('opponent_team','') for r in history if r.get('opponent_team')}),'source':'User-imported CSV; authenticity not independently verified'})
    if p.path=='/api/history/matchups':return self.send_json({'matchups':historical_matchups(history,season,q.get('opponent',[''])[0],q.get('position',[''])[0])[:500]})
    limit=max(1,min(1000,int(q.get('limit',['300'])[0])))
    return self.send_json({'rows':query_history(history,season,q.get('player',[''])[0],q.get('position',[''])[0],q.get('opponent',[''])[0],int(q['week'][0]) if q.get('week') and q['week'][0] else None,limit),'source':'User-imported; not independently verified'})
   if p.path=='/api/validation/compare':
    from scripts.compare_models import compare
    q=parse_qs(p.query);scoring=q.get('scoring',['ppr'])[0]
    if scoring not in ('ppr','half','standard'):raise ValueError('Invalid scoring')
    history=read_history()
    if not history:return self.send_json({'error':'Import historical player statistics before running validation'},409)
    return self.send_json(compare(history,{'ppr':1,'half':.5,'standard':0}[scoring]))
   if p.path=='/api/history/diagnostics':
    from scripts.source_diagnostics import diagnose
    q=parse_qs(p.query)
    return self.send_json(diagnose(int(q.get('season',['2024'])[0])))
   if p.path=='/api/history/player-averages':
    from scripts.player_comparison import player_averages
    q=parse_qs(p.query)
    season=int(q['season'][0]) if q.get('season') else None
    window=int(q.get('window',['5'])[0])
    if not 1<=window<=18:raise ValueError('Window must be 1–18 games')
    return self.send_json({'players':player_averages(read_history(),season,window),
      'source':'Imported historical game logs; averages are descriptive, not future projections'})
   if p.path=='/api/heldout-validation':
    from scripts.validation_suite import evaluate
    q=parse_qs(p.query)
    train_end=int(q.get('train_end',['2022'])[0]);test_start=int(q.get('test_start',['2023'])[0]);test_end=int(q.get('test_end',['2024'])[0])
    min_prior=int(q.get('min_prior',['3'])[0]);window=int(q.get('window',['5'])[0])
    return self.send_json(evaluate(read_history(),train_end,test_start,test_end,min_prior,window))
   if p.path=='/api/model-optimization':
    from scripts.model_optimization import optimize
    q=parse_qs(p.query)
    season=int(q['season'][0]) if q.get('season') and q['season'][0] else None
    min_prior=int(q.get('min_prior',['3'])[0]);window=int(q.get('window',['5'])[0])
    return self.send_json(optimize(read_history(),season,min_prior,window))
   if p.path=='/api/decision-backtest':
    from scripts.decision_backtest import backtest
    q=parse_qs(p.query)
    season=int(q['season'][0]) if q.get('season') and q['season'][0] else None
    min_prior=int(q.get('min_prior',['3'])[0])
    window=int(q.get('window',['5'])[0])
    return self.send_json(backtest(read_history(),season,min_prior,window))
   if p.path=='/api/decision-estimates':
    from scripts.decision_engine import estimate
    q=parse_qs(p.query)
    season=int(q.get('season',['2024'])[0])
    week=int(q.get('week',['18'])[0])
    window=int(q.get('window',['5'])[0])
    opponent=q.get('opponent',[''])[0]
    return self.send_json({'season':season,'week':week,'opponent':opponent or None,
       'players':estimate(read_history(),season,week,opponent,window),
       'warning':'Experimental estimates from imported past games only; not calibrated forecasts. Opponent effects are pooled position-level samples, not player-specific matchups. No injuries, depth charts or current usage feed.'})
   if p.path in ('/api/decisions/v2/players','/api/decisions/v2/start-sit','/api/decisions/v2/trade'):
    from scripts.decision_v2 import player_cards,start_sit,trade
    q=parse_qs(p.query)
    season=int(q['season'][0]) if q.get('season') and q['season'][0] else None
    week=int(q['week'][0]) if q.get('week') and q['week'][0] else None
    if week is not None and not 1<=week<=18:raise ValueError('Week must be 1–18')
    cards=player_cards(read_history(),season,week,q.get('scoring',['ppr'])[0],int(q.get('window',['5'])[0]))
    if p.path.endswith('/players'):return self.send_json(cards)
    if p.path.endswith('/start-sit'):return self.send_json(start_sit(cards,q.get('a',[''])[0],q.get('b',[''])[0],read_history(),q.get('opponent_a',[''])[0],q.get('opponent_b',[''])[0]))
    return self.send_json(trade(cards,q.get('a',[''])[0].split(',') if q.get('a') else [],q.get('b',[''])[0].split(',') if q.get('b') else [],int(q.get('league_size',['12'])[0])))
   if p.path=='/api/auth/me':
    u=self.current_user()
    return self.send_json({'authenticated':bool(u),'email':u['email'] if u else None,'csrf':u['csrf'] if u else None,'admin':bool(u and u['email']==os.getenv('ADMIN_EMAIL','').strip().lower())})
   if p.path=='/api/workspace':
    from scripts.public_auth import workspace
    u=self.current_user()
    if not u:return self.send_json({'error':'Sign in to view your roster'},401)
    return self.send_json({'workspace':workspace(u['id'])})
   if p.path=='/api/research':
    from scripts.research_hub import profiles
    q=parse_qs(p.query);season=int(q['season'][0]) if q.get('season') else None
    return self.send_json({'players':profiles(read_history(),season),'source':'Imported game logs; no live injury or usage feed'})
   if p.path=='/api/decision-center':
    from scripts.public_auth import workspace
    from scripts.research_hub import insights
    u=self.current_user()
    if not u:return self.send_json({'error':'Sign in to view recommendations'},401)
    q=parse_qs(p.query);season=int(q['season'][0]) if q.get('season') else None
    return self.send_json(insights(read_history(),workspace(u['id']),season))
   if p.path=='/api/data-readiness':
    from scripts.data_audit import audit
    history=read_history();metadata=ROOT/'data/metadata.json'
    m=json.loads(metadata.read_text()) if metadata.exists() else {}
    return self.send_json({'rows':len(history),'seasons':sorted({int(r['season']) for r in history}),
      'last_import_utc':m.get('updated_at_utc'), 'verified_live':False,
      'audit':audit(history) if history else None,
      'warning':'Local imported statistics are not independently verified as current or complete'})
   if p.path=='/api/health':return self.send_json({'ok':True,'service':'RosterHelix Public Beta','dataset_available':(ROOT/'data/player_stats.csv').exists()})
   if p.path=='/api/matchups':
    f=ROOT/'data/matchups.json'
    return self.send_json(json.loads(f.read_text()) if f.exists() else {'error':'No defensive matchup report; run build_defense.py and build_matchups.py'},200 if f.exists() else 503)
   if p.path=='/api/status':
    f=ROOT/'data/metadata.json';return self.send_json(json.loads(f.read_text()) if f.exists() else {'status':'no_data','message':'Run scripts/update_data.py to sync real stats'})
   f=ROOT/'data/player_stats.csv'
   if not f.exists():return self.send_json({'error':'No synced NFL dataset; run update_data.py'},503)
   with f.open(newline='',encoding='utf-8') as fp:rows=list(csv.DictReader(fp))
   if p.path=='/api/players':
    latest={}
    for r in rows:latest[r['player_id']]=r
    return self.send_json({'players':[{'id':r['player_id'],'name':r['player_name'],'team':r['recent_team'],'position':r['position']} for r in sorted(latest.values(),key=lambda x:x['player_name'])]})
   if p.path=='/api/schedule':
    sf=ROOT/'data/schedule.csv'
    if not sf.exists():return self.send_json({'error':'No schedule; run build_schedule.py'},503)
    with sf.open(newline='',encoding='utf8') as fp:games=list(csv.DictReader(fp))
    q=parse_qs(p.query);week=int(q.get('week',[0])[0]);return self.send_json({'games':[g for g in games if not week or int(g['week'])==week]})
   if p.path in ('/api/opportunity','/api/ros','/api/accuracy'):
    q=parse_qs(p.query);season=max(int(r['season']) for r in rows)
    week=int(q.get('week',[min(18,max(int(r['week']) for r in rows)+1)])[0]);scoring=q.get('scoring',['ppr'])[0]
    if not 1<=week<=18 or scoring not in ('ppr','half','standard'):raise ValueError('Invalid week or scoring')
    if p.path=='/api/opportunity':return self.send_json({'season':season,'week':week,'players':opportunity(rows,season,week)})
    if p.path=='/api/accuracy':return self.send_json(report(rows,{'ppr':1,'half':.5,'standard':0}[scoring]))
    sf=ROOT/'data/schedule.csv';df=ROOT/'data/defense_allowed.csv'
    with sf.open(newline='',encoding='utf8') as fp:schedule=list(csv.DictReader(fp)) if sf.exists() else []
    with df.open(newline='',encoding='utf8') as fp:defense=list(csv.DictReader(fp)) if df.exists() else []
    if not schedule:return self.send_json({'error':'Schedule unavailable; cannot calculate ROS totals'},503)
    return self.send_json({'season':season,'start_week':week,'players':rest_of_season(rows,schedule,defense,season,week,scoring),'warning':'Future projections freeze historical form at start week; missing schedule weeks are not byes.'})
   if p.path=='/api/projections':
    q=parse_qs(p.query);week=int(q.get('week',[max(int(r['week']) for r in rows)+1])[0]);scoring=q.get('scoring',['ppr'])[0]
    season=max(int(r['season']) for r in rows)
    sf=ROOT/'data/schedule.csv';df=ROOT/'data/defense_allowed.csv'
    with sf.open(newline='',encoding='utf8') as fp:schedule=list(csv.DictReader(fp)) if sf.exists() else []
    with df.open(newline='',encoding='utf8') as fp:defense=list(csv.DictReader(fp)) if df.exists() else []
    projections=project(rows,schedule,defense,season,week,scoring)
    status=q.get('scenario_status',['unknown'])[0];availability=float(q.get('availability',['1'])[0])
    if status!='unknown' or availability!=1:projections=apply_scenario(projections,status,availability)
    return self.send_json({'season':season,'week':week,'scoring':scoring,'schedule_available':bool(schedule),'defense_available':bool(defense),'warning':'Projections are uncalibrated estimates; no injury, route or weather model. Missing opponent mapping is not a verified bye.','projections':projections})
   return self.send_json({'error':'Unknown endpoint'},404)
  except (ValueError,KeyError,TypeError) as e:return self.send_json({'error':str(e)},400)
  except Exception as e:return self.send_json({'error':'Dataset unavailable','detail':str(e)},500)
if __name__=='__main__':
 port=int(os.getenv('PORT','8000'));host='0.0.0.0' if os.getenv('PUBLIC_SITE')=='1' else '127.0.0.1';print(f'RosterHelix http://{host}:{port}');ThreadingHTTPServer((host,port),Handler).serve_forever()
