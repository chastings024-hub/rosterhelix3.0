"""Local single-user roster persistence. Not suitable for multi-user public hosting."""
import json, os, tempfile
from pathlib import Path
SCORING=('ppr','half','standard')
POSITIONS={'QB','RB','WR','TE','K','DST'}
DEFAULT={'league_name':'My League','scoring':'ppr','slots':{'QB':1,'RB':2,'WR':2,'TE':1,'FLEX':1},'players':[]}

def validate(payload):
 if not isinstance(payload,dict):raise ValueError('Expected a roster object')
 name=payload.get('league_name','My League')
 if not isinstance(name,str) or len(name)>80:raise ValueError('League name must be 80 characters or less')
 scoring=payload.get('scoring','ppr')
 if scoring not in SCORING:raise ValueError('Invalid scoring')
 slots=payload.get('slots',DEFAULT['slots'])
 if not isinstance(slots,dict) or set(slots)-set(DEFAULT['slots']):raise ValueError('Invalid lineup positions')
 normalized={}
 for k in DEFAULT['slots']:
  v=slots.get(k,DEFAULT['slots'][k])
  if type(v) is not int or not 0<=v<=5:raise ValueError('Lineup slots must be integers 0–5')
  normalized[k]=v
 players=payload.get('players',[])
 if not isinstance(players,list) or len(players)>40:raise ValueError('Roster limited to 40 players')
 cleaned=[];ids=set()
 for pl in players:
  if not isinstance(pl,dict):raise ValueError('Invalid player')
  pid=pl.get('id');nm=pl.get('name');pos=pl.get('position')
  if not all(isinstance(v,str) for v in (pid,nm,pos)) or not 1<=len(pid)<=90 or not 1<=len(nm)<=100 or pos not in POSITIONS:raise ValueError('Invalid player fields')
  if pid in ids:raise ValueError('Duplicate player ID')
  ids.add(pid);cleaned.append({'id':pid,'name':nm,'position':pos,'team':str(pl.get('team',''))[:12]})
 return {'league_name':name,'scoring':scoring,'slots':normalized,'players':cleaned}

def load(path):
 if not Path(path).exists():return dict(DEFAULT)
 return validate(json.loads(Path(path).read_text(encoding='utf8')))

def save(path,payload):
 cleaned=validate(payload);path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile('w',encoding='utf8',dir=path.parent,delete=False) as f:
  json.dump(cleaned,f,indent=2);tmp=f.name
 os.replace(tmp,path)
 return cleaned
