#!/usr/bin/env python3
"""BBL Best & Worst — build tonight's tables and Top 10 image.

  python3 bbl/run.py                 # last night's games (before noon) or tonight's (after noon)
  python3 bbl/run.py 20261020        # a specific date (YYYYMMDD, the date the games were played)
  python3 bbl/run.py --demo          # sample data from Fri Oct 16 (no internet needed)

Results go to output/<date>/:
  best_worst.html        the full Best & Worst page (Player of the night, JACKPOT, Top 10, Oof Zone)
  best_worst_table.html  the detailed stat table version
  top10.png              phone-friendly Top 10 image to post in the group chat
"""
import datetime as dt, glob, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BBL = os.path.join(ROOT, "bbl")
ROST_DIR = os.path.join(ROOT, "rosters")
ROSTERS = os.path.join(ROST_DIR, "bbl_rosters.txt")
PY = sys.executable


def say(msg):
    print(msg, flush=True)


def pick_date(argv):
    for a in argv:
        if a.isdigit() and len(a) == 8:
            return a
    now = dt.datetime.now()
    d = now.date() - dt.timedelta(days=1) if now.hour < 12 else now.date()
    return d.strftime("%Y%m%d")


def refresh_rosters():
    """Use the newest bbl_rosters*.txt from Downloads if it's newer than the saved copy."""
    dl = sorted(glob.glob(os.path.expanduser("~/Downloads/bbl_rosters*.txt")), key=os.path.getmtime)
    if dl and (not os.path.exists(ROSTERS) or os.path.getmtime(dl[-1]) > os.path.getmtime(ROSTERS)):
        shutil.copy2(dl[-1], ROSTERS)
        say(f"Rosters: using {os.path.basename(dl[-1])} from Downloads")
    if not os.path.exists(ROSTERS):
        say("⚠️  No rosters yet: everyone will show as 'Free agent'. See README → 'Export rosters from CBS'.")
        open(ROSTERS, "w").write("# no rosters exported yet\n")
        return
    age = (dt.datetime.now() - dt.datetime.fromtimestamp(os.path.getmtime(ROSTERS))).days
    if age >= 3:
        say(f"ℹ️  Rosters are {age} days old. Click the 'BBL roster export' bookmark on CBS to refresh them.")


def nightly(box, label, mode=None, env=None):
    cmd = [PY, os.path.join(BBL, "nightly.py"), box, ROSTERS, label] + ([mode] if mode else [])
    r = subprocess.run(cmd, cwd=BBL, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"Building the {mode or 'table'} failed (details above).")


def page(title, body, dark=False):
    bg = "#0b1030" if dark else "#f6f7f9"
    return (f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title><style>body{{margin:0;padding:20px;background:{bg};font-family:-apple-system,Helvetica,Arial,sans-serif}}'
            f'.wrap{{max-width:1100px;margin:0 auto;background:#fff;border-radius:14px;padding:18px}}</style></head>'
            f'<body><div class="wrap">{body}</div></body></html>')


def main():
    args = sys.argv[1:]
    demo = "--demo" in args
    date = "20261016" if demo else pick_date(args)
    d = dt.datetime.strptime(date, "%Y%m%d")
    label = d.strftime("%a %b ") + str(d.day) + (" (sample)" if demo else "")
    out = os.path.join(ROOT, "output", date + ("-demo" if demo else ""))
    os.makedirs(out, exist_ok=True)
    box = os.path.join(BBL, "box.txt")

    global ROSTERS
    if demo:
        ROSTERS = os.path.join(ROOT, "tests", "sample_rosters.txt")
        shutil.copy2(os.path.join(ROOT, "tests", "sample_box_20261016.txt"), box)
        say("Demo: using saved box scores and rosters from Fri Oct 16")
    else:
        refresh_rosters()
        say(f"Fetching box scores for {label} from ESPN…")
        r = subprocess.run([PY, os.path.join(BBL, "fetch_box.py"), date, box], capture_output=True, text=True)
        say(r.stdout.strip())
        if r.returncode != 0:
            raise SystemExit(r.stderr.strip() or "ESPN fetch failed")
        first = open(box).readline().lstrip("#").split("|")
        if first[0] == "0":
            raise SystemExit(f"No NBA games on {label}. Nothing to build.")
        if first[1] == "0":
            raise SystemExit(f"None of the {first[0]} games on {label} have finished yet. Try again later tonight.")
        if first[2] != "0":
            say(f"ℹ️  {first[2]} game(s) still in progress: they're left out. Re-run later for the full night.")

    my = ""
    cfg = os.path.join(ROOT, "config.txt")
    if os.path.exists(cfg):
        for l in open(cfg, encoding="utf-8"):
            if l.strip().lower().startswith("my_team="):
                my = l.split("=", 1)[1].strip()
    env = dict(os.environ, BBL_CC_LINK="", BBL_MY_TEAM=my)
    say("Building the tables…")
    nightly(box, label, None, env)
    nightly(box, label, "share", env)
    nightly(box, label, "top10", env)
    open(os.path.join(out, "best_worst.html"), "w").write(page(f"BBL Best & Worst · {label}", open(os.path.join(BBL, "nightly_share.html")).read()))
    open(os.path.join(out, "best_worst_table.html"), "w").write(page(f"BBL Best & Worst table · {label}", open(os.path.join(BBL, "nightly.html")).read()))
    shutil.copy2(os.path.join(BBL, "nightly_share.txt"), os.path.join(out, "best_worst.txt"))

    say("Drawing the Top 10 image…")
    r = subprocess.run([PY, os.path.join(BBL, "render.py"), os.path.join(BBL, "nightly_top10.html"), os.path.join(out, "top10.png")])
    if r.returncode != 0:
        say("⚠️  The image couldn't be drawn. Run setup again (README step 2), then retry.")
    for f in ("box.txt", "nightly.html", "nightly_share.html", "nightly_share.txt", "nightly_share_subject.txt", "nightly_top10.html"):
        try:
            os.remove(os.path.join(BBL, f))
        except FileNotFoundError:
            pass
    say(f"\n✅ Done: {out}")
    if sys.platform == "darwin" and "--no-open" not in args:
        subprocess.run(["open", out])


if __name__ == "__main__":
    main()
