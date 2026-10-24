"""Leakage-safe walk-forward evaluation of the V22 decision engine.

For each target week, the estimator receives only earlier weeks of the same
season. Compare its matchup-adjusted prediction to the exact same prediction
with matchup factor 1.0, on identical player-games.
"""
from collections import defaultdict
from math import sqrt
from statistics import mean
from decision_engine import estimate


def _metrics(errors):
    return {'n': len(errors), 'mae': round(mean(abs(e) for e in errors), 3) if errors else None,
            'rmse': round(sqrt(mean(e * e for e in errors)), 3) if errors else None,
            'bias': round(mean(errors), 3) if errors else None}


def backtest(rows, season=None, min_prior=3, window=5):
    if not 1 <= window <= 18 or not 1 <= min_prior <= 17:
        raise ValueError('Invalid lookback or minimum history')
    weeks = defaultdict(list)
    for r in rows:
        try:
            year, week = int(r['season']), int(r['week'])
            actual = float(r['fantasy_points_ppr'])
        except (KeyError, TypeError, ValueError):
            continue
        if season is not None and year != season:
            continue
        if not 1 <= week <= 18 or not -100 <= actual <= 150:
            continue
        if r.get('position') not in ('QB', 'RB', 'WR', 'TE'):
            continue
        weeks[(year, week)].append(r)
    history_by_year = defaultdict(list)
    overall = [[], []]
    by_pos = defaultdict(lambda: [[], []])
    by_week = defaultdict(lambda: [[], []])
    evaluated = 0
    adjusted = 0
    skipped = defaultdict(int)
    for (year, week), games in sorted(weeks.items()):
        earlier = history_by_year[year]
        # Only previous weeks are used to compute any player or defense metric.
        cache = {}
        for game in games:
            opponent = (game.get('opponent_team') or '').strip().upper()
            if not opponent:
                skipped['missing_opponent'] += 1
                continue
            if opponent not in cache:
                cache[opponent] = {p['id']: p for p in estimate(earlier, year, week, opponent, window)}
            pid = game.get('player_id') or game.get('player_name')
            pred = cache[opponent].get(pid)
            if pred is None or pred['games_before_week'] < min_prior:
                skipped['insufficient_history'] += 1
                continue
            actual = float(game['fantasy_points_ppr'])
            # Baseline is the same shrunk player average, without opponent factor.
            weight = pred['recent_games'] / (pred['recent_games'] + 3)
            baseline = weight * pred['recent_ppg'] + (1 - weight) * pred['season_ppg']
            base_error = baseline - actual
            model_error = pred['estimate'] - actual
            overall[0].append(base_error)
            overall[1].append(model_error)
            by_pos[game['position']][0].append(base_error)
            by_pos[game['position']][1].append(model_error)
            by_week[(year, week)][0].append(base_error)
            by_week[(year, week)][1].append(model_error)
            evaluated += 1
            adjusted += pred['matchup_factor'] != 1.0
        earlier.extend(games)
    base, model = map(_metrics, overall)
    return {'source': 'locally imported game logs; authenticity unverified',
            'method': 'paired, season-isolated walk-forward; previous weeks only',
            'season': season, 'min_prior_games': min_prior, 'window': window,
            'baseline': base, 'decision_engine': model,
            'mae_improvement': round(base['mae'] - model['mae'], 3) if evaluated else None,
            'matchup_adjusted_samples': adjusted, 'skipped': dict(skipped),
            'by_position': {p: {'baseline': _metrics(v[0]), 'decision_engine': _metrics(v[1])}
                            for p, v in sorted(by_pos.items())},
            'by_week': [{'season': y, 'week': w, 'baseline': _metrics(v[0]),
                         'decision_engine': _metrics(v[1])}
                        for (y, w), v in sorted(by_week.items())],
            'warning': 'Retrospective error is not a guarantee of future accuracy; no injuries or live news included.'}
