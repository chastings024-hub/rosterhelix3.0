import unittest
from advanced_engine import opportunity,apply_scenario,rest_of_season,trade_sides
from model_accuracy import report

class AdvancedTests(unittest.TestCase):
 def setUp(self):
  self.rows=[{'player_id':'a','player_name':'Alpha','position':'RB','recent_team':'NYJ','season':'2026','week':str(w),'fantasy_points_ppr':str(10+w),'receptions':'2','receiving_targets':'3','rushing_attempts':'12'} for w in (1,2,3)]
  self.schedule=[{'season':'2026','week':'4','home_team':'NYJ','away_team':'BUF'},{'season':'2026','week':'5','home_team':'BUF','away_team':'NYJ'}]
 def test_opportunity_prior_only(self):
  self.assertEqual(opportunity(self.rows,2026,3)['a']['games'],2)
  self.assertEqual(opportunity(self.rows,2026,3)['a']['opportunities_per_game'],15)
 def test_unknown_missing_usage(self):
  self.assertIsNone(opportunity(self.rows,2026,4)['a']['snap_share'])
 def test_injury_scenario(self):
  result=apply_scenario([{'projection':12}],status='out');self.assertEqual(result[0]['availability_weighted_projection'],0)
  self.assertEqual(result[0]['conditional_projection'],12)
 def test_bad_availability(self):
  with self.assertRaises(ValueError):apply_scenario([{'projection':12}],availability=1.5)
 def test_ros_schedule(self):
  result=rest_of_season(self.rows,self.schedule,[],2026,4)
  self.assertEqual(result[0]['scheduled_games'],2)
  self.assertIn(6,result[0]['missing_schedule_weeks'])
 def test_roster_trade(self):
  players=[{'id':'a','position':'RB','ros_total':20},{'id':'b','position':'RB','ros_total':40},{'id':'c','position':'RB','ros_total':10},{'id':'d','position':'RB','ros_total':15}]
  outcome=trade_sides(players,['a'],['b'],['a','c'],['b','d'],{'RB':1,'FLEX':0})
  self.assertEqual(outcome['team_a']['delta'],20)
 def test_accuracy_walk_forward(self):
  result=report(self.rows);self.assertEqual(result['overall']['n'],1)
  self.assertFalse(result['evaluates_matchup_adjustments'])
if __name__=='__main__':unittest.main()
