import unittest
from unittest.mock import patch
from sync_history import sync,fetch

class SyncHistoryTests(unittest.TestCase):
 def test_invalid_range(self):
  with self.assertRaises(ValueError):sync(2025,2020)
 def test_all_seasons_fetched_before_merge(self):
  calls=[]
  def fake_fetch(y):calls.append(('fetch',y));return [{'season':str(y)}]
  with patch('sync_history.merge',side_effect=lambda rows: (calls.append(('merge',len(rows))) or {'seasons':[2024,2025]})),patch('sync_history.Path.write_text'):
   sync(2024,2025,fake_fetch)
  self.assertEqual(calls,[('fetch',2024),('fetch',2025),('merge',2)])
 def test_failed_fetch_does_not_merge(self):
  with patch('sync_history.merge') as merge:
   with self.assertRaises(RuntimeError):sync(2024,2025,lambda y: (_ for _ in ()).throw(RuntimeError('offline')) if y==2025 else [{'season':'2024'}])
   merge.assert_not_called()
 def test_http_rejected(self):
  with self.assertRaises(ValueError):fetch(2024,'http://example.org/{season}.csv')
if __name__=='__main__':unittest.main()
