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

# Windows opens text files in an old code page by default; run everything in UTF-8 (emojis, names like ᴛɪɴᴏʟᴀ)
if not sys.flags.utf8_mode:
    raise SystemExit(subprocess.run([sys.executable, "-X", "utf8"] + sys.argv, env=dict(os.environ, PYTHONUTF8="1")).returncode)
os.environ["PYTHONUTF8"] = "1"

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
    r = subprocess.run(cmd, cwd=BBL, env=env, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"Building the {mode or 'table'} failed (details above).")


def page(title, body, dark=False):
    """Light content card on a light page (kept for reference)."""
    bg = "#0b1030" if dark else "#f6f7f9"
    return (f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title><style>body{{margin:0;padding:20px;background:{bg};font-family:-apple-system,Helvetica,Arial,sans-serif}}'
            f'.wrap{{max-width:1100px;margin:0 auto;background:#fff;border-radius:14px;padding:18px}}</style></head>'
            f'<body><div class="wrap">{body}</div></body></html>')


def page_dark(title, body):
    """The detailed table in the Command Center's dark theme."""
    css = (":root{--bg:#11151c;--panel:#181e27;--fg:#e6e9ef;--muted:#98a2b3;--line:#2a3240;--accent:#fb923c;--ok:#4ade80;--warn:#fbbf24;--bad:#f87171;color-scheme:dark}"
           "body{margin:0;padding:20px;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif}"
           ".wrap{max-width:1180px;margin:0 auto;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;overflow-x:auto}"
           ".wrap{color:var(--fg)}.wrap table{border-collapse:collapse;width:100%}"
           ".wrap th,.wrap td{color:var(--fg)!important;border-color:var(--line)!important;background-color:transparent}"
           ".wrap th{color:var(--muted)!important}.wrap h3{color:var(--accent)}.wrap p,.wrap small{color:var(--muted)}"
           "@media (max-width:600px){body{padding:8px}.wrap{padding:10px}}")
    return (f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title><style>{css}</style></head><body><div class="wrap">{body}</div></body></html>')


def page_fancy(title, body, label, logo=None):
    """The shareable page: the Top 10 image's night-sky background with the content on a white card."""
    css = ("*{box-sizing:border-box}body{margin:0;min-height:100vh;padding:24px 16px 40px;font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;color:#1b2230;"
           "background:radial-gradient(60% 30% at 85% 0%,rgba(34,211,238,.30),transparent 70%),radial-gradient(70% 30% at 5% 6%,rgba(255,94,58,.34),transparent 70%),"
           "repeating-conic-gradient(from 200deg at 50% -10%,rgba(255,255,255,.04) 0 6deg,transparent 6deg 14deg),linear-gradient(180deg,#141a4d 0%,#0a0f30 45%,#070b24 100%) fixed;background-color:#070b24}"
           "body:before{content:'';position:fixed;inset:0;background:radial-gradient(rgba(255,255,255,.07) 1.2px,transparent 1.6px) 0 0/18px 18px;"
           "-webkit-mask:linear-gradient(180deg,#000,transparent 45%);mask:linear-gradient(180deg,#000,transparent 45%);pointer-events:none}"
           ".hero{max-width:1100px;margin:0 auto 18px;display:flex;align-items:center;gap:16px;position:relative}"
           ".hero img{width:72px;height:72px;border-radius:16px;box-shadow:0 6px 20px rgba(0,0,0,.4)}"
           ".eyebrow{font:800 12px Arial,sans-serif;letter-spacing:.25em;text-transform:uppercase;color:#7dd3fc}"
           ".title{font:900 44px/1 Arial,sans-serif;letter-spacing:-.01em;transform:skewX(-8deg);background:linear-gradient(180deg,#fff7c2,#ffd23f 40%,#ff7a18 75%,#ff3d5a);"
           "-webkit-background-clip:text;background-clip:text;color:transparent;margin:4px 0 2px}"
           ".sub{color:#cbd5e1;font-size:14px}"
           ".wrap{max-width:820px;margin:0 auto;background:#fff;border-radius:20px;padding:20px;position:relative;"
           "box-shadow:0 0 0 1px rgba(255,255,255,.08),0 20px 60px rgba(0,0,0,.45);overflow-x:auto}"
           "@media (max-width:600px){.title{font-size:30px}.hero img{width:52px;height:52px}.wrap{padding:12px}}")
    lg = f'<img src="{logo}" alt="">' if logo else ''
    return (f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title><style>{css}</style></head><body>'
            f'<div class="wrap">{body}</div></body></html>')


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
        r = subprocess.run([PY, os.path.join(BBL, "fetch_box.py"), date, box], capture_output=True, text=True, encoding="utf-8")
        say(r.stdout.strip())
        if r.returncode != 0:
            raise SystemExit(r.stderr.strip() or "ESPN fetch failed")
        first = open(box, encoding="utf-8").readline().strip().lstrip("#").split("|")
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
    try:
        import base64
        logo = "data:image/png;base64," + base64.b64encode(open(os.path.join(BBL, "league_logo.png"), "rb").read()).decode()
    except OSError:
        logo = None
    open(os.path.join(out, "best_worst.html"), "w", encoding="utf-8").write(page_fancy(f"BBL Best & Worst · {label}", open(os.path.join(BBL, "nightly_share.html"), encoding="utf-8").read(), label, logo))
    open(os.path.join(out, "best_worst_table.html"), "w", encoding="utf-8").write(page_dark(f"BBL Best & Worst table · {label}", open(os.path.join(BBL, "nightly.html"), encoding="utf-8").read()))
    shutil.copy2(os.path.join(BBL, "nightly_share.txt"), os.path.join(out, "best_worst.txt"))

    say("Drawing the Top 10 image…")
    r = subprocess.run([PY, os.path.join(BBL, "render.py"), os.path.join(BBL, "nightly_top10.html"), os.path.join(out, "top10.png")])
    if r.returncode != 0:
        say("⚠️  The image couldn't be drawn. Run '1 - Setup' again, then retry.")
    for f in ("box.txt", "nightly.html", "nightly_share.html", "nightly_share.txt", "nightly_share_subject.txt", "nightly_top10.html"):
        try:
            os.remove(os.path.join(BBL, f))
        except FileNotFoundError:
            pass
    say(f"\n✅ Done: {out}")
    if "--no-open" not in args:
        if sys.platform == "darwin":
            subprocess.run(["open", out])
        elif sys.platform == "win32":
            os.startfile(out)


if __name__ == "__main__":
    main()
