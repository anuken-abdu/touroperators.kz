# -*- coding: utf-8 -*-
"""Картинки сайта → assets/img (WebP, без EXIF). Запуск: python3 src/images.py
orig/members/<slug>.png — логотипы членов и партнёров (фон белый или прозрачный; лишние поля обрезаются)
orig/president.jpg (или rei-inna.jpg) — фото президента, вертикальное 3:4
orig/brand/atrk-white.png — логотип АТРК белым на прозрачном (шапка); atrk-original.png — исходный (иконка вкладки)
orig/brand/turistik-qamqor.png — логотип «Туристік Қамқор»"""
from pathlib import Path
from PIL import Image, ImageOps, ImageChops, ImageDraw
ROOT = Path(__file__).resolve().parent.parent; O = ROOT / "orig"; A = ROOT / "assets" / "img"; A.mkdir(parents=True, exist_ok=True)

def trim_white(im, tol=16):
    rgb = im.convert("RGB")
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, (255, 255, 255))).convert("L").point(lambda v: 255 if v > tol else 0)
    if im.mode == "RGBA": diff = ImageChops.multiply(diff, im.split()[3].point(lambda v: 255 if v > 10 else 0))
    box = diff.getbbox()
    return im.crop(box) if box else im

def clean(im):
    """Новый объект без метаданных."""
    out = Image.new(im.mode, im.size); out.paste(im); return out

def logo(src, dst, h=160):
    im = Image.open(src); im = ImageOps.exif_transpose(im)
    im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
    im = trim_white(im)
    if im.mode == "RGB":   # светло-серая подложка (как у Selfie Travel) → чистый белый, чтобы плитки были одинаковыми
        im = im.point(lambda v: v)  # копия
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b = px[x, y]
                if min(r, g, b) > 232 and max(r, g, b) - min(r, g, b) < 12: px[x, y] = (255, 255, 255)
    w = round(im.width * h / im.height)
    clean(im.resize((w, h), Image.LANCZOS)).save(dst, "WEBP", quality=92, method=6)
    return w, h

def main():
    for f in sorted((O / "members").glob("*.*")):
        print("логотип", f.stem, logo(f, A / f"m-{f.stem}.webp"))
    for name in ("president", "rei-inna"):
        for f in O.glob(name + ".*"):
            im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
            im = ImageOps.fit(im, (im.width, round(im.width * 4 / 3)) if im.height > im.width * 4 / 3 else (round(im.height * 3 / 4), im.height), Image.LANCZOS)
            w = min(im.width, 640); clean(im.resize((w, round(w * 4 / 3)), Image.LANCZOS)).save(A / "president.webp", "WEBP", quality=86, method=6)
            print("фото президента", w)
    b = O / "brand"
    if (b / "atrk-white.png").exists():
        im = Image.open(b / "atrk-white.png").convert("RGBA"); h = 96; w = round(im.width * h / im.height)
        clean(im.resize((w, h), Image.LANCZOS)).save(ROOT / "assets" / "logo.webp", "WEBP", quality=95, method=6); print("логотип шапки", w, h)
    if (b / "turistik-qamqor.png").exists(): print("Туристік Қамқор", logo(b / "turistik-qamqor.png", A / "turistik-qamqor.webp", 220))
    if (b / "atrk-original.png").exists():
        src = Image.open(b / "atrk-original.png").convert("RGB"); icons(src)
        # крупный знак для первого экрана: белый самолёт в круге на прозрачном фоне
        left = src.crop((0, 0, src.width // 3, src.height)); m = left.convert("L"); box = m.point(lambda v: 255 if v > 200 else 0).getbbox()
        m = m.crop(box).point(lambda v: max(0, min(255, (v - 40) * 255 // 175))); m = m.resize((640, round(640 * m.height / m.width)), Image.LANCZOS)
        mk = Image.new("RGBA", m.size, (255, 255, 255, 255)); mk.putalpha(m); clean(mk).save(A / "mark.webp", "WEBP", quality=90); print("знак", mk.size)

def icons(src):
    """Иконка вкладки: знак-самолёт из логотипа АТРК, на круге фирменного синего."""
    import io, struct
    # белый знак слева от надписи: ищем его по белым пикселям в левой трети
    left = src.crop((0, 0, src.width // 3, src.height)).convert("L").point(lambda v: 255 if v > 200 else 0)
    box = left.getbbox(); mark = src.crop(box)
    s = 512; ic = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(ic); d.ellipse((0, 0, s - 1, s - 1), fill=(1, 0, 102, 255))
    m = mark.convert("L").point(lambda v: max(0, min(255, (v - 40) * 255 // 175)))
    k = 0.66 * s / max(m.size); m = m.resize((round(m.width * k), round(m.height * k)), Image.LANCZOS)
    white = Image.new("RGBA", m.size, (255, 255, 255, 255)); white.putalpha(m)
    ic.alpha_composite(white, ((s - m.width) // 2, (s - m.height) // 2))
    a = ROOT / "assets"
    ic.save(a / "icon-512.png"); ic.resize((192, 192), Image.LANCZOS).save(a / "icon-192.png"); ic.resize((32, 32), Image.LANCZOS).save(a / "favicon-32.png")
    bg = Image.new("RGBA", (180, 180), (1, 0, 102, 255)); bg.alpha_composite(ic.resize((180, 180), Image.LANCZOS)); bg.convert("RGB").save(a / "apple-touch-icon.png")
    data = []
    for z in (16, 32, 48):
        bio = io.BytesIO(); ic.resize((z, z), Image.LANCZOS).save(bio, "PNG"); data.append((z, bio.getvalue()))
    hdr = struct.pack("<HHH", 0, 1, len(data)); off = 6 + 16 * len(data); ent = b""
    for z, dd in data: ent += struct.pack("<BBBBHHII", z, z, 0, 0, 1, 32, len(dd), off); off += len(dd)
    (a / "favicon.ico").write_bytes(hdr + ent + b"".join(dd for _, dd in data)); print("иконки готовы")

if __name__ == "__main__":
    main()
