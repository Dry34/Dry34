"""Shared palette and helpers for the animated profile SVGs."""

from xml.sax.saxutils import escape

THEMES = {
    "light": {
        "bg": "#fffaf5",
        "border": "#ead9c6",
        "text": "#3d2f25",
        "muted": "#8a7563",
        "accent": "#b07a4f",
        "track": "#f1e4d6",
    },
    "dark": {
        "bg": "#17120e",
        "border": "#3a2c22",
        "text": "#f2e6da",
        "muted": "#b09a87",
        "accent": "#d9a679",
        "track": "#2a211a",
    },
}

# Seconds between two replays of the looping animations
CYCLE = 12

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"


def esc(s):
    return escape(str(s), {'"': "&quot;"})


def loop(name, start, end, action, timing="cubic-bezier(.15,.85,.25,1)"):
    """Keyframes that play over `action` seconds, hold, then rewind before the next cycle."""
    a = action / CYCLE * 100
    return (f"  @keyframes {name} {{ 0% {{ {start} animation-timing-function: {timing}; }} "
            f"{a:.2f}%, 94% {{ {end} }} 100% {{ {start} }} }}")


def looped(name, delay):
    return f"animation: {name} {CYCLE}s {delay:.2f}s infinite backwards"


ROLL = loop("roll", "transform: translateY(0);", "transform: translateY(var(--y));", 1.8)


def odometer(uid, text, x, top, t, delay, size=30, fill=None, weight=700, anchor="middle"):
    """Each digit is a 0-9 column that rolls up to its final value."""
    cw, h = size * 0.62, size * 1.3
    widths = [cw * 0.45 if ch in ",." else cw for ch in text]
    x0 = {"middle": x - sum(widths) / 2, "end": x - sum(widths)}[anchor]
    out = [f'<clipPath id="odo{uid}"><rect x="{x0 - 4:.1f}" y="{top}" width="{sum(widths) + 8:.1f}" height="{h:.1f}"/></clipPath>',
           f'<g clip-path="url(#odo{uid})" class="mono" font-size="{size}" font-weight="{weight}" fill="{fill or t["accent"]}" text-anchor="middle">']
    for i, ch in enumerate(text):
        cx = x0 + sum(widths[:i]) + widths[i] / 2
        if not ch.isdigit():
            out.append(f'<text x="{cx:.1f}" y="{top + size:.1f}">{ch}</text>')
            continue
        stop = (10 + int(ch)) * h
        out.append(f'<g style="--y: -{stop:.1f}px; transform: translateY(var(--y)); {looped("roll", delay + i * 0.08)}">')
        out.extend(f'<text x="{cx:.1f}" y="{top + k * h + size:.1f}">{k % 10}</text>' for k in range(20))
        out.append("</g>")
    out.append("</g>")
    return "\n".join(out)


def card(width, height, t, body, extra_css=""):
    """Wraps body in a rounded card."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
  text {{ font-family: {SANS}; }}
  .mono {{ font-family: {MONO}; }}
  .title {{ font-size: 15px; font-weight: 700; fill: {t["text"]}; }}
  .sub {{ font-size: 11px; fill: {t["muted"]}; }}
  .fade {{ opacity: 0; animation: fade .6s ease-out forwards; }}
  @keyframes fade {{ to {{ opacity: 1; }} }}
{extra_css}
</style>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>
{body}
</svg>
"""
