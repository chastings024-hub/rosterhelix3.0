"""Deterministic quality report for imported historical player-games."""
from collections import Counter,defaultdict

def audit(rows):
    seasons=defaultdict(lambda: {'games':0,'players':set(),'weeks':set(),'opponent_missing':0,'names_missing':0,'duplicate_keys':0})
    seen=set(); issues=[]
    for r in rows:
        season=str(r.get('season','')).strip(); week=str(r.get('week','')).strip()
        s=seasons[season];s['games']+=1;s['players'].add(r.get('player_id',''));s['weeks'].add(week)
        if not str(r.get('opponent_team') or '').strip():s['opponent_missing']+=1
        if not str(r.get('player_name') or '').strip():s['names_missing']+=1
        key=(season,week,r.get('player_id'))
        if key in seen:s['duplicate_keys']+=1
        seen.add(key)
    result=[]
    for season,s in sorted(seasons.items(),reverse=True):
        n=s['games'];weeks=sorted(s['weeks'],key=lambda x:int(x) if x.isdigit() else -1)
        result.append({'season':season,'player_games':n,'unique_players':len(s['players']),'weeks':weeks,'missing_opponents':s['opponent_missing'],'missing_opponent_pct':round(100*s['opponent_missing']/n,1) if n else 0,'missing_names':s['names_missing'],'duplicate_keys':s['duplicate_keys']})
    return {'total_player_games':len(rows),'season_reports':result,'note':'This is a structural data-quality audit, not independent verification of NFL statistical accuracy.'}
