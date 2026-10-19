#!/usr/bin/env python3
"""Turn nightly_top10.html into a PNG with a headless browser (Playwright + Chromium).
Usage: python3 render.py IN.html OUT.png"""
import os, sys
from playwright.sync_api import sync_playwright

src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1400}, device_scale_factor=1)
    pg.goto("file://" + src)
    try:
        pg.wait_for_load_state("networkidle", timeout=8000)  # web fonts; falls back to Arial if offline
    except Exception:
        pass
    pg.wait_for_timeout(300)
    pg.locator("#card").screenshot(path=dst)
    b.close()
print("image saved:", dst)
