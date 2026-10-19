#!/usr/bin/env python3
"""Download one night's NBA box scores from ESPN's public scoreboard API.

Usage: python3 fetch_box.py YYYYMMDD OUT.txt
Output (what nightly.py reads):
  first line  #games|completed|in_progress
  then one line per player who played:
  name|team|min|pts|fgm|fga|tpm|tpa|ftm|fta|reb|ast|to|stl|blk|pf|espn_position
Only finished games are included. No login or API key is needed.
"""
import json, sys, time, urllib.request

BASE = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) bbl-best-worst"}


def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # network hiccup: wait and retry
            if i == tries - 1:
                raise SystemExit(f"Couldn't reach ESPN ({e}). Check your internet connection and try again.")
            time.sleep(2 * (i + 1))


def split(s):
    a, _, b = (s or "0-0").partition("-")
    return a or "0", b or "0"


def rows_from_summary(g):
    out = []
    for team in (g.get("boxscore") or {}).get("players") or []:
        ab = team["team"]["abbreviation"]
        st = team["statistics"][0]
        keys = st["keys"]
        for a in st["athletes"]:
            if a.get("didNotPlay") or not a.get("stats"):
                continue
            v = dict(zip(keys, a["stats"]))
            fgm, fga = split(v.get("fieldGoalsMade-fieldGoalsAttempted"))
            tpm, tpa = split(v.get("threePointFieldGoalsMade-threePointFieldGoalsAttempted"))
            ftm, fta = split(v.get("freeThrowsMade-freeThrowsAttempted"))
            pos = ((a.get("athlete") or {}).get("position") or {}).get("abbreviation", "")
            out.append("|".join(str(x) for x in [
                a["athlete"]["displayName"], ab, v.get("minutes", "0"), v.get("points", "0"),
                fgm, fga, tpm, tpa, ftm, fta, v.get("rebounds", "0"), v.get("assists", "0"),
                v.get("turnovers", "0"), v.get("steals", "0"), v.get("blocks", "0"), v.get("fouls", "0"), pos]))
    return out


def fetch(date):
    sb = get(f"{BASE}/scoreboard?dates={date}")
    ev = sb.get("events") or []
    done = [e for e in ev if (((e.get("status") or {}).get("type") or {}).get("completed"))]
    rows = []
    for e in done:
        rows += rows_from_summary(get(f"{BASE}/summary?event={e['id']}"))
    return f"#{len(ev)}|{len(done)}|{len(ev) - len(done)}\n" + "\n".join(rows) + "\n", len(ev), len(done)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    text, n, d = fetch(sys.argv[1])
    open(sys.argv[2], "w", encoding="utf-8").write(text)
    print(f"ESPN: {n} game(s) on {sys.argv[1]}, {d} final")
