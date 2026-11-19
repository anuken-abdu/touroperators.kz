# -*- coding: utf-8 -*-
"""Картинка для ссылок в мессенджерах 1200×630. Запуск: python3 src/og.py"""
import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from data import NAME, FOUNDED
from playwright.sync_api import sync_playwright
A = Path(__file__).resolve().parent.parent / "assets"
f = lambda n: (A / "fonts" / n).as_uri()
H = f"""<html><head><style>
@font-face{{font-family:I;src:url({f('inter-cyrillic-wght-normal.woff2')});font-weight:100 900}}
body{{margin:0;width:1200px;height:630px;background:#010066;color:#fff;font-family:I;position:relative;overflow:hidden}}
img{{position:absolute;left:80px;top:70px;height:78px}}
h1{{position:absolute;left:80px;top:200px;margin:0;font-size:68px;line-height:1.08;font-weight:800;letter-spacing:-2px;width:1000px}}
p{{position:absolute;left:80px;bottom:72px;margin:0;font-size:28px;font-weight:600;padding-top:20px;border-top:3px solid #e8a317;width:1040px}}
</style></head><body><img src="{(A / 'logo.webp').as_uri()}"><h1>{NAME}</h1><p>Основана в {FOUNDED} году. Член НПП РК «Атамекен»</p></body></html>"""
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    fd, t = tempfile.mkstemp(suffix=".html"); os.write(fd, H.encode()); os.close(fd)
    pg.goto(Path(t).as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300); pg.screenshot(path=str(A / "og.png")); os.unlink(t); b.close()
print("og.png")
