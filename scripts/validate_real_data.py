#!/usr/bin/env python3
"""Auditable validation of imported real NFL player-week statistics.

Never reports sample fixtures as real NFL observations. Outputs provenance,
coverage, duplicate checks, and strictly walk-forward baseline accuracy.
"""
import argparse, csv, datetime, hashlib, json, pathlib, sys
from collections import Counter
from backtest import evaluate

ROOT=pathlib.Path(__file__).resolve().parents[1]
REQUIRED={'player_id','player_name','position','season','week','fantasy_points_ppr','receptions'}
POSITIONS={'QB','RB','WR','TE'}

def audit(path, source='unverified', expected_season=None):
    path=pathlib.Path(path)
    with path.open(encoding='utf-8-sig',newline='') as handle:
        reader=csv.DictReader(handle)
        fields=set(reader.fieldnames or [])
        missing=sorted(REQUIRED-fields)
        if missing:raise ValueError('Missing required columns: '+', '.join(missing))
        rows=list(reader)
    if not rows:raise ValueError('Empty player dataset')
    errors=[]; keys=set(); duplicates=[]; valid=[]; positions=Counter(); seasons=Counter(); weeks=Counter()
    for line,row in enumerate(rows,2):
        try:
            season=int(row['season']);week=int(row['week']);points=float(row['fantasy_points_ppr']);rec=float(row['receptions'] or 0)
            if not (1999<=season<=datetime.date.today().year and 1<=week<=18 and -100<=points<=150 and 0<=rec<=40):raise ValueError('out-of-range season/week/points/receptions')
            if row['position'] not in POSITIONS or not row['player_id'].strip():raise ValueError('missing player ID or unsupported position')
            if expected_season is not None and season!=expected_season:raise ValueError('unexpected season')
        except (ValueError,TypeError) as exc:
            errors.append({'line':line,'reason':str(exc)});continue
        key=(season,week,row['player_id'])
        if key in keys:duplicates.append({'line':line,'key':list(key)})
        keys.add(key);valid.append(row);positions[row['position']]+=1;seasons[season]+=1;weeks[f'{season}-W{week:02}']+=1
    if not valid:raise ValueError('No valid player-week rows')
    result=evaluate(valid)
    sha=hashlib.sha256(path.read_bytes()).hexdigest()
    report={'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'source_label':source,'source_verified':source=='nflverse-import',
            'input_file':str(path),'sha256':sha,'total_rows':len(rows),
            'valid_rows':len(valid),'invalid_rows':len(errors),'duplicate_player_weeks':len(duplicates),
            'invalid_examples':errors[:15],'duplicate_examples':duplicates[:15],
            'seasons':dict(sorted(seasons.items())),'positions':dict(sorted(positions.items())),
            'weeks':dict(sorted(weeks.items())),
            'baseline_accuracy':{'overall':result['overall'],'by_position':result['by_position'],
              'method':result['method']},
            'warnings':['This tests the recent-game baseline, not opponent, injury or ROS adjustments.',
              'Player-weeks are not independent samples; MAE is descriptive, not a confidence interval.'],
            'pass':not errors and not duplicates and result['overall']['n']>0}
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',default=str(ROOT/'data/player_stats.csv'))
    p.add_argument('--output',default=str(ROOT/'data/validation_report.json'))
    p.add_argument('--source',default='unverified',choices=['unverified','nflverse-import'])
    p.add_argument('--season',type=int);a=p.parse_args()
    report=audit(a.input,a.source,a.season)
    dest=pathlib.Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('weeks','invalid_examples','duplicate_examples')},indent=2))
    sys.exit(0 if report['pass'] else 2)
if __name__=='__main__':main()
