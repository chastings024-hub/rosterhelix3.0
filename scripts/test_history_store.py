import unittest,tempfile
from unittest.mock import patch
from pathlib import Path
import history_store as h
CSV=b'player_id,player_name,position,recent_team,opponent_team,season,week,fantasy_points_ppr,receptions,receiving_targets,rushing_attempts\na,Test A,WR,NYG,DAL,2025,1,14.2,4,7,0\na,Test A,WR,NYG,PHI,2025,2,20,5,8,0\nb,Test B,RB,NYG,DAL,2025,1,12,2,2,14\n'
class HistoryTest(unittest.TestCase):
 def test_parse(self):self.assertEqual(len(h.parse(CSV)),3)
 def test_reject_duplicate(self):
  with self.assertRaises(ValueError):h.parse(CSV+CSV.splitlines()[1]+b'\n')
 def test_matchups(self):
  rows=h.parse(CSV);m=h.matchups(rows,2025,'DAL');self.assertEqual(len(m),2);self.assertEqual({r['position'] for r in m},{'WR','RB'})
 def test_query(self):self.assertEqual(len(h.query(h.parse(CSV),2025,'Test A',opponent='DAL')),1)
 def test_merge(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   with patch.object(h,'DATA',root),patch.object(h,'HISTORY',root/'history_player_stats.csv'):
    h.merge(h.parse(CSV));meta=h.merge(h.parse(CSV));self.assertEqual(meta['history_rows'],3)
if __name__=='__main__':unittest.main()
