"""Renders the static animated cards (header, about, PeakRando, Barcelona, tech stack) into assets/

Usage: python3 scripts/render_assets.py
Icons come from skillicons.dev and are inlined as data URIs.
"""

import base64
import math
import re
import os
import urllib.request

from theme import CYCLE, MONO, SANS, THEMES, card, esc, loop

WIDTH = 800
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

STACK = [
    ("Languages", ["ts", "js", "dart", "python", "cpp", "c", "java"]),
    ("Front & Mobile", ["react", "vite", "flutter", "vue", "nuxtjs", "html", "css"]),
    ("Back & Data", ["nestjs", "nodejs", "postgres", "firebase", "mongodb", "mysql"]),
    ("DevOps & Cloud", ["docker", "githubactions", "gcp", "kubernetes", "linux", "bash", "git"]),
]

BARCELONA = [
    ("☀️", "Sun", 100, "100%"),
    ("🐛", "Bugs fixed", 92, "(mostly not mine)"),
    ("🥘", "Paella", 84, "tried them all"),
    ("🗣️", "English", 88, "B2 → way more confident"),
    ("😴", "Siesta", 8, "segfaults don't sleep"),
]


def icon(name, theme):
    url = f"https://skillicons.dev/icons?i={name}&theme={theme}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return base64.b64encode(resp.read()).decode()


def stack_svg(theme, t):
    size, gap, label_w, row_h, top = 48, 12, 160, 66, 60
    body = [
        '<text x="24" y="34" class="title">Tech stack</text>',
        f'<text x="{WIDTH - 24}" y="34" class="sub" text-anchor="end">full-stack · web &amp; mobile · from C to full-stack dev</text>',
    ]
    n = 0
    for r, (label, icons) in enumerate(STACK):
        y = top + r * row_h
        body.append(f'<text x="24" y="{y + size / 2 + 5}" font-size="13" font-weight="600" fill="{t["muted"]}" class="fade" style="animation-delay: {r * 0.15:.2f}s">{esc(label)}</text>')
        for c, name in enumerate(icons):
            x = 24 + label_w + c * (size + gap)
            body.append(
                f'<g class="pop" style="animation-delay: {0.1 + n * 0.06:.2f}s">'
                f'<g class="float" style="animation-delay: {2.5 + n * 0.12:.2f}s">'
                f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="data:image/svg+xml;base64,{icon(name, theme)}"/>'
                "</g></g>"
            )
            n += 1
    css = f"""  .pop {{ transform-box: fill-box; transform-origin: center; animation: pop {CYCLE}s infinite backwards; }}
{loop("pop", "transform: scale(0);", "transform: scale(1);", 0.5, "cubic-bezier(.3,1.6,.5,1)")}
  .float {{ animation: float 3.2s ease-in-out infinite; }}
  @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-5px); }} }}"""
    return card(WIDTH, top + len(STACK) * row_h, t, "\n".join(body), css)


MISSIONS = [
    ("🧑‍🏫", [("Daily mentoring for ", 0), ("1st, 2nd and 3rd year", 1), (" students", 0)]),
    ("🛠️", [("Technical help across ", 0), ("C, C++, Python and Java", 1)]),
    ("🎤", [("Project defenses and technical ", 0), ("workshops", 1)]),
    ("📊", [("Tracking a whole class: progress, evaluations, coding standards", 0)]),
    ("🌍", [("Working day-to-day ", 0), ("in English", 1), (" in an international hub", 0)]),
]


def terminal(t, title, width, height, body, css):
    chrome = [
        '<circle cx="26" cy="22" r="6" fill="#ff5f57"/><circle cx="46" cy="22" r="6" fill="#febc2e"/><circle cx="66" cy="22" r="6" fill="#28c840"/>',
        f'<text x="{width / 2}" y="26" class="sub" text-anchor="middle">{esc(title)}</text>',
        f'<line x1="0" y1="42" x2="{width}" y2="42" stroke="{t["border"]}"/>',
    ]
    css += """
  .type { transform-box: fill-box; transform-origin: left; transform: scaleX(0); animation: type .7s steps(28) forwards; }
  @keyframes type { to { transform: scaleX(1); } }
  .blink { animation: blink 1s steps(1) infinite; }
  @keyframes blink { 50% { opacity: 0; } }"""
    return card(width, height, t, "\n".join(chrome + body), css)


def typed(uid, x, y, text_svg, chars, delay, size=13):
    """A line revealed left to right like it is being typed."""
    w = chars * size * 0.62 + 6
    return (f'<clipPath id="ty{uid}"><rect class="type" style="animation-delay: {delay:.2f}s" x="{x}" y="{y - size - 2}" width="{w:.1f}" height="{size + 8}"/></clipPath>'
            f'<text x="{x}" y="{y}" class="mono" font-size="{size}" clip-path="url(#ty{uid})" xml:space="preserve">{text_svg}</text>')


def prompt(t, uid, y, cmd, delay):
    return typed(uid, 24, y, f'<tspan fill="{t["accent"]}">➜</tspan><tspan fill="{t["text"]}"> {esc(cmd)}</tspan>', len(cmd) + 2, delay)


def barcelona_svg(t):
    bar_x, bar_w, row_h = 210, 300, 30
    body = [
        prompt(t, "c1", 68, "whoami", 0.3),
        f'<text x="24" y="94" font-size="14" font-weight="700" fill="{t["accent"]}" class="fade" style="animation-delay: 1s">Teaching Assistant · Epitech Barcelona hub · Jan → Jul 2026</text>',
        f'<text x="24" y="114" font-size="12" fill="{t["muted"]}" class="fade" style="animation-delay: 1.2s">Six months on the other side of the desk: helping students instead of being one.</text>',
        prompt(t, "c2", 148, "cat missions.txt", 1.6),
    ]
    y = 174
    for i, (emoji, parts) in enumerate(MISSIONS):
        spans = "".join(f'<tspan font-weight="{700 if bold else 400}" fill="{t["text"] if bold else t["muted"]}">{esc(txt)}</tspan>' for txt, bold in parts)
        body.append(f'<g class="slide" style="animation-delay: {2.3 + i * 0.15:.2f}s"><text x="24" y="{y}" font-size="13">{emoji}</text>'
                    f'<text x="50" y="{y}" font-size="13">{spans}</text></g>')
        y += 24
    y += 14
    body.append(prompt(t, "c3", y, "cat epitech-barcelona-2026.log", 3.2))
    top = y + 14
    for i, (emoji, label, pct, note) in enumerate(BARCELONA):
        ry = top + i * row_h
        delay = 3.9 + i * 0.3
        body.append(f'<g class="fade" style="animation-delay: {delay:.2f}s">')
        body.append(f'<text x="24" y="{ry + 15}" font-size="15">{emoji}</text>')
        body.append(f'<text x="54" y="{ry + 15}" class="mono" font-size="13" fill="{t["text"]}">{esc(label)}</text>')
        body.append(f'<rect x="{bar_x}" y="{ry + 4}" width="{bar_w}" height="12" rx="3" fill="{t["track"]}"/>')
        body.append("</g>")
        fill_cls = "siesta" if label == "Siesta" else "grow"
        body.append(f'<rect x="{bar_x}" y="{ry + 4}" width="{bar_w * pct / 100:.1f}" height="12" rx="3" fill="{t["accent"]}" class="{fill_cls}" style="animation-delay: {delay + 0.2:.2f}s"/>')
        body.append(f'<text x="{bar_x + bar_w + 16}" y="{ry + 15}" class="mono fade" font-size="12" fill="{t["muted"]}" style="animation-delay: {delay + 1:.2f}s">{esc(note)}</text>')
    cursor_y = top + len(BARCELONA) * row_h + 14
    body.append(f'<text x="24" y="{cursor_y}" class="mono fade" font-size="13" fill="{t["accent"]}" style="animation-delay: 6s">➜ <tspan class="blink">▋</tspan></text>')
    pct = lambda sec: f"{sec / CYCLE * 100:.2f}"
    css = f"""  .grow {{ transform-box: fill-box; transform-origin: left; animation: grow {CYCLE}s infinite backwards; }}
{loop("grow", "transform: scaleX(0);", "transform: scaleX(1);", 1.0)}
  .siesta {{ transform-box: fill-box; transform-origin: left; animation: siesta {CYCLE}s ease-in-out infinite backwards; }}
  @keyframes siesta {{ 0% {{ transform: scaleX(0); }} {pct(1.1)}%, {pct(1.4)}% {{ transform: scaleX(4.5); }} {pct(2.4)}%, 94% {{ transform: scaleX(1); }} 100% {{ transform: scaleX(0); }} }}
  .slide {{ opacity: 0; transform: translateX(10px); animation: slide .4s ease-out forwards; }}
  @keyframes slide {{ to {{ opacity: 1; transform: translateX(0); }} }}"""
    return terminal(t, "thibaut@barcelona: ~", WIDTH, cursor_y + 22, body, css)


ABOUT = [
    'const thibaut = {',
    '  location:   "Paris, France",',
    '  school:     "Epitech — Software Engineering Expert (RNCP 7)",',
    '  currently:  "Full-Stack Developer intern @ Tessan Group",',
    '  building:   "PeakRando 🏔️ — hiking app, team lead of 6",',
    '  previously: ["Teaching Assistant @ Epitech Barcelona", "Mobile & Web Dev @ Incarline"],',
    '  languages:  { french: "native", english: "B2, sharpened in Barcelona" },',
    '  traits:     ["autonomous", "adaptable", "team player", "good vibes"],',
    '  lookingFor: "a full-stack web & mobile internship 🚀",',
    '};',
]

TOKEN = re.compile(r'("[^"]*")|\b(const)\b|(\w+)(?=:)|([{}\[\],;:=])|([^"{}\[\],;:=]+?(?=["{}\[\],;:=]|\w+:|$))')


def highlight(line, t, string_color):
    out = []
    for m in TOKEN.finditer(line):
        text = m.group(0)
        if m.group(1):
            color = string_color
        elif m.group(2):
            color = "#e5533d"
        elif m.group(3):
            color = t["accent"]
        elif m.group(4):
            color = t["muted"]
        else:
            color = t["text"]
        out.append(f'<tspan fill="{color}">{esc(text)}</tspan>')
    return "".join(out)


def about_svg(theme, t):
    string_color = "#3f7d4f" if theme == "light" else "#9ccc9c"
    row_h, top = 22, 74
    body = []
    for i, line in enumerate(ABOUT):
        y = top + i * row_h
        body.append(f'<text x="44" y="{y}" class="mono" font-size="12" fill="{t["border"]}" text-anchor="end">{i + 1}</text>')
        body.append(typed(f"a{i}", 60, y, highlight(line, t, string_color), len(line), 0.3 + i * 0.3))
    y = top + len(ABOUT) * row_h
    body.append(f'<text x="44" y="{y}" class="mono" font-size="12" fill="{t["border"]}" text-anchor="end">{len(ABOUT) + 1}</text>')
    body.append(f'<text x="60" y="{y}" class="mono fade" font-size="13" fill="{t["accent"]}" style="animation-delay: {0.3 + len(ABOUT) * 0.3:.2f}s"><tspan class="blink">▋</tspan></text>')
    return terminal(t, "about-me.js", WIDTH, y + 24, body, "")


PEAKRANDO = [
    ("👥", "Team", "6 people · agile · I lead it"),
    ("📱", "Mobile", "Flutter"),
    ("🌐", "Web", "React + Vite"),
    ("⚙️", "Backend", "NestJS + PostgreSQL"),
    ("🤖", "AI", "Python modules for smarter hikes"),
    ("🗺️", "Partner", "French State &amp; IGN official map data"),
]


def peakrando_svg(t, snow):
    trail = "M150 236 C 200 228, 250 214, 246 196 S 196 172, 210 150 S 252 124, 240 104 S 226 82, 230 74"
    # One SMIL timeline: the trail draws itself, then the hiker walks it and the flag goes up
    def timeline(begin, end):
        return f'dur="{CYCLE}s" repeatCount="indefinite" calcMode="linear" keyTimes="0;{begin / CYCLE:.4f};{end / CYCLE:.4f};.94;1"'
    draw, top = timeline(0.3, 2.3), 6.6 / CYCLE
    body = [
        '<clipPath id="scene"><rect x="1" y="1" width="384" height="258" rx="12"/></clipPath>',
        f'<mask id="trailMask"><path d="{trail}" pathLength="1" stroke="#fff" stroke-width="8" fill="none" stroke-dasharray="1" stroke-dashoffset="1">'
        f'<animate attributeName="stroke-dashoffset" values="1;1;0;0;1" {draw}/></path></mask>',
        '<g clip-path="url(#scene)">',
        '<circle class="sun" cx="318" cy="84" r="18" fill="#f6c453"/>',
        f'<g class="cloud" opacity=".55" fill="{t["muted"]}"><rect x="0" y="64" width="56" height="14" rx="7"/><rect x="14" y="56" width="28" height="14" rx="7"/></g>',
        f'<g class="cloud slow" opacity=".35" fill="{t["muted"]}"><rect x="0" y="104" width="44" height="12" rx="6"/><rect x="10" y="97" width="22" height="12" rx="6"/></g>',
        f'<path d="M0 260 L0 236 L90 150 L130 180 L200 96 L250 150 L300 120 L386 236 L386 260 Z" fill="{t["muted"]}" opacity=".25"/>',
        f'<path d="M0 260 L0 236 L110 170 L160 200 L230 70 L290 160 L330 140 L386 236 L386 260 Z" fill="{t["accent"]}" opacity=".6"/>',
        f'<path d="M230 70 L215.5 97 L223 92 L231 99 L240 92 L248 97 Z" fill="{snow}"/>',
        '</g>',
        f'<path d="{trail}" mask="url(#trailMask)" stroke="{t["text"]}" stroke-width="2.5" stroke-dasharray="5 6" stroke-linecap="round" fill="none"/>',
        f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" dur="{CYCLE}s" repeatCount="indefinite" keyTimes="0;{top:.4f};{top + 0.02:.4f};.94;1"/>'
        f'<line x1="230" y1="72" x2="230" y2="46" stroke="{t["text"]}" stroke-width="2"/><path d="M230 46 L250 52 L230 58 Z" fill="#e5533d"/></g>',
        f'<circle r="5" fill="{t["bg"]}" stroke="{t["text"]}" stroke-width="2.5">'
        f'<animateMotion path="{trail}" keyPoints="0;0;1;1;0" dur="{CYCLE}s" repeatCount="indefinite" calcMode="linear" keyTimes="0;{2.6 / CYCLE:.4f};{top:.4f};.99;1"/>'
        f'<animate attributeName="opacity" values="0;1;1;0;0" dur="{CYCLE}s" repeatCount="indefinite" keyTimes="0;{0.5 / CYCLE:.4f};.94;.97;1"/>'
        '</circle>',
        f'<line x1="386" y1="24" x2="386" y2="236" stroke="{t["border"]}"/>',
        f'<text x="410" y="56" font-size="24" font-weight="800" fill="{t["text"]}" class="fade">PeakRando</text>',
        f'<text x="410" y="78" class="sub fade" style="animation-delay: .2s">Project Lead &amp; Full-Stack Dev · Epitech EIP · 2025 → today</text>',
    ]
    for i, (emoji, label, value) in enumerate(PEAKRANDO):
        y = 112 + i * 24
        body.append(f'<g class="slide" style="animation-delay: {0.5 + i * 0.25:.2f}s">')
        body.append(f'<text x="410" y="{y}" font-size="13">{emoji}</text>')
        body.append(f'<text x="436" y="{y}" font-size="12" font-weight="700" fill="{t["muted"]}">{label}</text>')
        body.append(f'<text x="500" y="{y}" font-size="13" fill="{t["text"]}">{value}</text>')
        body.append("</g>")
    css = f"""  .cloud {{ animation: drift 16s linear infinite; transform: translateX(-80px); }}
  .cloud.slow {{ animation-duration: 26s; animation-delay: -9s; }}
  @keyframes drift {{ to {{ transform: translateX(420px); }} }}
  .sun {{ transform-box: fill-box; transform-origin: center; animation: pulse 4s ease-in-out infinite; }}
  @keyframes pulse {{ 50% {{ transform: scale(1.12); }} }}
  .slide {{ opacity: 0; transform: translateX(14px); animation: slide .5s ease-out forwards; }}
  @keyframes slide {{ to {{ opacity: 1; transform: translateX(0); }} }}"""
    return card(WIDTH, 260, t, "\n".join(body), css)


TAGLINES = [
    "Hey 👋 I'm Thibaut",
    "Full-stack dev @ Tessan Group",
    "Ex teaching assistant @ Epitech Barcelona",
    "Building PeakRando 🏔️",
    "From C to full-stack dev, one commit at a time",
]


def wave(base, amp, period, width):
    pts = " ".join(f"L{x} {base + amp * math.sin(2 * math.pi * x / period):.1f}" for x in range(0, width + 1, 20))
    return f"M0 0 L0 {base} {pts} L{width} 0 Z"


def header_svg(t):
    slot, size = 3.2, 18
    cycle = slot * len(TAGLINES)
    body = [
        '<defs><linearGradient id="hg" x1="0" x2="1"><stop offset="0" stop-color="#7a5c45"/><stop offset="1" stop-color="#d9a679"/></linearGradient></defs>',
        f'<path class="wave back" d="{wave(150, 10, 400, 1600)}" fill="url(#hg)" opacity=".45"/>',
        f'<path class="wave" d="{wave(140, 12, 400, 1600)}" fill="url(#hg)"/>',
        '<text x="400" y="78" text-anchor="middle" font-size="46" font-weight="800" fill="#fff" class="fade">Thibaut Tavernier</text>',
        '<text x="400" y="112" text-anchor="middle" font-size="17" fill="#fff" opacity=".9" class="fade" style="animation-delay: .3s">Full-Stack Developer • Web &amp; Mobile</text>',
    ]
    for i, line in enumerate(TAGLINES):
        w = len(line) * size * 0.6 + 4
        x = 400 - w / 2
        body.append(f'<clipPath id="tl{i}"><rect class="type" style="animation-delay: {i * slot:.1f}s" x="{x:.1f}" y="176" width="{w:.1f}" height="28"/></clipPath>')
        body.append(f'<text x="{x:.1f}" y="196" class="mono" font-size="{size}" fill="{t["accent"]}" clip-path="url(#tl{i})">{esc(line)}</text>')
    type_end = 1.4 / cycle * 100
    hide_start = (slot - 0.4) / cycle * 100
    hide_end = slot / cycle * 100
    css = f"""  .wave {{ animation: wave 10s linear infinite; }}
  .wave.back {{ animation-duration: 16s; animation-direction: reverse; }}
  @keyframes wave {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-400px); }} }}
  .fade {{ opacity: 0; animation: fade .8s ease-out forwards; }}
  @keyframes fade {{ to {{ opacity: 1; }} }}
  .type {{ transform-box: fill-box; transform-origin: left; transform: scaleX(0); animation: type {cycle:.1f}s infinite backwards; }}
  @keyframes type {{
    0% {{ transform: scaleX(0); animation-timing-function: steps(24); }}
    {type_end:.2f}% {{ transform: scaleX(1); }}
    {hide_start:.2f}% {{ transform: scaleX(1); animation-timing-function: steps(12); }}
    {hide_end:.2f}%, 100% {{ transform: scaleX(0); }}
  }}"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="220" viewBox="0 0 800 220">
<style>
  text {{ font-family: {SANS}; }}
  .mono {{ font-family: {MONO}; }}
{css}
</style>
{chr(10).join(body)}
</svg>
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    for theme, t in THEMES.items():
        with open(os.path.join(OUT, f"header-{theme}.svg"), "w") as f:
            f.write(header_svg(t))
        with open(os.path.join(OUT, f"peakrando-{theme}.svg"), "w") as f:
            f.write(peakrando_svg(t, t["text"] if theme == "light" else "#f2e6da"))
        with open(os.path.join(OUT, f"tech-stack-{theme}.svg"), "w") as f:
            f.write(stack_svg(theme, t))
        with open(os.path.join(OUT, f"barcelona-{theme}.svg"), "w") as f:
            f.write(barcelona_svg(t))
        with open(os.path.join(OUT, f"about-{theme}.svg"), "w") as f:
            f.write(about_svg(theme, t))


if __name__ == "__main__":
    main()
