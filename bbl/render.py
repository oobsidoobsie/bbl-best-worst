#!/usr/bin/env python3
"""Draw a page as a PNG with a headless browser (Playwright + Chromium).
Usage: python3 render.py IN.html OUT.png [css-selector] [viewport-width] [scale]"""
import os, sys
from playwright.sync_api import sync_playwright

src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
sel = sys.argv[3] if len(sys.argv) > 3 else "#card"
width = int(sys.argv[4]) if len(sys.argv) > 4 else 1080
scale = float(sys.argv[5]) if len(sys.argv) > 5 else 1
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": width, "height": 1400}, device_scale_factor=scale)
    pg.goto("file://" + src)
    try:
        pg.wait_for_load_state("networkidle", timeout=8000)  # web fonts; falls back to Arial if offline
        pg.evaluate("document.fonts.ready.then(() => true)")
    except Exception:
        pass
    pg.wait_for_timeout(300)
    pg.locator(sel).first.screenshot(path=dst)
    b.close()
print("image saved:", os.path.basename(dst))
