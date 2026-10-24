import unittest
from model_optimization import optimize

class OptimizationTests(unittest.TestCase):
    def setUp(self):
        self.rows=[]
        for week in range(1,9):
            for name,points in [('A',10+week),('B',18-week)]:
                self.rows.append({'season':'2024','week':str(week),'player_id':name,
                                  'player_name':name,'position':'WR','recent_team':'NYJ',
                                  'opponent_team':'BUF','fantasy_points_ppr':str(points)})
    def test_empty(self):
        result=optimize([])
        self.assertEqual(result['samples'],0)
        self.assertIsNone(result['exploratory_best'])
    def test_paired_counts(self):
        result=optimize(self.rows,2024,3,5)
        self.assertEqual(result['samples'],10)
        self.assertEqual(len(result['variants']),6)
        self.assertEqual({v['n'] for v in result['variants']},{10})
    def test_future_games_not_used(self):
        a=optimize(self.rows,2024,3,5)
        # A later-season row cannot affect an earlier-season-only result.
        extra={'season':'2025','week':'1','player_id':'X','player_name':'X','position':'WR',
               'opponent_team':'BUF','fantasy_points_ppr':'99'}
        b=optimize(self.rows+[extra],2024,3,5)
        self.assertEqual(a['variants'],b['variants'])
    def test_invalid_window(self):
        with self.assertRaises(ValueError): optimize(self.rows,window=0)
    def test_missing_opponent_skipped(self):
        rows=[dict(r,opponent_team='') for r in self.rows]
        self.assertEqual(optimize(rows,2024)['samples'],0)
