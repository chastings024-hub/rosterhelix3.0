import unittest
from decision_backtest import backtest


def fixture():
    rows=[]
    for w in range(1,9):
        for player in ('A','B'):
            rows.append({'season':'2024','week':str(w),'player_id':player,
                         'player_name':player,'position':'WR',
                         'opponent_team':'BUF','fantasy_points_ppr':str(10+w)})
    return rows

class BacktestTests(unittest.TestCase):
    def test_no_early_predictions(self):
        result=backtest(fixture(),2024,min_prior=3)
        self.assertEqual(result['baseline']['n'],10)
        self.assertEqual(result['decision_engine']['n'],10)
    def test_empty(self):
        self.assertIsNone(backtest([])['mae_improvement'])
    def test_no_opponent(self):
        rows=fixture()
        for row in rows: row['opponent_team']=''
        self.assertEqual(backtest(rows)['baseline']['n'],0)
    def test_future_changes_do_not_change_earlier_week(self):
        rows=fixture()
        original=backtest(rows)['by_week'][0]
        rows[-1]['fantasy_points_ppr']='100'
        self.assertEqual(original,backtest(rows)['by_week'][0])
    def test_no_cross_season_history(self):
        rows=fixture()
        for row in fixture():
            copy=dict(row);copy['season']='2025';copy['week']='1';rows.append(copy)
        self.assertEqual(backtest(rows,2024)['baseline']['n'],10)
    def test_invalid_window(self):
        with self.assertRaises(ValueError):backtest(fixture(),window=0)
