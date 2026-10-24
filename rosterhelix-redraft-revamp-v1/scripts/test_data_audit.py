import unittest
from data_audit import audit
class AuditTests(unittest.TestCase):
 def test_empty(self):
  self.assertEqual(audit([])['season_reports'],[])
 def test_counts_and_missing(self):
  rows=[dict(season='2024',week='1',player_id='a',player_name='A',opponent_team='NYJ'),dict(season='2024',week='2',player_id='a',player_name='A',opponent_team='')]
  r=audit(rows)['season_reports'][0]
  self.assertEqual(r['missing_opponent_pct'],50)
  self.assertEqual(r['unique_players'],1)
  self.assertEqual(r['weeks'],['1','2'])
 def test_duplicates(self):
  row=dict(season='2025',week='1',player_id='a',player_name='A',opponent_team='DAL')
  self.assertEqual(audit([row,row])['season_reports'][0]['duplicate_keys'],1)
if __name__=='__main__':unittest.main()
