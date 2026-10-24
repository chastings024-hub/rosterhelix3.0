import unittest,io,socket,urllib.error
from source_diagnostics import diagnose
class Response:
 status=200
 headers={'Content-Type':'text/csv'}
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def read(self,n):return b'season,week,player_id,position\n2024,1,abc,QB\n'
class DiagnosticsTests(unittest.TestCase):
 def test_success(self):
  r=diagnose(2024,resolver=lambda *args:True,opener=lambda *args,**kwargs:Response());self.assertTrue(r['ready'])
 def test_dns_failure(self):
  def fail(*args):raise socket.gaierror('DNS down')
  r=diagnose(2024,resolver=fail);self.assertFalse(r['ready']);self.assertEqual(r['dns'],'failed')
 def test_http_404(self):
  def fail(*args,**kwargs):raise urllib.error.HTTPError('url',404,'Not found',{},None)
  r=diagnose(2024,resolver=lambda *args:True,opener=fail);self.assertEqual(r['http'],404)
 def test_invalid_season(self):
  with self.assertRaises(ValueError):diagnose(1800)
if __name__=='__main__':unittest.main()
