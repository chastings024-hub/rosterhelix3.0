"""Historical fantasy comparison from imported weekly player-game rows."""
from collections import defaultdict

def player_averages(rows, season=None, window=5):
    if not 1 <= window <= 18:
        raise ValueError("Window must be 1–18 games")
    if not rows:
        return []
    if season is None:
        season = max(int(r["season"]) for r in rows)
    grouped = defaultdict(list)
    for r in rows:
        if int(r["season"]) != season or r.get("position") not in ("QB", "RB", "WR", "TE"):
            continue
        try:
            week = int(r["week"])
            points = float(r["fantasy_points_ppr"])
        except (KeyError, ValueError, TypeError):
            continue
        if not 1 <= week <= 18 or not -100 <= points <= 150:
            continue
        key = r.get("player_id") or r.get("player_name")
        if not key:
            continue
        grouped[key].append((week, points, r))
    result = []
    for pid, games in grouped.items():
        games.sort(key=lambda x: x[0])
        latest = games[-1][2]
        last = games[-window:]
        avg = sum(g[1] for g in last) / len(last)
        season_avg = sum(g[1] for g in games) / len(games)
        result.append({"id":pid, "name":latest.get("player_name",""), "position":latest.get("position",""),
                       "team":latest.get("recent_team",""), "season":season, "games":len(games),
                       "sample":len(last), "recent_average":round(avg,2),
                       "season_average":round(season_avg,2), "latest_week":games[-1][0]})
    return sorted(result, key=lambda x:(x["name"].lower(), x["id"]))
