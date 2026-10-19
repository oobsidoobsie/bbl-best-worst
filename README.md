# 🏀 BBL Best & Worst

Builds the **Best & Worst performances of the night** for the BBL (CBS fantasy basketball) on a Mac or Windows PC:

- `best_worst.html`: the full page: Player of the night, JACKPOT callouts, podium, Top 10, honorable mentions, 🥶 Oof Zone
- `best_worst_table.html`: the detailed stat table (best slot, base, minutes, every stat)
- `top10.png`: a phone-friendly Top 10 image to post in the group chat

Everything uses BBL scoring: PTS +1, FGM +2, FGA −1, FTM +1, FTA −1, REB +1, AST +2, STL +4, BLK +4, TO −2, PF −1,
plus the **best-slot bonus** (G slot +1 per rebound, F slot +1 per assist, C slot +1 per made 3).

---

## Setup (once, about 10 minutes)

**1. Put the folder somewhere permanent.** Unzip `bbl-best-worst.zip` and move the `bbl-best-worst` folder to Documents.

**2. Double-click `1 - Setup`.**
- The first time, macOS may say it *"can't be opened because it is from an unidentified developer"*. Right-click (or Control-click) the file → **Open** → **Open**. You only do this once per file.
- If a window offers to install **command line developer tools**, click **Install**, wait, then double-click Setup again.
- It downloads about 150 MB (the headless browser that draws the image). When you see ✅, press any key.

**3. Install the roster bookmark.** Open `rosters/Install roster bookmark.html` and drag the purple **🏀 BBL roster export** button onto your bookmarks bar.

**4. Export rosters.** Go to the CBS league site, sign in, and click the bookmark. After about 20 seconds, `bbl_rosters.txt` appears in Downloads.

## Windows PC instead of a Mac

Same steps, using the Windows files:

1. Install **Python 3** from <https://www.python.org/downloads/windows/>. On the first installer screen, **tick "Add python.exe to PATH"**.
2. Unzip the folder (right-click the zip → **Extract All**), then double-click **`1 - Setup (Windows).bat`**. If Windows shows *"Windows protected your PC"*, click **More info** → **Run anyway** (this happens once).
3. Roster bookmark: same as the Mac steps 3–4 (Chrome or Edge work well).
4. Each game night, double-click **`2 - BBL Tonight (Windows).bat`** and press **Enter** (or type `demo`).

## Every game night

Double-click **`2 - BBL Tonight`** and press **Enter**. The results folder opens by itself (`output/<date>/`).

- **Before noon** it builds last night's games; **after noon**, today's. Type a date like `20261020` for a specific night.
- Type `demo` to try it with saved sample data from Fri Oct 16 (works offline).
- If games are still going, it tells you and leaves them out. Run it again later for the full night.
- **Rosters:** re-click the bookmark on CBS after waivers or trades. `BBL Tonight` uses the newest `bbl_rosters*.txt` in Downloads automatically.

**Optional:** put your team name in `config.txt` (`my_team=Pucs`) to get a ★ next to it in the team legend.

---

## How the data is collected

| What | Where from | Login? |
|---|---|---|
| Box scores (every player's stats, minutes) | ESPN's public scoreboard/summary feed (`site.api.espn.com`), the same data espn.com shows | No |
| Fantasy owners, CBS positions, team logos | Your CBS league pages, read by the bookmark in **your** signed-in browser | Uses your existing CBS sign-in; the code never sees or stores your password |

1. `bbl/fetch_box.py` asks ESPN for that date's games, then downloads the box score of every **finished** game.
2. The bookmark (`rosters/export_rosters.js`) only **reads** CBS pages: standings, each team page, and the player lists for positions. It never changes your lineup or roster.
3. `bbl/nightly.py` scores every player, picks his best eligible slot, ranks the lists and builds the pages:
   - **Top 10:** ties go to the higher base score, then fewer minutes.
   - **Worst list:** players with 20+ minutes only; ties go to the lower base score, then more minutes.
   - **Milestones:** 80+ 🔥, 90+ ☄️, 100+ 👑.
   - **Callouts:** 2 players from one manager in the top 10 = 🤝 DOUBLE UP, 3 = 🎰 JACKPOT!, 4 = 💎 MEGA JACKPOT!!, 5+ = 👑 GRAND JACKPOT!!!.
4. `bbl/render.py` takes a screenshot of the Top 10 page to make the PNG.

## Run it from Terminal (optional)

```bash
cd ~/Documents/bbl-best-worst
.venv/bin/python bbl/run.py            # latest night
.venv/bin/python bbl/run.py 20261020   # a specific date
.venv/bin/python bbl/run.py --demo     # sample data
```

## Troubleshooting

- **"Couldn't reach ESPN"**: check your internet connection and run it again.
- **Everyone shows as "Free agent"**: no roster file yet. Do setup step 4.
- **The bookmark does nothing in Safari**: try Chrome. Or in Safari: Settings → Advanced → *Show features for web developers*, then Develop menu → *Allow JavaScript from Smart Search Field*.
- **"No teams found"**: you weren't signed in to CBS, or you weren't on the league site when you clicked the bookmark.
- **The image wasn't made**: run `1 - Setup` again, then retry.

## What's in here

```
1 - Setup.command          one-time setup (Mac)
2 - BBL Tonight.command    run each game night (Mac)
1 - Setup (Windows).bat    one-time setup (Windows)
2 - BBL Tonight (Windows).bat   run each game night (Windows)
config.txt                 optional: your team name
bbl/fetch_box.py           ESPN box scores
bbl/nightly.py             scoring, rankings, HTML pages
bbl/render.py              Top 10 PNG
bbl/run.py                 runs everything in order
bbl/league_logo.png        BBL logo for the image
rosters/                   CBS roster bookmark + its install page
tests/                     sample data and a parser check (python3 tests/test_fetch_box.py)
```
