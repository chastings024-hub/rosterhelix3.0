import unittest
from decision_engine import estimate

class DecisionTests(unittest.TestCase):
 def setUp(self):
  self.rows=[dict(season='2024',week=str(w),player_id='a',player_name='Alpha',position='WR',recent_team='BUF',fantasy_points_ppr=str(w*10),opponent_team='NYJ',receiving_targets='8',rushing_attempts='0') for w in range(1,5)]
 def test_no_future_leakage(self):
  p=estimate(self.rows,2024,3)[0]
  self.assertEqual(p['games_before_week'],2)
  self.assertEqual(p['recent_ppg'],15)
 def test_empty_first_week(self):self.assertEqual(estimate(self.rows,2024,1),[])
 def test_usage(self):self.assertEqual(estimate(self.rows,2024,5)[0]['targets_pg'],8)
 def test_bad_week(self):
  with self.assertRaises(ValueError):estimate(self.rows,2024,19)
 def test_sparse_opponent_neutral(self):self.assertEqual(estimate(self.rows,2024,5,'NYJ')[0]['matchup_factor'],1)
