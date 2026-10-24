import unittest
from matchup_engine import matchup_factor
class MatchupTests(unittest.TestCase):
 def test_no_future_leak(self):
  rows=[dict(season='2026',week='3',defense_team='NYJ',position='WR',points_allowed='30',league_avg_points='20'),dict(season='2026',week='4',defense_team='NYJ',position='WR',points_allowed='200',league_avg_points='20')]
  a=matchup_factor(rows,2026,4,'NYJ','WR');self.assertEqual(a['games'],1);self.assertLess(a['factor'],1.1)
 def test_neutral_missing(self):self.assertEqual(matchup_factor([],2026,8,'NYJ','QB')['factor'],1)
 def test_capped(self):
  rows=[dict(season='2025',week=str(i),defense_team='NYJ',position='RB',points_allowed='100',league_avg_points='10') for i in range(1,15)]
  self.assertEqual(matchup_factor(rows,2026,1,'NYJ','RB')['factor'],1.2)
if __name__=='__main__':unittest.main()
