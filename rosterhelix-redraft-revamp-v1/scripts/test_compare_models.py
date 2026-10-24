import unittest
from compare_models import compare

def row(week,pid,opp,pts,position='RB'):
 return {'season':'2024','week':str(week),'player_id':pid,'player_name':pid,'position':position,'opponent_team':opp,'fantasy_points_ppr':str(pts),'receptions':'0'}
class CompareTests(unittest.TestCase):
 def test_empty(self):
  self.assertEqual(compare([])['baseline']['n'],0)
 def test_two_prior_games_required(self):
  self.assertEqual(compare([row(1,'a','NYJ',10),row(2,'a','NYJ',20)])['baseline']['n'],0)
 def test_same_week_data_never_leaks(self):
  early=[row(1,'a','NYJ',10),row(2,'a','NYJ',20)]
  a=compare(early+[row(3,'a','NYJ',30)])
  b=compare(early+[row(3,'a','NYJ',30),row(3,'b','NYJ',100)])
  self.assertEqual(a['sample_predictions'][0]['adjusted'],b['sample_predictions'][0]['adjusted'])
 def test_paired_comparison(self):
  rows=[row(w,'a','NYJ',10+w) for w in range(1,6)]
  result=compare(rows)
  self.assertEqual(result['baseline']['n'],result['matchup_adjusted']['n'])
  self.assertEqual(result['baseline']['n'],3)
 def test_scoring(self):
  rows=[row(w,'a','NYJ',10+w) for w in range(1,5)]
  for r in rows:r['receptions']='2'
  self.assertNotEqual(compare(rows,1)['sample_predictions'][0]['actual'],compare(rows,0)['sample_predictions'][0]['actual'])
if __name__=='__main__':unittest.main()
