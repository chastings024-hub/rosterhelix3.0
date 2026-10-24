"""Three-stage validation: season holdout, position audit, and downloadable report."""
from collections import defaultdict
from math import sqrt
from statistics import mean
from model_optimization import optimize, VARIANTS


def evaluate(rows, train_end, test_start, test_end, min_prior=3, window=5):
    if not (1999 <= train_end < test_start <= test_end <= 2100):
        raise ValueError('Training must end before held-out test seasons begin (1999–2100)')
    if not (1 <= min_prior <= 17 and 1 <= window <= 18):
        raise ValueError('Invalid minimum prior games or recent window')
    training = [r for r in rows if _year(r) is not None and _year(r) <= train_end]
    test = [r for r in rows if _year(r) is not None and test_start <= _year(r) <= test_end]
    train_result = optimize(training, min_prior=min_prior, window=window)
    candidates = [v for v in train_result['variants'] if v['mae'] is not None and v['n'] >= 20]
    chosen = min(candidates, key=lambda v:(v['mae'],v['id'])) if candidates else None
    test_result = optimize(test, min_prior=min_prior, window=window)
    variant_lookup = {v['id']:v for v in test_result['variants']}
    chosen_test = variant_lookup.get(chosen['id']) if chosen else None
    baseline = variant_lookup.get('season_average')
    position_results = []
    for position, variants in sorted(test_result['by_position'].items()):
        lookup = {v['id']:v for v in variants}
        selected = lookup.get(chosen['id']) if chosen else None
        reference = lookup.get('season_average')
        position_results.append({'position':position, 'selected':selected, 'baseline':reference,
             'mae_improvement':round(reference['mae']-selected['mae'],3) if selected and reference and selected['mae'] is not None and reference['mae'] is not None else None})
    improvement = round(baseline['mae']-chosen_test['mae'],3) if chosen_test and baseline and chosen_test['mae'] is not None and baseline['mae'] is not None else None
    warnings=[]
    if chosen is None:warnings.append('Insufficient training observations to select a model (minimum 20).')
    if not chosen_test or chosen_test['n'] < 50:warnings.append('Held-out sample is small; do not treat this as a validated improvement.')
    if train_end+1 < test_start:warnings.append('There is a gap between training and test seasons.')
    if improvement is not None and improvement < 0:warnings.append('Selected strategy underperformed the season-average baseline on held-out games.')
    return {'method':'Train-only model selection, held-out future-season evaluation; within each season only previous weeks inform estimates',
            'train_end':train_end,'test_start':test_start,'test_end':test_end,'window':window,'min_prior':min_prior,
            'selected_strategy':chosen['id'] if chosen else None,'training_samples':chosen['n'] if chosen else 0,
            'training_mae':chosen['mae'] if chosen else None,'test_samples':chosen_test['n'] if chosen_test else 0,
            'test_mae':chosen_test['mae'] if chosen_test else None,'baseline_mae':baseline['mae'] if baseline else None,
            'heldout_mae_improvement':improvement,'positions':position_results,
            'test_variants':test_result['variants'],'train_variants':train_result['variants'],
            'warnings':warnings,
            'limitations':'Data source not independently verified; within-season training history is observed past games, no live injuries or depth charts; variant selection uses earlier seasons only.'}

def _year(r):
    try:return int(r['season'])
    except (KeyError,ValueError,TypeError):return None
