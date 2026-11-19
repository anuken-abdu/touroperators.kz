# -*- coding: utf-8 -*-
"""Одностраничный сайт АТРК: src/ → dist/. Запуск: python3 src/build.py (Vercel запускает сам)."""
import json, re, shutil, sys, html
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from data import *

ROOT = Path(__file__).resolve().parent.parent; DIST = ROOT / "dist"; IMG = ROOT / "assets" / "img"
VER = "1911261"
E = html.escape
YEAR = date.today().year

def minify_css(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S); s = re.sub(r"\s*\n\s*", "", s)
    return re.sub(r"\s*([{};,>])\s*", r"\1", s).replace(";}", "}")
CSS = minify_css((ROOT / "src" / "styles.css").read_text(encoding="utf-8"))

_P = {"up": '<path d="M12 20V5M5 12l7-7 7 7"/>', "back": '<path d="M20 12H5M12 5l-7 7 7 7"/>',
      "menu": '<path d="M3 7h18M3 12h18M3 17h18"/>', "x": '<path d="M5 5l14 14M19 5L5 19"/>'}
def ic(n): return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_P[n]}</svg>'

_SHORT = r"(?<![\w])(в|во|и|с|со|к|о|об|у|а|на|по|за|от|до|из|не|для|при|под|или)\s(?=\S)"
def typo(h):
    """Неразрывные пробелы после коротких слов и внутри чисел — без висячих предлогов и «лет» в одиночку."""
    def t(m):
        x = re.sub(_SHORT, lambda k: k.group(1) + "\u00a0", m.group(0), flags=re.I)
        x = re.sub(r"(?<=\d) (?=\d)", "\u00a0", x); x = re.sub(r"(?<=\d) (?=(лет|года|году|членов|партнёра)\b)", "\u00a0", x)
        return x.replace(" —", "\u00a0—")
    parts = re.split(r"(<script\b.*?</script>|<style\b.*?</style>|<head>.*?</head>)", h, flags=re.S)
    return "".join(p if p.startswith(("<script", "<style", "<head")) else re.sub(r"(?<=>)[^<]+", t, p) for p in parts)

def gtag():
    if not TAG_ID: return ""
    return ("<!-- Google tag (gtag.js) -->\n" f'<script async src="https://www.googletagmanager.com/gtag/js?id={TAG_ID}"></script>\n'
            "<script>\n  window.dataLayer = window.dataLayer || [];\n  function gtag(){dataLayer.push(arguments);}\n  gtag('js', new Date());\n\n"
            f"  gtag('config', '{TAG_ID}');\n" + (f"  gtag('config', '{GA_ID}');\n" if GA_ID else "") + "</script>\n")

HAS_CONTACTS = any([PHONE_DISPLAY, EMAIL, ADDRESS, WHATSAPP])
NAV = [("Об ассоциации", "#ob-assotsiatsii"), ("Члены", "#chleny"), ("Система гарантирования", "#sistema-garantirovaniya"), ("Планы", "#plany"), ("Вопросы", "#voprosy")] + \
      ([("Контакты", "#kontakty")] if HAS_CONTACTS else [])

def logo_tile(slug, name):
    f = IMG / f"m-{slug}.webp"
    if f.exists():
        from PIL import Image
        w, h = Image.open(f).size
        return f'<li class="lg"><img src="/assets/img/m-{slug}.webp" alt="{E(name)}" width="{w}" height="{h}" loading="lazy" decoding="async"></li>'
    return f'<li class="lg lg-t"><b>{E(name)}</b></li>'

def org_ld():
    o = {"@context": "https://schema.org", "@type": "Organization", "@id": SITE_URL + "/#org", "name": NAME, "alternateName": SHORT,
         "url": SITE_URL + "/", "logo": SITE_URL + "/assets/icon-512.png", "image": SITE_URL + "/assets/og.png", "foundingDate": FOUNDED,
         "description": ABOUT, "areaServed": {"@type": "Country", "name": "Казахстан"}, "knowsLanguage": ["ru", "kk"],
         "employee": {"@type": "Person", "name": PRESIDENT[0], "jobTitle": PRESIDENT[1]},
         "member": [{"@type": "Organization", "name": n} for _, n in MEMBERS],
         "memberOf": {"@type": "Organization", "name": "Национальная палата предпринимателей Республики Казахстан «Атамекен»", "url": "https://atameken.kz/"}}
    if PHONE_TEL: o["telephone"] = PHONE_TEL
    if EMAIL: o["email"] = EMAIL
    if ADDRESS: o["address"] = {"@type": "PostalAddress", "streetAddress": ADDRESS, "addressCountry": "KZ"}
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    site = {"@context": "https://schema.org", "@type": "WebSite", "url": SITE_URL + "/", "name": NAME, "inLanguage": "ru", "publisher": {"@id": SITE_URL + "/#org"}}
    return "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (o, site, faq))

def head(title, desc, path="/", noindex=False):
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
{gtag()}<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{f'<meta name="google-site-verification" content="{GSC_META}" />' + chr(10) if GSC_META else ""}<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
{'<meta name="robots" content="noindex,follow">' if noindex else f'<link rel="canonical" href="{SITE_URL}{path}">' + chr(10) + '<meta name="robots" content="index,follow,max-image-preview:large">'}
<meta name="theme-color" content="#010066">
<meta property="og:type" content="website"><meta property="og:locale" content="ru_KZ"><meta property="og:site_name" content="{SHORT}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{SITE_URL}{path}">
<meta property="og:image" content="{SITE_URL}/assets/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">
<meta name="geo.region" content="KZ"><meta name="geo.placename" content="Казахстан">
<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48"><link rel="icon" href="/assets/favicon-32.png" type="image/png" sizes="32x32"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/inter-cyrillic-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
'''

def header():
    links = "".join(f'<a href="{u}">{n}</a>' for n, u in NAV)
    return f'''<a class="skip" href="#main">К содержимому</a>
<header class="hd"><div class="w hd-in">
<a class="logo" href="#top" aria-label="{NAME} — в начало"><img src="/assets/logo.webp" alt="{SHORT} — {NAME}" width="185" height="60" decoding="async"></a>
<nav class="nav" aria-label="Разделы">{links}</nav>
<button class="burger" type="button" aria-label="Открыть меню" aria-expanded="false" aria-controls="menu">{ic("menu")}</button>
</div></header>
<div class="menu" id="menu" hidden><div class="menu-p"><div class="menu-x"><span>{SHORT}</span><button type="button" data-close aria-label="Закрыть меню">{ic("x")}</button></div><nav aria-label="Разделы">{links}</nav></div></div>'''

def footer():
    return f'''<footer class="ft"><div class="w ft-in">
<div><img src="/assets/logo.webp" alt="{SHORT}" width="148" height="48" loading="lazy" decoding="async"><p>{ABOUT}</p></div>
<div class="ft-b"><span>© {FOUNDED}–{YEAR} {NAME}</span><span>Член НПП РК «Атамекен»</span><a href="https://www.anuken.kz" target="_blank" rel="noopener">Разработка и продвижение Anuken.kz</a></div>
</div></footer>
<div class="flo"><button class="sm" type="button" data-back hidden aria-label="Назад" title="Назад">{ic("back")}</button><button class="sm" type="button" data-top hidden aria-label="Наверх" title="Наверх">{ic("up")}</button></div>
<script src="/assets/app.js?v={VER}" defer></script>'''

def build():
    g = GUARANTEE
    pres = IMG / "president.webp"
    pres_img = (f'<img src="/assets/img/president.webp" alt="{PRESIDENT[0]}, {PRESIDENT[1].lower()} {SHORT}" width="326" height="435" loading="lazy" decoding="async">'
                if pres.exists() else '<span class="noph"></span>')
    tq = (f'<img class="tq" src="/assets/img/turistik-qamqor.webp" alt="Туристік Қамқор" width="369" height="220" loading="lazy" decoding="async">'
          if (IMG / "turistik-qamqor.webp").exists() else "")
    tasks = "".join(f"<li><h3>{E(h)}</h3><p>{E(t)}</p></li>" for h, t in TASKS)
    atam = "".join(f"<li><h3>{E(h)}</h3><p>{E(t)}</p></li>" for h, t in ATAMEKEN)
    dirs = "".join(f"<li><h3>{E(h)}</h3><p>{E(t)}</p></li>" for h, t in g["directions"])
    figs = "".join(f"<li><b>{n}</b><span>{t}</span></li>" for n, t in g["figures"] + [g["helped"]])
    plans = "".join(f"<li>{E(p)}</li>" for p in PLANS)
    faq = "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in FAQ)
    contacts = ""
    if HAS_CONTACTS:
        rows = []
        if PHONE_DISPLAY: rows.append(f'<div><dt>Телефон</dt><dd><a href="tel:{PHONE_TEL}">{E(PHONE_DISPLAY)}</a></dd></div>')
        if EMAIL: rows.append(f'<div><dt>Электронная почта</dt><dd><a href="mailto:{EMAIL}">{E(EMAIL)}</a></dd></div>')
        if WHATSAPP: rows.append(f'<div><dt>WhatsApp</dt><dd><a href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener">Написать сообщение</a></dd></div>')
        if ADDRESS: rows.append(f'<div><dt>Адрес</dt><dd>{E(ADDRESS)}</dd></div>')
        contacts = f'<section class="s" id="kontakty"><div class="w"><div class="sh"><h2>Контакты</h2><p>По вопросам вступления в ассоциацию и сотрудничества.</p></div><dl class="ct">{"".join(rows)}</dl></div></section>'
    body = f'''<main id="main">
<section class="hero" id="top">{'<img class="mark" src="/assets/img/mark.webp" alt="" width="640" height="640" aria-hidden="true">' if (IMG / "mark.webp").exists() else ""}<div class="w hero-in">
<p class="ey">Основана в {FOUNDED} году</p>
<h1>{NAME}</h1>
<p class="lead">{ABOUT}</p>
<ul class="hf">
<li><b>8 членов</b><span>около 80% доли рынка</span></li>
<li><b>2 партнёра</b><span>вместе с членами около 90% доли рынка</span></li>
<li><b>НПП РК «Атамекен»</b><span>активный член, аккредитация в двух комитетах</span></li>
</ul></div></section>

<section class="s" id="ob-assotsiatsii"><div class="w about">
<figure class="pr">{pres_img}<figcaption><b>{PRESIDENT[0]}</b><span>{PRESIDENT[1]}</span></figcaption></figure>
<div><div class="sh"><h2>Об ассоциации</h2><p>{ABOUT} В состав входят 8 членов и 2 партнёра.</p></div>
<h3 class="sub">Задачи и направления деятельности</h3><ul class="cells c3">{tasks}</ul></div>
</div></section>

<section class="s alt"><div class="w split"><div class="sh"><h2>Член НПП РК «Атамекен»</h2><p>Ассоциация является активным членом Национальной палаты предпринимателей Республики Казахстан «Атамекен» и аккредитована в двух комитетах.</p></div>
<ul class="cells c2">{atam}</ul></div></section>

<section class="s" id="chleny"><div class="w"><div class="sh"><h2>Члены ассоциации</h2><p>Восемь туроператоров, на которых приходится около 80% доли рынка.</p></div>
<ul class="lgs c4">{"".join(logo_tile(s, n) for s, n in MEMBERS)}</ul>
<div class="sh sh2"><h3>Партнёры</h3><p>Вместе с членами ассоциации — около 90% доли рынка.</p></div>
<ul class="lgs c2">{"".join(logo_tile(s, n) for s, n in PARTNERS)}</ul></div></section>

<section class="s dark" id="sistema-garantirovaniya"><div class="w">
<div class="gt-h"><div class="sh"><p class="ey">Проект ассоциации</p><h2>{g["title"]}</h2><p>Администратор системы — «{g["admin"]}».</p></div>{f'<div class="tq-w">{tq}</div>' if tq else ""}</div>
<ul class="cells c4">{dirs}</ul>
<ul class="figs">{figs}</ul></div></section>

<section class="s" id="plany"><div class="w split"><div class="sh"><h2>Дальнейшие планы</h2><p>Направления, по которым ассоциация будет работать дальше.</p></div>
<ul class="rows">{plans}</ul></div></section>

<section class="s alt" id="voprosy"><div class="w split"><div class="sh"><h2>Вопросы об ассоциации</h2></div><div class="faq">{faq}</div></div></section>
{contacts}
</main>'''
    title = f"{NAME} — {SHORT}"
    desc = f"{SHORT} — объединение туроператоров Казахстана с {FOUNDED} года: защита интересов отрасли, туристское законодательство, Система гарантирования прав туристов."
    assert len(title) <= 60 and len(desc) <= 160, (len(title), len(desc))
    doc = head(title, desc) + org_ld() + "\n</head>\n<body>\n" + header() + body + footer() + "\n</body>\n</html>\n"
    (DIST / "index.html").write_text(typo(doc), encoding="utf-8")
    nf = head(f"Страница не найдена — {SHORT}", "Страница не найдена.", noindex=True) + "</head>\n<body>\n" + header() + \
         f'<main id="main"><section class="hero nf"><div class="w hero-in"><p class="ey">Ошибка 404</p><h1>Такой страницы нет</h1><p class="lead">Возможно, адрес изменился.</p><p><a class="btn" href="/">На главную</a></p></div></section></main>' + footer() + "\n</body>\n</html>\n"
    (DIST / "404.html").write_text(nf, encoding="utf-8")

def meta():
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Google-Extended", "Googlebot", "Applebot-Extended", "Bingbot", "YandexBot", "CCBot"]
    (DIST / "robots.txt").write_text("".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{SITE_URL}/</loc><lastmod>{date.today().isoformat()}</lastmod><priority>1.0</priority></url></urlset>\n', encoding="utf-8")
    (DIST / "site.webmanifest").write_text(json.dumps({"name": NAME, "short_name": SHORT, "start_url": "/", "display": "standalone", "background_color": "#ffffff", "theme_color": "#010066",
        "icons": [{"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False), encoding="utf-8")
    g = GUARANTEE
    llms = f"""# {NAME} ({SHORT})

> {ABOUT} Основана в {FOUNDED} году. Президент — {PRESIDENT[0]}.

## Состав
- Члены (8, около 80% доли рынка): {", ".join(n for _, n in MEMBERS)}
- Партнёры (2, вместе с членами около 90% доли рынка): {", ".join(n for _, n in PARTNERS)}

## Задачи
""" + "\n".join(f"- {t}" for _, t in TASKS) + f"""

## НПП РК «Атамекен»
Ассоциация — активный член НПП РК «Атамекен», аккредитована в Комитете туристской отрасли с правом голоса и в Комитете по вопросам развития саморегулирования с правом совещательного голоса.

## Проект: {g["title"]}
Администратор — «{g["admin"]}». Участники: {", ".join(n + " " + t for n, t in g["figures"])}. {g["helped"][1].capitalize()}: {g["helped"][0]}.
""" + "\n".join(f"- {t}" for _, t in g["directions"]) + "\n\n## Планы\n" + "\n".join(f"- {p}" for p in PLANS) + f"\n\nСайт: {SITE_URL}/\n"
    (DIST / "llms.txt").write_text(llms, encoding="utf-8")

def main():
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir(); shutil.copytree(ROOT / "assets", DIST / "assets")
    shutil.copyfile(ROOT / "src" / "app.js", DIST / "assets" / "app.js")
    if (ROOT / "assets" / "favicon.ico").exists(): shutil.copyfile(ROOT / "assets" / "favicon.ico", DIST / "favicon.ico")
    build(); meta(); print("готово:", DIST)

if __name__ == "__main__":
    main()
