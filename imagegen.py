import io
import random
import urllib.parse
import requests
from PIL import Image, ImageDraw, ImageFont
import config

W = H = 1080
M = 80
REG = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans.ttf",
       "/Library/Fonts/Arial.ttf", "C:/Windows/Fonts/arial.ttf"]
BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"]


def font(bold, size):
    for p in (BOLD if bold else REG):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def wrap(d, text, f, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def ai_background(prompt):
    full = f"{prompt}, {config.IMAGE_STYLE}"
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(full)
           + f"?width={W}&height={H}&nologo=true&seed={random.randint(1, 99999)}")
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    img = Image.open(io.BytesIO(r.content)).convert("RGB").resize((W, H))
    return Image.blend(img, Image.new("RGB", (W, H), (8, 12, 30)), 0.62)


def gradient():
    c1, c2 = random.choice(config.PALETTES)
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    return img


def make_card(draft, out_path):
    bg = None
    try:
        bg = ai_background(draft["image_prompt"])
    except Exception as e:
        print(f"[image] AI background failed, using gradient: {e}")
    if bg is None:
        bg = gradient()
    d = ImageDraw.Draw(bg)
    accent = config.ACCENT

    # tag pill
    tag = draft.get("tag", "TECH TIP").upper()[:24]
    tf = font(True, 28)
    tw = d.textlength(tag, font=tf)
    d.rounded_rectangle([M, 90, M + tw + 48, 90 + 56], radius=28, fill=accent)
    d.text((M + 24, 90 + 11), tag, font=tf, fill=(15, 23, 42))

    # headline (shrink until it fits in 4 lines)
    headline = draft["headline"].strip()
    for size in range(88, 44, -4):
        hf = font(True, size)
        lines = wrap(d, headline, hf, W - 2 * M)
        if len(lines) <= 4:
            break
    y = 200
    for ln in lines:
        d.text((M, y), ln, font=hf, fill="white")
        y += int(size * 1.22)
    d.rectangle([M, y + 14, M + 120, y + 22], fill=accent)
    y += 70

    # points
    pf, nf = font(False, 38), font(True, 38)
    for i, pt in enumerate(draft["points"][:3], 1):
        plines = wrap(d, pt, pf, W - 2 * M - 90)
        if y + len(plines) * 50 > H - 190:
            break
        d.text((M, y), f"0{i}", font=nf, fill=accent)
        for ln in plines:
            d.text((M + 90, y), ln, font=pf, fill=(226, 232, 240))
            y += 50
        y += 26

    # footer
    d.line([(M, H - 130), (W - M, H - 130)], fill=(100, 116, 139), width=2)
    d.text((M, H - 108), config.BRAND_NAME, font=font(True, 32), fill="white")
    d.text((M, H - 64), config.BRAND_TAGLINE, font=font(False, 26), fill=(148, 163, 184))
    bg.save(out_path, "PNG", optimize=True)
    return out_path
