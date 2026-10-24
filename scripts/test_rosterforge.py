import unittest,tempfile
from pathlib import Path
from roster_workspace import validate,save,load
from research_hub import profiles,insights

ROWS=[{'player_id':'p1','player_name':'A','position':'WR','recent_team':'NYJ','season':'2024','week':str(w),'fantasy_points_ppr':str(w*4),'receiving_targets':'8','rushing_attempts':'0','opponent_team':'BUF'} for w in range(1,5)] + [{'player_id':'p2','player_name':'B','position':'RB','recent_team':'BUF','season':'2024','week':'1','fantasy_points_ppr':'12','receiving_targets':'1','rushing_attempts':'15','opponent_team':'NYJ'}]
class WorkspaceTests(unittest.TestCase):
 def test_default(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(load(Path(d)/'roster.json')['scoring'],'ppr')
 def test_roundtrip(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'roster.json';data={'league_name':'test','scoring':'half','players':[{'id':'p1','name':'A','position':'WR','team':'NYJ'}]}
   save(path,data);self.assertEqual(load(path)['players'][0]['id'],'p1')
 def test_duplicates(self):
  with self.assertRaisesRegex(ValueError,'Duplicate'):validate({'players':[{'id':'p1','name':'A','position':'WR'}]*2})
 def test_bad_slots(self):
  with self.assertRaises(ValueError):validate({'slots':{'QB':100}})
 def test_bad_scoring(self):
  with self.assertRaises(ValueError):validate({'scoring':'bogus'})
 def test_invalid_position(self):
  with self.assertRaises(ValueError):validate({'players':[{'id':'p1','name':'A','position':'X'}]})
 def test_profile(self):
  p=profiles(ROWS);self.assertEqual(len(p),2);self.assertEqual(next(x for x in p if x['id']=='p1')['recent_ppg'],10.0);self.assertEqual(len(next(x for x in p if x['id']=='p1')['logs']),4)
 def test_missing_history(self):self.assertEqual(profiles([]),[])
 def test_lineup(self):
  roster=validate({'players':[{'id':'p1','name':'A','position':'WR'},{'id':'p2','name':'B','position':'RB'}]})
  x=insights(ROWS,roster);self.assertEqual(len(x['starters']),2);self.assertEqual(x['missing'],[])
 def test_missing_player(self):
  roster=validate({'players':[{'id':'missing','name':'Unknown','position':'QB'}]})
  self.assertEqual(insights(ROWS,roster)['missing'],['Unknown'])
if __name__=='__main__':unittest.main()
