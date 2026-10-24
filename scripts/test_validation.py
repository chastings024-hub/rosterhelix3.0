import csv,pathlib,tempfile,unittest
from validate_real_data import audit

class ValidationTests(unittest.TestCase):
 def write(self,rows):
  t=tempfile.TemporaryDirectory();path=pathlib.Path(t.name)/'player.csv'
  with path.open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=['player_id','player_name','position','season','week','fantasy_points_ppr','receptions']);w.writeheader();w.writerows(rows)
  return t,path
 def sample(self):return [dict(player_id='id1',player_name='Fixture Player',position='RB',season=2025,week=i,fantasy_points_ppr=i*2,receptions=2) for i in range(1,5)]
 def test_walk_forward_and_coverage(self):
  t,p=self.write(self.sample())
  try:
   r=audit(p);self.assertEqual(r['baseline_accuracy']['overall']['n'],2);self.assertTrue(r['pass']);self.assertFalse(r['source_verified'])
  finally:t.cleanup()
 def test_duplicate_detection(self):
  rows=self.sample();rows.append(rows[0].copy());t,p=self.write(rows)
  try:self.assertEqual(audit(p)['duplicate_player_weeks'],1)
  finally:t.cleanup()
 def test_bad_week_detection(self):
  rows=self.sample();rows[0]['week']=20;t,p=self.write(rows)
  try:self.assertEqual(audit(p)['invalid_rows'],1)
  finally:t.cleanup()
 def test_missing_schema(self):
  t=tempfile.TemporaryDirectory();p=pathlib.Path(t.name)/'x.csv';p.write_text('player_id,week\na,1\n')
  try:
   with self.assertRaises(ValueError):audit(p)
  finally:t.cleanup()
if __name__=='__main__':unittest.main()
