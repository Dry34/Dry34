"""Renders animated stats cards from jstrieb/github-stats JSON output.

Usage: python3 render_stats.py <stats.json> <output-dir>
Writes stats-{light,dark}.svg and languages-{light,dark}.svg.
Honors the EXCLUDE_REPOS / EXCLUDE_LANGS env vars (comma-separated globs).
"""

import json
import os
import sys
from fnmatch import fnmatch

from theme import CYCLE, ROLL, THEMES, card, esc, loop, odometer

WIDTH = 800
TOP_LANGS = 8


def globs(var):
    return [g.strip().lower() for g in os.environ.get(var, "").split(",") if g.strip()]


def matches(name, patterns):
    return any(fnmatch(name.lower(), p) for p in patterns)


def aggregate(raw):
    exclude_repos, exclude_langs = globs("EXCLUDE_REPOS"), globs("EXCLUDE_LANGS")
    repos = [r for r in raw["repositories"] if not matches(r["name"], exclude_repos)]
    sizes, colors = {}, {}
    for repo in repos:
        for lang in repo.get("languages") or []:
            if matches(lang["name"], exclude_langs):
                continue
            sizes[lang["name"]] = sizes.get(lang["name"], 0) + lang["size"]
            if lang.get("color"):
                colors[lang["name"]] = lang["color"]
    contributions = sum(
        raw.get(k, 0)
        for k in ("repo_contributions", "issue_contributions", "commit_contributions",
                  "pr_contributions", "review_contributions")
    )
    return {
        "contributions": contributions,
        "lines": sum(r["lines_changed"] for r in repos),
        "repos": len(repos),
        "sizes": sizes,
        "colors": colors,
    }


def stats_svg(data, t):
    tiles = [
        ("contributions", data["contributions"], "all-time contributions"),
        ("lines", data["lines"], "lines of code changed"),
        ("langs", len(data["sizes"]), "languages written"),
    ]
    tile_w = (WIDTH - 48) / len(tiles)
    body = [
        f'<text x="24" y="34" class="title">GitHub activity</text>',
        f'<text x="{WIDTH - 24}" y="34" class="sub" text-anchor="end">all-time · private &amp; organization repos included · updated daily</text>',
    ]
    for i, (uid, value, label) in enumerate(tiles):
        cx = 24 + tile_w * i + tile_w / 2
        delay = 0.2 + i * 0.25
        body.append(odometer(uid, f"{value:,}", cx, 62, t, delay))
        body.append(f'<rect x="{cx - 22:.1f}" y="112" width="44" height="3" rx="1.5" fill="{t["accent"]}" class="grow" style="animation-delay: {delay + 1.2:.2f}s"/>')
        body.append(f'<text x="{cx:.1f}" y="138" class="sub fade" font-size="12" text-anchor="middle" style="animation-delay: {delay + 0.6:.2f}s">{esc(label)}</text>')
        if i:
            body.append(f'<line x1="{24 + tile_w * i:.1f}" y1="66" x2="{24 + tile_w * i:.1f}" y2="140" stroke="{t["border"]}"/>')
    css = f"""{ROLL}
  .grow {{ transform-box: fill-box; transform-origin: center; animation: grow {CYCLE}s infinite backwards; }}
{loop("grow", "transform: scaleX(0);", "transform: scaleX(1);", 0.6, "ease-out")}"""
    return card(WIDTH, 165, t, "\n".join(body), css)


def luminance(hex_color):
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def readable(color, t):
    """Swaps language colors that would vanish into the card background."""
    if abs(luminance(color) - luminance(t["bg"])) < 0.08:
        return t["muted"]
    return color


def languages_svg(data, t):
    total = sum(data["sizes"].values()) or 1
    ranked = sorted(data["sizes"].items(), key=lambda kv: kv[1], reverse=True)
    langs = [(name, size / total * 100, readable(data["colors"].get(name, t["muted"]), t)) for name, size in ranked[:TOP_LANGS]]
    rest = sum(size for _, size in ranked[TOP_LANGS:])
    if rest:
        langs.append(("Other", rest / total * 100, t["muted"]))

    bar_x, bar_w = 24, WIDTH - 48
    body = [
        f'<text x="24" y="34" class="title">Most used languages</text>',
        f'<text x="{WIDTH - 24}" y="34" class="sub" text-anchor="end">by code size across every repo I contribute to</text>',
        f'<clipPath id="barClip"><rect x="{bar_x}" y="52" width="{bar_w}" height="10" rx="5"/></clipPath>',
        f'<rect x="{bar_x}" y="52" width="{bar_w}" height="10" rx="5" fill="{t["track"]}"/>',
        f'<clipPath id="barFill"><rect class="fill" x="{bar_x}" y="52" width="{bar_w}" height="10" style="animation-delay: .2s"/></clipPath>',
        '<g clip-path="url(#barClip)"><g clip-path="url(#barFill)">',
    ]
    x = bar_x
    for i, (name, pct, color) in enumerate(langs):
        w = bar_w * pct / 100
        body.append(f'<rect x="{x:.2f}" y="52" width="{w + 0.5:.2f}" height="10" fill="{color}"/>')
        x += w
    body.append("</g></g>")

    col_w, row_h, top = (WIDTH - 48 - 32) / 2, 40, 92
    biggest = langs[0][1] if langs else 1
    for i, (name, pct, color) in enumerate(langs):
        col, row = i % 2, i // 2
        lx, ly = 24 + col * (col_w + 32), top + row * row_h
        delay = 0.5 + i * 0.1
        body.append(f'<g class="fade" style="animation-delay: {delay:.2f}s">')
        body.append(f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{color}"/>')
        body.append(f'<text x="{lx + 18}" y="{ly}" font-size="13" font-weight="600" fill="{t["text"]}">{esc(name)}</text>')
        body.append("</g>")
        body.append(odometer(f"pct{i}", f"{pct:.1f}%", lx + col_w, ly - 13, t, delay + 0.2, size=12, fill=t["muted"], weight=600, anchor="end"))
        body.append(f'<rect x="{lx}" y="{ly + 9}" width="{col_w:.1f}" height="4" rx="2" fill="{t["track"]}"/>')
        body.append(f'<rect x="{lx}" y="{ly + 9}" width="{max(col_w * pct / biggest, 4):.1f}" height="4" rx="2" fill="{color}" class="grow" style="animation-delay: {delay + 0.2:.2f}s"/>')
    height = top + ((len(langs) + 1) // 2) * row_h
    css = f"""{ROLL}
  .grow {{ transform-box: fill-box; transform-origin: left; animation: grow {CYCLE}s infinite backwards; }}
{loop("grow", "transform: scaleX(0);", "transform: scaleX(1);", 1.6)}
  .fill {{ transform-box: fill-box; transform-origin: left; animation: fill {CYCLE}s infinite backwards; }}
{loop("fill", "transform: scaleX(0);", "transform: scaleX(1);", 4.5, "cubic-bezier(.45,.05,.35,1)")}"""
    return card(WIDTH, height, t, "\n".join(body), css)


def main():
    src, out_dir = sys.argv[1], sys.argv[2]
    with open(src) as f:
        data = aggregate(json.load(f))
    os.makedirs(out_dir, exist_ok=True)
    for theme, t in THEMES.items():
        for name, render in (("stats", stats_svg), ("languages", languages_svg)):
            with open(os.path.join(out_dir, f"{name}-{theme}.svg"), "w") as f:
                f.write(render(data, t))


if __name__ == "__main__":
    main()
