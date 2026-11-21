#!/usr/bin/env python3
"""Draw the Aldermere passport spread (build tooling for the make.fun entry).

Renders a flat, top-down open passport spread: data page (left) with portrait,
personal data and a valid ICAO MRZ, and visa page (right) with a consistent
travel history and one telling paperwork detail (Condition 7: wool declaration).
Output: PNG, 1024x680, under the 1 MiB / 1024x1024 gate.
"""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1024, 680
OUT = "/home/hatch/workspace/makefun/passport-entry/assets/spread.png"
PORTRAIT = "/home/hatch/workspace/makefun/passport-entry/assets/media-generation-aldermere-portrait-0-652618e1-99a2-41c2-8a5e-ca153eee05cb.png"

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


# ---------- MRZ (ICAO 9303, check digits weights 7,3,1) ----------
def mrz_check(s):
    weights = (7, 3, 1)
    vals = {}
    for i in range(10):
        vals[str(i)] = i
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        vals[c] = 10 + i
    vals["<"] = 0
    return str(sum(vals[ch] * weights[i % 3] for i, ch in enumerate(s)) % 10)


def mrz_line1():
    # P< + ALD + surname VIK<< + given names ELENA<MAREN, padded to 44 with <
    s = "P<ALDV" + "IK" + "<<" + "ELENA<MAREN"
    return (s + "<" * 44)[:44]


def mrz_line2():
    doc = "ALD482917"            # 9 chars
    dob = "880314"               # 14 MAR 1988
    exp = "340201"               # 01 FEB 2034
    pers = "1403885521" + "<" * 4  # personal number, 14 chars
    core = (doc + mrz_check(doc) + "ALD" + dob + mrz_check(dob) + "F"
            + exp + mrz_check(exp) + pers + mrz_check(pers))
    assert len(core) == 43, len(core)
    return core + mrz_check(core)


# ---------- helpers ----------
def stamp_layer(size, rotate, draw_fn):
    """Draw a stamp on its own RGBA layer, rotate it, return the layer."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d, size)
    return layer.rotate(rotate, resample=Image.BICUBIC, expand=False)


def entry_stamp(d, size, country, city, kind, date, ink):
    w, h = size
    d.rounded_rectangle([4, 4, w - 5, h - 5], radius=10, outline=ink, width=3)
    d.rounded_rectangle([9, 9, w - 10, h - 10], radius=7, outline=ink, width=1)
    cx = w // 2
    d.text((cx, 12), country, font=font(SANS_B, 15), fill=ink, anchor="mt")
    d.text((cx, 31), city, font=font(SANS, 13), fill=ink, anchor="mt")
    d.line([(cx - 34, 50), (cx + 34, 50)], fill=ink, width=1)
    d.text((cx, 55), kind, font=font(SANS_B, 16), fill=ink, anchor="mt")
    d.text((cx, 76), date, font=font(SANS_B, 15), fill=ink, anchor="mt")


def main():
    img = Image.new("RGB", (W, H), (38, 41, 47))
    d = ImageDraw.Draw(img, "RGBA")

    # subtle vignette
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-220, -180, W + 220, H + 180], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    img = Image.composite(img, Image.new("RGB", (W, H), (18, 20, 24)), vig)
    d = ImageDraw.Draw(img, "RGBA")

    # booklet shadow + pages
    d.rounded_rectangle([28, 26, 996, 654], radius=6, fill=(0, 0, 0, 110))
    d.rectangle([32, 30, 992, 650], fill=(233, 236, 240))          # spread
    # faint guilloche waves on both pages
    for y0 in range(60, 640, 46):
        pts = [(x, y0 + 5 * math.sin(x / 55.0 + y0)) for x in range(40, 985, 8)]
        d.line(pts, fill=(120, 140, 165, 26), width=1)
    # centre gutter
    d.rectangle([508, 30, 516, 650], fill=(120, 125, 135, 90))
    d.line([(508, 30), (508, 650)], fill=(90, 95, 105, 120), width=1)
    d.line([(516, 30), (516, 650)], fill=(255, 255, 255, 90), width=1)

    # ================= LEFT PAGE: data page =================
    # emblem: circle + star + waves
    cx, cy = 272, 78
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], outline=(43, 72, 110), width=2)
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], outline=(43, 72, 110), width=1)
    # simple puffin-ish star
    star = [(cx, cy - 13), (cx + 4, cy - 4), (cx + 13, cy - 3), (cx + 6, cy + 3),
            (cx + 9, cy + 12), (cx, cy + 7), (cx - 9, cy + 12), (cx - 6, cy + 3),
            (cx - 13, cy - 3), (cx - 4, cy - 4)]
    d.polygon(star, fill=(43, 72, 110))
    d.arc([cx - 14, cy + 6, cx + 14, cy + 22], 0, 180, fill=(43, 72, 110), width=2)
    d.arc([cx - 10, cy + 11, cx + 10, cy + 24], 0, 180, fill=(43, 72, 110), width=1)

    d.text((272, 112), "REPUBLIC OF ALDERMERE", font=font(SERIF_B, 17),
           fill=(28, 42, 66), anchor="mt")
    d.text((272, 134), "PASSPORT", font=font(SERIF_B, 26),
           fill=(28, 42, 66), anchor="mt")
    d.text((272, 162), "PASSEPORT", font=font(SERIF, 12),
           fill=(70, 80, 95), anchor="mt")
    d.line([(72, 184), (472, 184)], fill=(43, 72, 110), width=1)

    # portrait
    photo = Image.open(PORTRAIT).convert("RGB")
    pw, ph = photo.size
    photo = photo.crop((int(pw * 0.10), int(ph * 0.15), int(pw * 0.90), int(ph * 0.82)))
    photo = photo.resize((148, 186), Image.LANCZOS)
    img.paste(photo, (56, 200))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([56, 200, 204, 386], outline=(90, 100, 115), width=2)
    d.text((130, 392), "E. M. Vik", font=font(SERIF_I, 15), fill=(40, 50, 65), anchor="mt")

    # data fields: label / value rows, two blocks
    x0, y = 228, 200
    rows = [
        ("Type", "P"), ("Code", "ALD"), ("Passport No.", "ALD 482 917"),
        ("Surname", "VIK"), ("Given names", "ELENA MAREN"),
        ("Nationality", "ALDERMERIAN"), ("Date of birth", "14 MAR 1988"),
        ("Sex", "F"), ("Place of birth", "SKARDVIK"),
        ("Date of issue", "02 FEB 2024"), ("Date of expiry", "01 FEB 2034"),
        ("Authority", ""),
    ]
    for label, value in rows:
        d.text((x0, y), label.upper(), font=font(SANS, 10), fill=(95, 105, 120))
        if value:
            d.text((x0, y + 11), value, font=font(SANS_B, 14), fill=(25, 30, 40))
        y += 27
    # authority wraps to a second line (y is now just past the label row)
    d.text((x0, y - 27 + 11), "MINISTRY OF THE INTERIOR,", font=font(SANS_B, 14), fill=(25, 30, 40))
    d.text((x0, y - 27 + 26), "SKARDVIK", font=font(SANS_B, 14), fill=(25, 30, 40))

    # MRZ
    d.rectangle([48, 556, 496, 634], fill=(225, 229, 234))
    d.text((56, 562), mrz_line1(), font=font(MONO, 15), fill=(20, 25, 35))
    d.text((56, 584), mrz_line2(), font=font(MONO, 15), fill=(20, 25, 35))
    d.text((488, 640), "2", font=font(SANS, 11), fill=(110, 118, 130), anchor="rb")

    # ================= RIGHT PAGE: visa stamps =================
    d.text((752, 52), "VISAS", font=font(SERIF_B, 16), fill=(28, 42, 66), anchor="mt")
    d.text((752, 72), "V I S A S   ·   E N T R Y   ·   E X I T", font=font(SANS, 9),
           fill=(100, 110, 125), anchor="mt")
    d.line([(540, 92), (964, 92)], fill=(43, 72, 110), width=1)

    stamps = [
        # (x, y, rotate, country, city, kind, date, ink)
        (548, 108, -4, "NORWAY", "BERGEN", "ENTRY", "11 MAR 2024", (32, 84, 150, 215)),
        (742, 108, 3, "NORWAY", "BERGEN", "EXIT", "18 MAR 2024", (150, 52, 40, 205)),
        (548, 216, 4, "FAROE ISLANDS", "TÓRSHAVN", "ENTRY", "22 JUN 2024", (38, 110, 62, 205)),
        (742, 216, -3, "FAROE ISLANDS", "TÓRSHAVN", "EXIT", "30 JUN 2024", (32, 84, 150, 215)),
        (548, 324, -2, "ICELAND", "REYKJAVÍK", "ENTRY", "05 SEP 2024", (150, 52, 40, 205)),
        (742, 324, 5, "ICELAND", "REYKJAVÍK", "EXIT", "12 SEP 2024", (38, 110, 62, 205)),
    ]
    for (x, y, rot, country, city, kind, date, ink) in stamps:
        layer = stamp_layer((188, 104), rot,
                            lambda dd, sz, c=country, ci=city, k=kind, da=date, ik=ink:
                            entry_stamp(dd, sz, c, ci, k, da, ik))
        img.paste(layer, (x, y), layer)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- the telling detail: Condition 7 (wool declaration) ----
    d.rounded_rectangle([548, 436, 736, 532], radius=4, outline=(43, 72, 110, 235), width=2)
    d.text((642, 446), "CONDITION 7", font=font(SANS_B, 13), fill=(43, 72, 110, 235), anchor="mt")
    d.text((642, 466), "THE HOLDER MUST", font=font(SANS_B, 11), fill=(43, 72, 110, 235), anchor="mt")
    d.text((642, 481), "DECLARE ALL WOOL", font=font(SANS_B, 11), fill=(43, 72, 110, 235), anchor="mt")
    d.text((642, 496), "AND DOWN ON ARRIVAL", font=font(SANS_B, 11), fill=(43, 72, 110, 235), anchor="mt")
    d.text((642, 514), "MINISTRY OF THE INTERIOR", font=font(SANS, 8), fill=(43, 72, 110, 235), anchor="mt")

    # return-home stamp, right of the condition box
    layer = stamp_layer((206, 104), -2,
                        lambda dd, sz: entry_stamp(dd, sz, "ALDERMERE", "SKARDVIK",
                                                   "ARRIVAL", "12 SEP 2024", (43, 72, 110, 225)))
    img.paste(layer, (756, 432), layer)
    d = ImageDraw.Draw(img, "RGBA")

    # small round fee stamp overlapping the condition box corner
    fee = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fee)
    fd.ellipse([8, 8, 112, 112], outline=(150, 52, 40, 220), width=3)
    fd.ellipse([16, 16, 104, 104], outline=(150, 52, 40, 220), width=1)
    fd.text((60, 34), "PUFFIN LEVY", font=font(SANS_B, 11), fill=(150, 52, 40, 220), anchor="mt")
    fd.text((60, 50), "PAID", font=font(SANS_B, 13), fill=(150, 52, 40, 220), anchor="mt")
    fd.text((60, 68), "40 KR", font=font(SANS_B, 12), fill=(150, 52, 40, 220), anchor="mt")
    fd.text((60, 84), "SKARDVIK", font=font(SANS, 8), fill=(150, 52, 40, 220), anchor="mt")
    fee = fee.rotate(14, resample=Image.BICUBIC)
    img.paste(fee, (700, 512), fee)
    d = ImageDraw.Draw(img, "RGBA")

    # faint watermark
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    wd.text((752, 590), "ALDERMERE", font=font(SERIF_B, 44), fill=(43, 72, 110, 16), anchor="mm")
    wm = wm.rotate(-18, center=(752, 590), resample=Image.BICUBIC)
    img.paste(wm, (0, 0), wm)

    d.text((964, 640), "3", font=font(SANS, 11), fill=(110, 118, 130), anchor="rb")

    img.save(OUT, optimize=True)
    import os
    print("saved", OUT, os.path.getsize(OUT), "bytes,", img.size)


if __name__ == "__main__":
    print("MRZ1:", mrz_line1(), len(mrz_line1()))
    print("MRZ2:", mrz_line2(), len(mrz_line2()))
    main()
