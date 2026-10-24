"""Walk-forward grid comparison; results are diagnostic, never automatically deployed."""
from collections import defaultdict
from math import sqrt
from statistics import mean
from decision_engine import estimate

VARIANTS = (
    ('season_average', 0.0, 0.0),
    ('recent_blend_25', 0.25, 0.0),
    ('recent_blend_50', 0.50, 0.0),
    ('recent_blend_75', 0.75, 0.0),
    ('recent_50_matchup_50', 0.50, 0.50),
    ('recent_50_matchup_100', 0.50, 1.00),
)


def optimize(rows, season=None, min_prior=3, window=5):
    if not 1 <= min_prior <= 17 or not 1 <= window <= 18:
        raise ValueError('Invalid lookback or minimum prior games')
    weeks=defaultdict(list)
    for r in rows:
        try:
            y,w=int(r['season']),int(r['week']); actual=float(r['fantasy_points_ppr'])
        except (ValueError, TypeError, KeyError):
            continue
        if season is not None and y!=season: continue
        if 1 <= w <= 18 and -100 <= actual <= 150 and r.get('position') in ('QB','RB','WR','TE'):
            weeks[(y,w)].append(r)
    previous=defaultdict(list)
    errors={name:[] for name,_,_ in VARIANTS}
    per_position=defaultdict(lambda: {name:[] for name,_,_ in VARIANTS})
    adjusted=0
    skipped=defaultdict(int)
    for (y,w),games in sorted(weeks.items()):
        history=previous[y]
        cache={}
        for game in games:
            opponent=(game.get('opponent_team') or '').strip().upper()
            if not opponent:
                skipped['missing_opponent']+=1;continue
            if opponent not in cache:
                cache[opponent]={p['id']:p for p in estimate(history,y,w,opponent,window)}
            player=cache[opponent].get(game.get('player_id') or game.get('player_name'))
            if player is None or player['games_before_week'] < min_prior:
                skipped['insufficient_history']+=1;continue
            actual=float(game['fantasy_points_ppr'])
            adjusted+=player['matchup_factor']!=1.0
            for name,recent_weight,matchup_strength in VARIANTS:
                base=recent_weight*player['recent_ppg']+(1-recent_weight)*player['season_ppg']
                factor=1+matchup_strength*(player['matchup_factor']-1)
                error=max(0,base*factor)-actual
                errors[name].append(error)
                per_position[game['position']][name].append(error)
        history.extend(games)
    def stats(err):
        return {'n':len(err),'mae':round(mean(abs(e) for e in err),3) if err else None,
                'rmse':round(sqrt(mean(e*e for e in err)),3) if err else None}
    variants=[{'id':name,'recent_weight':rw,'matchup_strength':ms,**stats(errors[name])}
              for name,rw,ms in VARIANTS]
    # Ranking on evaluation data is exploratory, not a deployment decision.
    ranked=sorted((v for v in variants if v['mae'] is not None),key=lambda v:v['mae'])
    return {'season':season,'window':window,'min_prior':min_prior,
            'samples':len(errors[VARIANTS[0][0]]),'matchup_adjusted_samples':adjusted,
            'variants':variants,'exploratory_best':ranked[0]['id'] if ranked else None,
            'by_position':{pos:[{'id':name,**stats(e[name])} for name,_,_ in VARIANTS]
                           for pos,e in sorted(per_position.items())},
            'skipped':dict(skipped),
            'warning':'Exploratory in-sample variant ranking. Selecting a winner on these games overfits; validate on held-out seasons before changing live estimates.'}
