"""Out-of-sample rolling evaluation with per-week and per-position error summaries."""
from collections import defaultdict
from backtest import evaluate
import math,statistics

def report(rows,scoring=1):
    base=evaluate(rows,scoring)
    def metrics(preds):
        if not preds:return {'n':0,'mae':None,'rmse':None,'bias':None}
        errors=[p['error'] for p in preds]
        return {'n':len(errors),'mae':round(statistics.mean(abs(e) for e in errors),3),'rmse':round(math.sqrt(statistics.mean(e*e for e in errors)),3),'bias':round(statistics.mean(errors),3)}
    groups=defaultdict(list)
    for p in base['predictions']:groups[(p['season'],p['week'])].append(p)
    return {'overall':base['overall'],'by_position':base['by_position'],'by_week':[{'season':s,'week':w,**metrics(g)} for (s,w),g in sorted(groups.items())], 'method':base['method'],'evaluates_matchup_adjustments':False,'evaluates_injury_adjustments':False,'warning':'These metrics test the baseline only, not matchup, injury or ROS predictions.'}
