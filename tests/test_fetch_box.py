"""Offline check of the ESPN parser against a real Oct 16 2026 box score (MIA @ ORL, trimmed)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bbl"))
from fetch_box import rows_from_summary
KEYS = ["minutes","points","fieldGoalsMade-fieldGoalsAttempted","threePointFieldGoalsMade-threePointFieldGoalsAttempted",
        "freeThrowsMade-freeThrowsAttempted","rebounds","assists","turnovers","steals","blocks","offensiveRebounds",
        "defensiveRebounds","fouls","plusMinus"]
SUMMARY = {"boxscore": {"players": [
  {"team": {"abbreviation": "ORL"}, "statistics": [{"keys": KEYS, "athletes": [
    {"didNotPlay": False, "stats": ["26","24","5-11","1-2","13-16","7","4","1","0","1","3","4","1","+9"],
     "athlete": {"displayName": "Paolo Banchero", "position": {"abbreviation": "F"}}},
    {"didNotPlay": True, "stats": [], "athlete": {"displayName": "Anthony Black", "position": {"abbreviation": "G"}}}]}]},
  {"team": {"abbreviation": "MIA"}, "statistics": [{"keys": KEYS, "athletes": [
    {"didNotPlay": False, "stats": ["30","21","9-17","3-7","0-0","1","7","4","1","0","0","1","4","-20"],
     "athlete": {"displayName": "Ryan Conwell", "position": {"abbreviation": "G"}}}]}]}]}}
rows = rows_from_summary(SUMMARY)
assert rows == ["Paolo Banchero|ORL|26|24|5|11|1|2|13|16|7|4|1|0|1|1|F",
                "Ryan Conwell|MIA|30|21|9|17|3|7|0|0|1|7|4|1|0|4|G"], rows
print("fetch_box parser OK:", len(rows), "players, DNP skipped")
