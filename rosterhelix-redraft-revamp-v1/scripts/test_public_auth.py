"""Unit tests for user isolation and credential handling."""
import unittest,tempfile,os
from pathlib import Path
from unittest.mock import patch
from scripts import public_auth as auth

class PublicAuthTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=auth.DB;auth.DB=Path(self.tmp.name)/'test.sqlite'
 def tearDown(self):
  auth.DB=self.old;self.tmp.cleanup()
 def test_registration_and_session(self):
  token,csrf=auth.register('ONE@EXAMPLE.COM','a very strong password')
  user=auth.session(token);self.assertEqual(user['email'],'one@example.com');self.assertEqual(user['csrf'],csrf)
  auth.logout(token);self.assertIsNone(auth.session(token))
 def test_wrong_password_and_short_password(self):
  with self.assertRaises(ValueError):auth.register('a@example.com','short')
  auth.register('a@example.com','a very strong password')
  with self.assertRaises(ValueError):auth.login('a@example.com','wrong password')
 def test_user_roster_isolation(self):
  one,_=auth.register('one@example.com','a very strong password')
  two,_=auth.register('two@example.com','a very strong password')
  u1=auth.session(one)['id'];u2=auth.session(two)['id']
  auth.save_workspace(u1,{'league_name':'Only one','players':[]})
  self.assertEqual(auth.workspace(u1)['league_name'],'Only one')
  self.assertEqual(auth.workspace(u2)['league_name'],'My League')
 def test_rate_limit(self):
  self.assertTrue(auth.rate_limit('ip',2))
  self.assertTrue(auth.rate_limit('ip',2))
  self.assertFalse(auth.rate_limit('ip',2))
