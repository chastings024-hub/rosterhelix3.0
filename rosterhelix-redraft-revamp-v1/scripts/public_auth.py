"""Small single-instance account store for a persistent Render disk."""
import os, sqlite3, hashlib, hmac, secrets, time, json, re
from contextlib import contextmanager
from pathlib import Path
from scripts.roster_workspace import validate, DEFAULT
DB=Path(os.getenv('ROSTERHELIX_DB', str(Path(__file__).resolve().parent.parent/'data'/'accounts.sqlite3')))
MAX_AGE=60*60*24*14

@contextmanager
def connect():
 DB.parent.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect(str(DB),timeout=10)
 c.execute('PRAGMA busy_timeout=10000')
 c.execute('PRAGMA journal_mode=WAL')
 c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, salt BLOB NOT NULL, digest BLOB NOT NULL, created INTEGER NOT NULL)')
 c.execute('CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL, csrf TEXT NOT NULL, expires INTEGER NOT NULL)')
 c.execute('CREATE TABLE IF NOT EXISTS workspaces (user_id INTEGER PRIMARY KEY, payload TEXT NOT NULL)')
 c.execute('CREATE TABLE IF NOT EXISTS attempts (key TEXT PRIMARY KEY, count INTEGER NOT NULL, since INTEGER NOT NULL)')
 c.commit()
 try:
  with c:yield c
 finally:c.close()

def rate_limit(key, max_count=8, period=900):
 now=int(time.time())
 with connect() as c:
  r=c.execute('SELECT count,since FROM attempts WHERE key=?',(key,)).fetchone()
  if not r or now-r[1]>=period:
   c.execute('INSERT INTO attempts(key,count,since) VALUES(?,1,?) ON CONFLICT(key) DO UPDATE SET count=1,since=excluded.since',(key,now));return True
  if r[0]>=max_count:return False
  c.execute('UPDATE attempts SET count=count+1 WHERE key=?',(key,));return True

def register(email,password):
 email=email.strip().lower()
 if not re.fullmatch(r'[^@\s]{1,100}@[^@\s]{1,150}\.[^@\s]{2,30}',email):raise ValueError('Enter a valid email address')
 if not 12<=len(password)<=128:raise ValueError('Password must be 12–128 characters')
 salt=secrets.token_bytes(16);digest=hashlib.scrypt(password.encode(),salt=salt,n=2**14,r=8,p=1)
 with connect() as c:
  try:c.execute('INSERT INTO users(email,salt,digest,created) VALUES(?,?,?,?)',(email,salt,digest,int(time.time())))
  except sqlite3.IntegrityError:raise ValueError('Account already exists')
 return login(email,password)

def login(email,password):
 email=email.strip().lower()
 with connect() as c:
  row=c.execute('SELECT id,salt,digest FROM users WHERE email=?',(email,)).fetchone()
  salt=row[1] if row else b'\0'*16
  attempt=hashlib.scrypt(password.encode(),salt=salt,n=2**14,r=8,p=1)
  if not row or not hmac.compare_digest(attempt,row[2]):raise ValueError('Invalid email or password')
  token=secrets.token_urlsafe(32);csrf=secrets.token_urlsafe(32)
  c.execute('DELETE FROM sessions WHERE expires<?',(int(time.time()),))
  c.execute('INSERT INTO sessions(token_hash,user_id,csrf,expires) VALUES(?,?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),row[0],csrf,int(time.time())+MAX_AGE))
  return token,csrf

def session(token):
 if not token:return None
 with connect() as c:
  row=c.execute('SELECT s.user_id,s.csrf,u.email FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires>?',(hashlib.sha256(token.encode()).hexdigest(),int(time.time()))).fetchone()
 return {'id':row[0],'csrf':row[1],'email':row[2]} if row else None

def logout(token):
 if token:
  with connect() as c:c.execute('DELETE FROM sessions WHERE token_hash=?',(hashlib.sha256(token.encode()).hexdigest(),))

def workspace(user_id):
 with connect() as c:r=c.execute('SELECT payload FROM workspaces WHERE user_id=?',(user_id,)).fetchone()
 return validate(json.loads(r[0])) if r else validate(DEFAULT)

def save_workspace(user_id,payload):
 data=validate(payload)
 with connect() as c:c.execute('INSERT INTO workspaces(user_id,payload) VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET payload=excluded.payload',(user_id,json.dumps(data)))
 return data
