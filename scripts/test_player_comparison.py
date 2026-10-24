import unittest
from player_comparison import player_averages

class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.rows=[
          {"season":"2024","week":"1","player_id":"a","player_name":"A","position":"WR","recent_team":"NYJ","fantasy_points_ppr":"10"},
          {"season":"2024","week":"2","player_id":"a","player_name":"A","position":"WR","recent_team":"NYJ","fantasy_points_ppr":"20"},
          {"season":"2023","week":"1","player_id":"a","player_name":"A","position":"WR","recent_team":"NYJ","fantasy_points_ppr":"100"},
          {"season":"2024","week":"1","player_id":"b","player_name":"B","position":"RB","recent_team":"BUF","fantasy_points_ppr":"8"}]
    def test_latest_season(self):
        p=player_averages(self.rows)
        self.assertEqual(len(p),2)
        self.assertEqual(p[0]["recent_average"],15)
    def test_window(self):
        self.assertEqual(player_averages(self.rows,2024,1)[0]["recent_average"],20)
    def test_season_filter(self):
        self.assertEqual(player_averages(self.rows,2023)[0]["recent_average"],100)
    def test_invalid_window(self):
        with self.assertRaises(ValueError):player_averages(self.rows,window=0)
