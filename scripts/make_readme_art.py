"""Build the animated SVG panels used by the profile README. Standard library only."""
import math, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets"
MONO = "ui-monospace,Menlo,Consolas,DejaVu Sans Mono,monospace"
BG, FG, DIM, GREEN, GOLD, BLUE = "#04070f", "#f2f8ff", "#8da3c4", "#9dffc0", "#ffd678", "#7dc4ff"


def text(x, y, s, size=22, fill=FG, extra=""):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {extra}>{s}</text>'


def svg(name, h, css, body, frame=None):
    border = f'<rect x="1" y="1" width="718" height="{h - 2}" rx="12" fill="none" stroke="{frame}" stroke-opacity=".45" stroke-width="2"/>' if frame else ""
    run = (f'<rect x="1" y="1" width="718" height="{h - 2}" rx="12" fill="none" stroke="{frame}" stroke-width="3" '
           f'pathLength="1000" stroke-dasharray="90 910" style="animation:run 5s linear infinite"/>') if frame else ""
    (OUT / f"{name}.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 {h}" width="720" height="{h}" font-family="{MONO}">'
        f'<style>@keyframes run{{to{{stroke-dashoffset:-1000}}}}{css}'
        f'@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>'
        f'<rect width="720" height="{h}" rx="12" fill="{BG}"/>{body}{border}{run}</svg>', encoding="utf-8")


def typing():
    lines = ["$ whoami  ->  AI backend engineer in the making", "$ cat focus  ->  backends, LLM tooling, realtime",
             "$ uptime  ->  B.Tech IT, class of 2028"]
    css, body = [], []
    for i, s in enumerate(lines):
        w = len(s) * 12.1
        a, b, c = i * 33.3, i * 33.3 + 15, i * 33.3 + 31
        css.append(f"@keyframes w{i}{{0%,{a:.1f}%{{width:0}}{b:.1f}%,{c:.1f}%{{width:{w:.0f}px}}{c + 1:.1f}%,100%{{width:0}}}}")
        body.append(f'<clipPath id="c{i}"><rect x="30" y="0" height="70" width="{w if i == 0 else 0}" style="animation:w{i} 12s linear infinite"/></clipPath>'
                    f'<g clip-path="url(#c{i})">' + text(30, 43, s, 20, GREEN, f'textLength="{w:.0f}"') + "</g>")
    svg("typing", 70, "".join(css), "".join(body), GREEN)


def header(slug, title, col):
    css = "@keyframes march{to{transform:translateX(-24px)}}"
    chev = "".join(text(300 + i * 24, 39, ">", 22, col, f'opacity="{.15 + .85 * (i % 6) / 6:.2f}"') for i in range(20))
    body = (text(24, 40, title, 28, col, 'font-weight="bold"')
            + f'<clipPath id="k"><rect x="320" y="0" width="376" height="60"/></clipPath><g clip-path="url(#k)">'
            f'<g style="animation:march .8s linear infinite">{chev}</g></g>')
    svg(slug, 60, css, body)


def card(slug, num, title, role, lines, stack, col, css, art):
    body = (text(28, 40, f"QUEST {num}", 16, GOLD, 'font-weight="bold"') + text(692, 40, role, 16, DIM, 'text-anchor="end"')
            + text(28, 88, title, 36, col, 'font-weight="bold"')
            + "".join(text(28, 126 + i * 27, s, 17) for i, s in enumerate(lines))
            + text(28, 262, stack, 16, BLUE) + text(692, 262, "OPEN >", 16, GREEN, 'text-anchor="end" font-weight="bold" style="animation:blink 1.2s step-end infinite"')
            + art)
    svg(slug, 285, "@keyframes blink{50%{opacity:.25}}" + css, body, col)


def nexus():
    col, nodes, css = "#6fa8ff", [], ["@keyframes flow{to{stroke-dashoffset:-30}}@keyframes pulse{50%{opacity:.35}}"]
    cx, cy = 585, 140
    for i, n in enumerate(["AWS", "GCP", "AZ", "R2", "B2", "OCI", "IBM"]):
        a = -math.pi / 2 + i * 2 * math.pi / 7
        x, y = cx + 88 * math.cos(a), cy + 72 * math.sin(a)
        nodes.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{cx}" y2="{cy}" stroke="{col}" stroke-width="3" stroke-dasharray="4 11" style="animation:flow {.8 + i % 3 * .3:.1f}s linear infinite"/>')
        nodes.append(f'<rect x="{x - 21:.0f}" y="{y - 12:.0f}" width="42" height="24" rx="5" fill="{BG}" stroke="{col}"/>' + text(round(x), round(y) + 5, n, 12, FG, 'text-anchor="middle"'))
    nodes.append(f'<circle cx="{cx}" cy="{cy}" r="25" fill="{col}" style="animation:pulse 1.6s infinite"/>' + text(cx, cy + 5, "DISK", 12, BG, 'text-anchor="middle" font-weight="bold"'))
    card("nexuscloud", "01", "NexusCloud", "PROJECT LEAD", ["Seven free cloud tiers, one disk.", "A router picks the bucket."],
         "FastAPI · PostgreSQL · Redis · React", col, "".join(css), "".join(nodes))


def siddai():
    col = "#c3a5ff"
    models = ["gpt-4o", "gemini-2.5-flash", "grok-4.3", "llama3.2", "kimi-k2.5"]
    css = "@keyframes m{0%{opacity:1}20%,100%{opacity:0}}"
    art = f'<rect x="458" y="70" width="234" height="140" rx="10" fill="#0d0a1c" stroke="{col}"/>' + text(474, 100, "AiClient", 17, FG) + text(474, 128, ".chatQuick(", 17, FG)
    for i, m in enumerate(models):
        art += text(488, 160, f'"{m}",', 17, GOLD, f'font-weight="bold" opacity="{1 if i == 0 else 0}" style="animation:m 7.5s step-end {i * 1.5 - 7.5}s infinite"')
    art += text(488, 190, "prompt);", 17, FG)
    card("sidd-ai", "02", "sidd-ai", "CREATOR", ["One Java call, 8 AI providers.", "600+ Maven Central downloads."],
         "Java 17 · Maven · JUnit 5 · Apache 2.0", col, css, art)


def coedit():
    """The council run: seats draft, critique each other, then merge into the three handoff files."""
    col = "#ff8a5c"
    dur = 9
    css = ["@keyframes orbit{to{stroke-dashoffset:-60}}@keyframes beat{50%{opacity:.35}}",
           "@keyframes p0{0%,32%{opacity:1}33%,100%{opacity:0}}",
           "@keyframes p1{0%,32%{opacity:0}33%,65%{opacity:1}66%,100%{opacity:0}}",
           "@keyframes p2{0%,65%{opacity:0}66%,100%{opacity:1}}"]

    def phase(i, inner, still=0):
        return f'<g opacity="{still}" style="animation:p{i} {dur}s step-end infinite">{inner}</g>'

    seats = [(575, 80), (505, 164), (645, 164)]
    ring = "M575 80 L645 164 L505 164 Z"
    art = f'<path d="{ring}" fill="none" stroke="#5a3a30" stroke-width="2"/>'
    art += phase(1, f'<path d="{ring}" fill="none" stroke="{GOLD}" stroke-width="5" stroke-linecap="round" '
                    f'stroke-dasharray="2 18" style="animation:orbit .9s linear infinite"/>')
    for i, ((x, y), c) in enumerate(zip(seats, ["#ff8a5c", "#7dc4ff", "#9dffc0"])):
        art += (f'<circle cx="{x}" cy="{y}" r="23" fill="{BG}" stroke="{c}" stroke-width="3"/>'
                f'<circle cx="{x}" cy="{y}" r="9" fill="{c}" style="animation:beat 1.2s {-i * .4}s infinite"/>')
    for i, label in enumerate(["DRAFT", "CRITIQUE"]):
        art += phase(i, text(575, 215, label, 16, GOLD, 'text-anchor="middle" font-weight="bold"'), 1 if i == 0 else 0)
    files = f'<rect x="462" y="52" width="228" height="174" rx="8" fill="{BG}"/>'
    for i, n in enumerate(["AGENTS", "ARCHITECTURE", "PRD"]):
        y = 70 + i * 46
        files += (f'<path d="M470 {y}h192l18 14v24h-210z" fill="#f6efe0"/><path d="M662 {y}v14h18z" fill="{col}"/>'
                  + text(484, y + 26, n + ".md", 15, "#1c1a17", 'font-weight="bold"'))
    art += phase(2, files)
    card("coedit", "03", "Coedit", "SOLO BUILD", ["Live docs, sheets and drawings.", "AI council. Runs locally for now."],
         "Next.js · Yjs · FastAPI · PostgreSQL", col, "".join(css), art)


def swara():
    col = "#ebc96e"
    css = "@keyframes eq{0%,100%{transform:scaleY(.15)}50%{transform:scaleY(1)}}"
    art = "".join(
        f'<rect x="{478 + i * 15}" y="80" width="9" height="140" rx="3" fill="{col}" opacity="{.55 + .45 * (i % 3) / 2:.2f}" '
        f'style="transform-box:fill-box;transform-origin:bottom;transform:scaleY({.2 + .7 * abs(math.sin(i * 1.7)):.2f});animation:eq {.7 + (i * 7 % 5) * .17:.2f}s ease-in-out {-i * .13:.2f}s infinite"/>'
        for i in range(14))
    card("swara", "04", "Swara", "SOLO BUILD", ["Offline Android music player.", "On-device AI karaoke, ~23 ms."],
         "Java · Media3 · Room · ONNX Runtime", col, css, art)


def stack():
    rows = [["Java", "Python", "FastAPI", "Spring Boot", "PostgreSQL", "Redis"],
            ["Docker", "Kubernetes", "GCP Cloud Run", "Android", "Yjs", "GitHub Actions"]]
    css, body = [], []
    for r, items in enumerate(rows):
        chips, x = "", 0
        for n in items:
            w = len(n) * 12 + 30
            chips += f'<rect x="{x}" y="0" width="{w}" height="42" rx="8" fill="#0b1426" stroke="{GREEN}" stroke-opacity=".5"/>' + text(x + w / 2, 28, n, 20, FG, 'text-anchor="middle"')
            x += w + 14
        a, b = ("0", f"-{x}px") if r == 0 else (f"-{x}px", "0")
        css.append(f"@keyframes s{r}{{from{{transform:translateX({a})}}to{{transform:translateX({b})}}}}")
        body.append(f'<g transform="translate(0,{18 + r * 56})"><g style="animation:s{r} {22 + r * 4}s linear infinite">{chips}'
                    f'<g transform="translate({x},0)">{chips}</g></g></g>')
    svg("stack", 132, "".join(css), "".join(body))


def footer():
    css = "@keyframes sea{to{transform:translateX(-96px)}}"
    body = ""
    for i, (col, d) in enumerate([("#2a5f92", 5), ("#3a86c4", 3.5), ("#4ea6e8", 2.4)]):
        body += f'<g style="animation:sea {d}s linear infinite">' + text(-i * 20, 26 + i * 16, "~~~~--  " * 14, 20, col, 'xml:space="preserve" textLength="1344"') + "</g>"
    body += text(360, 94, "thanks for visiting", 18, GREEN, 'text-anchor="middle"')
    svg("footer", 108, css, body)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    typing()
    header("h-quests", "FLAGSHIPS", GOLD)
    header("h-stack", "INVENTORY", GREEN)
    header("h-snake", "SNAKE RUN", BLUE)
    header("h-leet", "TRAINING", "#ff9de1")
    nexus(); siddai(); coedit(); swara(); stack(); footer()
