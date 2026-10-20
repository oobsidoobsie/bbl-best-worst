# 🏀 BBL Best & Worst

Builds the **Best & Worst performances of the night** for the BBL (CBS fantasy basketball) on a **Windows PC or Mac**:

- **Best & Worst** (`.html` and `.png`): Player of the night, callouts, podium, Top 10, honorable mentions and the 🥶 Oof Zone
- **Best & Worst - Full Table** (`.html` and `.png`): the detailed stat table (best slot, base, minutes, every stat)
- **Top 10 - Mobile Friendly.png**: a tall Top 10 image sized for phones and group chats
- **Best & Worst - Text.txt**: the same lists as plain text

The PNGs are ready to upload to Facebook or a group chat.

Everything uses BBL scoring: PTS +1, FGM +2, FGA −1, FTM +1, FTA −1, REB +1, AST +2, STL +4, BLK +4, TO −2, PF −1,
plus the **best-slot bonus** (G slot +1 per rebound, F slot +1 per assist, C slot +1 per made 3).

## Download

On GitHub, click the green **Code** button → **Download ZIP**. You don't need Git. To update later, download the ZIP again and copy its `bbl` folder over your old one (your rosters and settings stay).

---

## Windows PC

### Setup (once, about 10 minutes)

**1. Install Python 3** from <https://www.python.org/downloads/windows/>. On the first installer screen, **tick "Add python.exe to PATH"**, then click Install Now.

**2. Put the folder somewhere permanent.** Right-click the downloaded zip → **Extract All**, and move the extracted folder to Documents. Don't run it from inside the zip.

**3. Double-click `1 - Setup (Windows)`.**
- If Windows shows *"Windows protected your PC"*, click **More info** → **Run anyway**. This happens once per file.
- It downloads about 150 MB (the headless browser that draws the image). When it says *Setup done*, press any key.

**4. Install the roster bookmark.** Open `rosters/Install roster bookmark.html` and drag the purple **🏀 BBL roster export** button onto your bookmarks bar (Chrome or Edge; press Ctrl+Shift+B if you don't see the bookmarks bar).

**5. Export rosters.** Go to the CBS league site, sign in, and click the bookmark. After about 20 seconds, `bbl_rosters.txt` appears in Downloads.

### Every game night

Double-click **`2 - BBL Tonight (Windows)`** and press **Enter**. The results folder opens by itself (`output\<date>\`).

- **Before noon** it builds last night's games; **after noon**, today's. Type a date like `20261020` for a specific night.
- Type `demo` to try it with saved sample data from Fri Oct 16 (works offline).
- If games are still going, it tells you and leaves them out. Run it again later for the full night.
- **Rosters:** re-click the bookmark on CBS after waivers or trades. `BBL Tonight` uses the newest `bbl_rosters*.txt` in Downloads automatically.

**Optional:** put your team name in `config.txt` (`my_team=Pucs`) to get a ★ next to it in the team legend.

## Mac

### Setup (once, about 10 minutes)

**1. Put the folder somewhere permanent.** Double-click the downloaded zip to unzip it, then move the folder to Documents.

**2. Double-click `1 - Setup`.**
- The first time, macOS may say it *"can't be opened because it is from an unidentified developer"*. Right-click (or Control-click) the file → **Open** → **Open**. You only do this once per file.
- If a window offers to install **command line developer tools**, click **Install**, wait, then double-click Setup again.
- It downloads about 150 MB (the headless browser that draws the image). When you see ✅, press any key.

**3. Install the roster bookmark.** Open `rosters/Install roster bookmark.html` and drag the purple **🏀 BBL roster export** button onto your bookmarks bar (in Safari: View → Show Favorites Bar first).

**4. Export rosters.** Go to the CBS league site, sign in, and click the bookmark. After about 20 seconds, `bbl_rosters.txt` appears in Downloads.

### Every game night

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
   - **Callouts:** 2 players from one manager in the top 10 = 🤝 DOUBLE UP, 3 = 🎰 JACKPOT!, 4 = 💎 MEGA JACKPOT!!, 5 = 👑 GRAND JACKPOT!!!, 6 = 🌋 ERUPTION, 7+ = 🏆 TOTAL DOMINATION. A free agent in the top 3 gets a 👀 tag, a #1 who wins by 15+ gets a 🚀 note, and the worst player gets the 🥶 Brick layer card.
4. `bbl/render.py` takes a screenshot of the Top 10 page to make the PNG.

## Troubleshooting

### Windows
- **"Python isn't installed"** even after installing it: re-run the Python installer, choose **Modify**, and make sure *Add Python to environment variables* is ticked. Then run Setup again.
- **"Couldn't reach ESPN"**: check your internet connection and run it again.
- **Everyone shows as "Free agent"**: no roster file yet. Do setup step 5 (Windows) or 4 (Mac).
- **"No teams found"**: you weren't signed in to CBS, or you weren't on the league site when you clicked the bookmark.
- **The window flashes and closes**: you're probably running it from inside the zip. Extract it first (setup step 2).
- **The image wasn't made**: run `1 - Setup` again, then retry.

### Mac
- **"Couldn't reach ESPN"**: check your internet connection and run it again.
- **Everyone shows as "Free agent"**: no roster file yet. Do setup step 4.
- **The bookmark does nothing in Safari**: try Chrome. Or in Safari: Settings → Advanced → *Show features for web developers*, then Develop menu → *Allow JavaScript from Smart Search Field*.
- **"No teams found"**: you weren't signed in to CBS, or you weren't on the league site when you clicked the bookmark.
- **"Permission denied" on a .command file**: open Terminal, type `chmod +x ` (with a space), drag the file into the window, press Enter.
- **The image wasn't made**: run `1 - Setup` again, then retry.

## What's in here

```
1 - Setup (Windows).bat         one-time setup (Windows)
2 - BBL Tonight (Windows).bat   run each game night (Windows)
1 - Setup.command               one-time setup (Mac)
2 - BBL Tonight.command         run each game night (Mac)
config.txt                      optional: your team name
bbl/                            the code (ESPN box scores, scoring, pages, images)
rosters/                        CBS roster bookmark + its install page
tests/                          sample data and a parser check
```
