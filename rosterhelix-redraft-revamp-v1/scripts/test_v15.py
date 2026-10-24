import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from update_data import normalize
class ImportNameTests(unittest.TestCase):
 def test_full_name_fallback(self):
  data=b"season,week,position,player_id,full_name,season_type,recent_team,opponent_team,receptions\n2025,1,WR,abc,Example Receiver,REG,NYJ,BUF,0\n"
  rows=normalize(data,2025)
  self.assertEqual(rows[0]["player_name"],"Example Receiver")
  self.assertEqual(rows[0]["receptions"],"0")
 def test_display_name_priority(self):
  data=b"season,week,position,player_id,player_display_name,full_name,season_type\n2025,1,QB,abc,Display Name,Alternate Name,REG\n"
  self.assertEqual(normalize(data,2025)[0]["player_name"],"Display Name")
if __name__=="__main__":unittest.main()
