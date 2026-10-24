import unittest
from backtest import estimate,evaluate
class TestModel(unittest.TestCase):
 def test_future_excluded(self):
  rows=[{'player_id':'a','position':'WR','season':'2025','week':str(i),'fantasy_points_ppr':str(v),'receptions':'0'} for i,v in enumerate([10,12,14,100],1)]
  result=evaluate(rows)
  self.assertEqual(result['overall']['n'],2)
  self.assertAlmostEqual(result['predictions'][0]['prediction'],estimate(rows[:2],'WR'),places=3)
 def test_missing_data(self):self.assertIsNone(estimate([{'fantasy_points_ppr':'10'}],'WR'))
 def test_score(self):self.assertAlmostEqual(estimate([{'fantasy_points_ppr':'20','receptions':'5'}]*2,'WR',0),15)
if __name__=='__main__':unittest.main()
