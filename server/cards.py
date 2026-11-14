"""Pictures Spenzo sends in chat: spending charts and the monthly Wrapped card.

Drawn with Pillow in the website's colours and fonts (Bricolage Grotesque for headlines and
numbers, Hanken Grotesk for text), at 1080 px wide so they stay sharp on any phone.
Hanken has no ₹ glyph, so ₹ is always drawn in Bricolage.
"""
import io
import re
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).parent / "assets"
PAPER, CARD, INK, MUTED, LINE = "#F3F6F0", "#FFFFFF", "#0E2A1F", "#56675D", "#DAE3D8"
LEAF, LEAF_DEEP, LEAF_SOFT, MANGO, MANGO_SOFT = "#2E9E47", "#1D7533", "#E3F2DF", "#FFB627", "#FFF1D6"
NIGHT, NIGHT_TILE, PAPER_DIM = "#0E2A1F", "#173B2C", "#B9CBBE"
W = 1080


@lru_cache(maxsize=64)
def font(size: int, weight: int = 500, display: bool = False) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(ASSETS / "fonts" / ("Bricolage.ttf" if display else "Hanken.ttf")), size)
    f.set_variation_by_axes([min(size, 96), max(weight, 200), 100] if display else [weight])
    return f


@lru_cache(maxsize=8)
def mascot(name: str) -> Image.Image:
    return Image.open(ASSETS / f"baaz-{name}.png").convert("RGBA")


def _pieces(text: str, f: ImageFont.FreeTypeFont):
    """Split text so ₹ is drawn in Bricolage when the font is Hanken."""
    if "Bricolage" in f.path:
        return [(text, f)]
    rupee = font(f.size, 600, display=True)
    return [(part, rupee if part == "₹" else f) for part in re.split(r"(₹)", text) if part]


def width(text: str, f: ImageFont.FreeTypeFont) -> int:
    return int(sum(face.getlength(part) for part, face in _pieces(text, f)))


def text(d: ImageDraw.ImageDraw, xy: tuple[float, float], s: str, f: ImageFont.FreeTypeFont, fill: str,
         anchor: str = "l") -> None:
    """Draw s with its top at y. anchor l / r / m sets where x is."""
    x, y = xy
    total = width(s, f)
    x = x - total if anchor == "r" else x - total / 2 if anchor == "m" else x
    for part, face in _pieces(s, f):
        d.text((x, y), part, font=face, fill=fill)
        x += face.getlength(part)


def fit(s: str, f: ImageFont.FreeTypeFont, max_width: int) -> str:
    """Shorten s with … until it fits."""
    if width(s, f) <= max_width:
        return s
    while s and width(s + "…", f) > max_width:
        s = s[:-1]
    return s.rstrip() + "…"


def short_inr(amount: float) -> str:
    """₹12.4k, ₹1.2L: for chart labels."""
    if amount >= 100_000:
        return f"₹{amount / 100_000:.1f}L".replace(".0L", "L")
    if amount >= 1000:
        return f"₹{amount / 1000:.1f}k".replace(".0k", "k")
    return f"₹{amount:,.0f}"


def png(im: Image.Image) -> bytes:
    out = io.BytesIO()
    im.convert("RGB").save(out, "PNG", optimize=True)
    return out.getvalue()


def _frame(title: str, subtitle: str, total: str, height: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGB", (W, height), PAPER)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 40, W - 40, height - 40), radius=44, fill=CARD, outline=LINE, width=2)
    text(d, (96, 100), fit(title, font(54, 800, True), W - 300), font(54, 800, True), INK)
    text(d, (96, 172), fit(subtitle, font(30, 500), W - 300), font(30, 500), MUTED)
    text(d, (96, 226), total, font(76, 800, True), LEAF_DEEP)
    icon = mascot("icon")
    im.paste(icon, (W - 96 - icon.width, 96), icon)
    text(d, (W - 96, height - 104), "spenzo.aravarun.in", font(26, 600), MUTED, anchor="r")
    text(d, (96, height - 104), "Spenzo", font(28, 800, True), LEAF_DEEP)
    return im, d


def bars(title: str, subtitle: str, total: str, rows: list[tuple[str, float]]) -> bytes:
    """Horizontal bars, biggest first: spending by category or by merchant."""
    rows = rows[:8]
    height = 420 + 112 * len(rows) + 120
    im, d = _frame(title, subtitle, total, height)
    top = max((v for _, v in rows), default=1) or 1
    y = 380
    label, value = font(32, 600), font(32, 700, True)
    for name, amount in rows:
        amount_text = short_inr(amount)
        text(d, (96, y), fit(name, label, W - 400), label, INK)
        text(d, (W - 96, y - 2), amount_text, value, INK, anchor="r")
        bar_y, full = y + 50, W - 192
        d.rounded_rectangle((96, bar_y, 96 + full, bar_y + 26), radius=13, fill=LEAF_SOFT)
        d.rounded_rectangle((96, bar_y, 96 + max(26, int(full * amount / top)), bar_y + 26), radius=13, fill=LEAF)
        y += 112
    return png(im)


def columns(title: str, subtitle: str, total: str, labels: list[str],
            series: list[tuple[str, list[float], str]]) -> bytes:
    """Vertical bars over time (months or days). Two series sit side by side, with a legend."""
    height, chart_top, chart_bottom = 1080, 400, 860
    im, d = _frame(title, subtitle, total, height)
    top = max((v for _, values, _ in series for v in values), default=1) or 1
    n, groups = len(series), len(labels)
    left, right = 96, W - 96
    slot = (right - left) / max(groups, 1)
    gap = slot * (0.28 if groups <= 12 else 0.18)
    bar_w = (slot - gap) / n
    d.line((left, chart_bottom, right, chart_bottom), fill=LINE, width=3)
    every = 1 if groups <= 12 else 5
    value_font, label_font = font(24 if groups <= 6 else 20, 700, True), font(24, 600)
    for i, lab in enumerate(labels):
        x0 = left + i * slot + gap / 2
        for j, (_, values, colour) in enumerate(series):
            v = values[i]
            h = (chart_bottom - chart_top - 40) * v / top
            bx = x0 + j * bar_w
            if v > 0:
                d.rounded_rectangle((bx + 2, chart_bottom - max(h, 8), bx + bar_w - 2, chart_bottom),
                                    radius=min(10, bar_w / 3), fill=colour)
            if v > 0 and groups <= 12 and (n == 1 or bar_w > 40):
                text(d, (bx + bar_w / 2, chart_bottom - h - 34), short_inr(v), value_font, INK, anchor="m")
        if i % every == 0 or i == groups - 1:
            text(d, (x0 + (slot - gap) / 2, chart_bottom + 16), lab, label_font, MUTED, anchor="m")
    if n > 1:
        x = 96
        for name, _, colour in series:
            d.rounded_rectangle((x, 330, x + 26, 356), radius=7, fill=colour)
            text(d, (x + 38, 326), name, font(26, 600), INK)
            x += 60 + width(name, font(26, 600)) + 30
    return png(im)


def wrapped(month: str, total: str, line: str, tiles: list[tuple[str, str, str]]) -> bytes:
    """The month in one shareable card: a dark card with Baaz, the total and up to six tiles."""
    tiles = tiles[:6]
    rows = (len(tiles) + 1) // 2
    top = 640
    height = top + rows * 250 + 190
    im = Image.new("RGB", (W, height), NIGHT)
    d = ImageDraw.Draw(im)
    baaz = mascot("celebrate")
    im.paste(baaz, (W - baaz.width + 40, 40), baaz)
    text(d, (80, 96), "SPENZO WRAPPED", font(30, 800, True), MANGO)
    text(d, (80, 146), month, font(80, 800, True), PAPER)
    text(d, (80, 330), total, font(118, 800, True), "#FFFFFF")
    y = 480
    for part in _wrap(line, font(34, 500), 560):
        text(d, (80, y), part, font(34, 500), PAPER_DIM)
        y += 46
    tile_w = (W - 160 - 30) / 2
    for i, (label, value, detail) in enumerate(tiles):
        x = 80 + (i % 2) * (tile_w + 30)
        ty = top + (i // 2) * 250
        d.rounded_rectangle((x, ty, x + tile_w, ty + 220), radius=36, fill=NIGHT_TILE)
        text(d, (x + 36, ty + 32), label.upper(), font(24, 700), MANGO)
        text(d, (x + 36, ty + 76), fit(value, font(50, 800, True), int(tile_w - 72)), font(50, 800, True), PAPER)
        text(d, (x + 36, ty + 150), fit(detail, font(28, 500), int(tile_w - 72)), font(28, 500), PAPER_DIM)
    text(d, (80, height - 118), "Get yours: say hi to Spenzo on WhatsApp", font(30, 600), PAPER)
    text(d, (80, height - 74), "spenzo.aravarun.in", font(28, 500), PAPER_DIM)
    return png(im)


def _wrap(s: str, f: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines, current = [], ""
    for word in s.split():
        trial = f"{current} {word}".strip()
        if width(trial, f) > max_width and current:
            lines.append(current)
            current = word
        else:
            current = trial
    return lines + [current] if current else lines
