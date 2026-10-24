"""Transparent, historical-only decision estimates; not calibrated forecasts."""
from collections import defaultdict
from statistics import mean

def estimate(rows, season, week, opponent=None, window=5):
    if not 1 <= week <= 18 or not 1 <= window <= 18:
        raise ValueError("Week and window must be 1–18")
    if opponent and (len(opponent)>4 or not opponent.isalpha()):
        raise ValueError("Opponent must be a team abbreviation")
    opponent=(opponent or "").upper()
    history=[]
    for r in rows:
        try:
            y,w=int(r["season"]),int(r["week"])
            pts=float(r["fantasy_points_ppr"])
        except (KeyError,ValueError,TypeError):
            continue
        if y==season and w<week and 1<=w<=18 and -100<=pts<=150 and r.get("position") in ("QB","RB","WR","TE"):
            history.append((w,pts,r))
    grouped=defaultdict(list)
    defense=defaultdict(list)
    for w,pts,r in history:
        pid=r.get("player_id") or r.get("player_name")
        if pid:grouped[pid].append((w,pts,r))
        opp=(r.get("opponent_team") or "").upper()
        if opp:defense[(opp,r["position"])].append(pts)
    position_baselines=defaultdict(list)
    for w,pts,r in history:
        position_baselines[r["position"]].append(pts)
    baselines={pos:mean(v) for pos,v in position_baselines.items()}
    result=[]
    for pid,games in grouped.items():
        games.sort(key=lambda x:x[0])
        recent=games[-window:]
        latest=games[-1][2]
        pos=latest["position"]
        recent_avg=mean(g[1] for g in recent)
        season_avg=mean(g[1] for g in games)
        # Shrink small recent samples toward season-long observed performance.
        weight=len(recent)/(len(recent)+3)
        baseline=weight*recent_avg+(1-weight)*season_avg
        def numeric_average(field):
            values=[]
            for _,_,r in recent:
                try:
                    if r.get(field) not in ("",None):
                        values.append(float(r[field]))
                except (ValueError,TypeError):
                    pass
            return round(mean(values),2) if values else None
        targets=numeric_average("receiving_targets")
        carries=numeric_average("rushing_attempts")
        # Opponent factor is conservative, and only available with sufficient observed samples.
        factor=1.0
        opp_games=defense.get((opponent,pos),[]) if opponent else []
        pos_mean=baselines.get(pos,0)
        if len(opp_games)>=8 and pos_mean>0:
            raw=mean(opp_games)/pos_mean
            factor=max(.85,min(1.15,1+(raw-1)*len(opp_games)/(len(opp_games)+20)))
        estimate_points=round(max(0,baseline*factor),2)
        result.append({"id":pid,"name":latest.get("player_name",""),"team":latest.get("recent_team",""),
                       "position":pos,"games_before_week":len(games),"recent_games":len(recent),
                       "recent_ppg":round(recent_avg,2),"season_ppg":round(season_avg,2),
                       "targets_pg":targets,"carries_pg":carries,"opponent":opponent or None,
                       "opponent_sample":len(opp_games),"matchup_factor":round(factor,3),
                       "estimate":estimate_points,"confidence":"limited" if len(games)<4 else "historical"})
    return sorted(result,key=lambda r:(-r["estimate"],r["name"]))
