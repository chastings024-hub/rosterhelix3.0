import unittest
from build_schedule import normalize
from projection_engine import project,upcoming_opponent
class ScheduleProjectionTests(unittest.TestCase):
 def test_schedule(self):
  data=b'season,week,game_type,home_team,away_team,gameday\n2026,7,REG,NYJ,BUF,2026-10-20\n2026,8,REG,BUF,NYJ,2026-10-27\n2026,8,WC,KC,LV,2026-10-27\n'
  rows=normalize(data,2026);self.assertEqual(len(rows),2);self.assertEqual(upcoming_opponent(rows,2026,8,'NYJ'),'BUF')
 def test_no_future_leakage(self):
  games=[dict(season='2026',week=str(w),player_id='a',player_name='A',recent_team='NYJ',position='WR',fantasy_points_ppr=str(p),receptions='0') for w,p in [(1,10),(2,20),(8,1000)]]
  schedule=[dict(season='2026',week='3',home_team='BUF',away_team='NYJ')]
  defense=[dict(season='2026',week='1',defense_team='BUF',position='WR',points_allowed='30',league_avg_points='20'),dict(season='2026',week='3',defense_team='BUF',position='WR',points_allowed='10000',league_avg_points='20')]
  result=project(games,schedule,defense,2026,3)[0]
  self.assertAlmostEqual(result['baseline'],16.67,places=2);self.assertTrue(result['matchup_adjusted']);self.assertLess(result['matchup_factor'],1.2)
 def test_bye_not_zero_projection(self):
  games=[dict(season='2026',week='1',player_id='a',player_name='A',recent_team='NYJ',position='WR',fantasy_points_ppr='12',receptions='1')]
  schedule=[dict(season='2026',week='2',home_team='BUF',away_team='MIA')]
  r=project(games,schedule,[],2026,2)[0];self.assertIsNone(r['projection']);self.assertEqual(r['baseline'],12)
 def test_no_schedule_still_baseline(self):
  games=[dict(season='2026',week='1',player_id='a',player_name='A',recent_team='NYJ',position='WR',fantasy_points_ppr='12',receptions='1')]
  r=project(games,[],[],2026,2)[0];self.assertEqual(r['projection'],12);self.assertFalse(r['bye'])
if __name__=='__main__':unittest.main()
