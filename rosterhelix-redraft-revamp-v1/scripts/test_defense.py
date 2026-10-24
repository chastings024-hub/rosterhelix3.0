import unittest
from build_defense import build
from build_matchups import report
class DefenseTests(unittest.TestCase):
 def test_grouping(self):
  rows=[{'season':'2026','week':'1','opponent_team':'NYJ','position':'WR','fantasy_points_ppr':'10'}, {'season':'2026','week':'1','opponent_team':'NYJ','position':'WR','fantasy_points_ppr':'5'}, {'season':'2026','week':'1','opponent_team':'BUF','position':'WR','fantasy_points_ppr':'20'}]
  result=build(rows)
  self.assertEqual(len(result),2)
  self.assertEqual(next(x for x in result if x['defense_team']=='NYJ')['points_allowed'],15)
  self.assertEqual(next(x for x in result if x['defense_team']=='NYJ')['league_avg_points'],17.5)
 def test_future_leakage(self):
  rows=[{'season':'2026','week':'1','defense_team':'NYJ','position':'WR','points_allowed':'10','league_avg_points':'20'},{'season':'2026','week':'2','defense_team':'NYJ','position':'WR','points_allowed':'100','league_avg_points':'20'}]
  v=report(rows,2026,2)['teams']['NYJ']['WR'];self.assertEqual(v['games'],1);self.assertLess(v['factor'],1)
if __name__=='__main__':unittest.main()
