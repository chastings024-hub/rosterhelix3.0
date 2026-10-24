import unittest
from validation_suite import evaluate
class ValidationSuiteTests(unittest.TestCase):
 def test_invalid_overlapping_years(self):
  with self.assertRaises(ValueError):evaluate([],2024,2024,2025)
 def test_invalid_reverse_years(self):
  with self.assertRaises(ValueError):evaluate([],2024,2025,2023)
 def test_empty_dataset(self):
  r=evaluate([],2022,2023,2024)
  self.assertIsNone(r['selected_strategy'])
  self.assertTrue(r['warnings'])
 def test_small_dataset(self):
  rows=[]
  for season in (2022,2023):
   for week in range(1,9):
    rows.append(dict(season=str(season),week=str(week),player_id='p',player_name='Player',position='RB',opponent_team='NYJ',fantasy_points_ppr=str(week+5)))
  r=evaluate(rows,2022,2023,2023,min_prior=2)
  self.assertEqual(r['test_start'],2023)
  self.assertEqual(r['training_samples'],0) # fewer than 20 observations
