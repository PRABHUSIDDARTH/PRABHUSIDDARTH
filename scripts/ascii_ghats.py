"""Animated ASCII night over the Western Ghats. The front ridge is the last year of contributions."""
import json, math, os, random, sys, urllib.request

COLS, ROWS, CW, CH = 120, 58, 6, 10
FRAMES, STEP = 12, 0.2
W, H = COLS * CW, ROWS * CH
RIVER = 49
FONT = {
    "P": "####. #...# ####. #.... #....", "R": "####. #...# ####. #..#. #...#",
    "A": ".###. #...# ##### #...# #...#", "B": "####. #...# ####. #...# ####.",
    "H": "#...# #...# ##### #...# #...#", "U": "#...# #...# #...# #...# .###.",
    "S": ".#### #.... .###. ....# ####.", "I": "##### ..#.. ..#.. ..#.. #####",
    "D": "####. #...# #...# #...# ####.", "T": "##### ..#.. ..#.. ..#.. ..#..",
}


def fetch(user, token):
    q = ("query($u:String!){user(login:$u){contributionsCollection{contributionCalendar"
         "{weeks{contributionDays{contributionCount}}}}}}")
    req = urllib.request.Request("https://api.github.com/graphql",
                                 json.dumps({"query": q, "variables": {"u": user}}).encode(),
                                 {"Authorization": "bearer " + token})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks][-53:]


def sample():
    r = random.Random(11)
    return [max(0, int(6 + i * .7 + 12 * math.sin(i / 4) + r.randint(-8, 14))) for i in range(53)]


def front_ridge(weeks):
    """Top row of the front ridge for every column: busier weeks stand taller."""
    top = max(weeks + [1])
    raw = []
    for c in range(COLS):
        p = c * (len(weeks) - 1) / (COLS - 1)
        i = int(p)
        j = min(i + 1, len(weeks) - 1)
        raw.append(weeks[i] + (weeks[j] - weeks[i]) * (p - i))
    smooth = [sum(raw[max(0, c - 3):c + 4]) / len(raw[max(0, c - 3):c + 4]) for c in range(COLS)]
    return [round(43 - 13 * math.sqrt(v / top)) for v in smooth]


def put(g, x, y, ch, col):
    if 0 <= x < COLS and 0 <= y < ROWS:
        g[x, y] = (ch, col)


def draw(cells):
    """One <text> per same-colour run, with a fixed width so every font lines up."""
    out = []
    for y in sorted({k[1] for k in cells}):
        xs = sorted(k[0] for k in cells if k[1] == y)
        i = 0
        while i < len(xs):
            start, col = xs[i], cells[xs[i], y][1]
            run = ""
            while i < len(xs) and xs[i] == start + len(run) and cells[xs[i], y][1] == col:
                run += cells[xs[i], y][0]
                i += 1
            n = len(run)
            run = run.replace("&", "&amp;").replace("<", "&lt;")
            out.append(f'<text x="{start * CW}" y="{y * CH + 8}" textLength="{n * CW}" fill="{col}" xml:space="preserve">{run}</text>')
    return "".join(out)


def sprite(lines, col, bg=False):
    out = []
    for i, line in enumerate(lines):
        if bg:
            out.append(f'<rect x="0" y="{i * CH}" width="{len(line) * CW}" height="{CH}" fill="#04070f"/>')
        t = line.replace("&", "&amp;").replace("<", "&lt;")
        out.append(f'<text y="{i * CH + 8}" textLength="{len(line) * CW}" fill="{col}" xml:space="preserve">{t}</text>')
    return "".join(out)


def sky():
    r = random.Random(4)
    g = {}
    for y in range(0, 40):  # faint dithered gradient
        for x in range(COLS):
            if r.random() < .10 + y / 90:
                put(g, x, y, "." if y < 22 else ":", ["#17233f", "#1c2c4d", "#24385c", "#2f4468"][y // 10])
    for _ in range(170):
        put(g, r.randrange(COLS), r.randrange(30), r.choice("..+'"), r.choice(["#7d93b8", "#b9c9e6", "#5b719a"]))
    for dy in range(-5, 6):  # moon with craters
        for dx in range(-8, 9):
            d = (dx / 8) ** 2 + (dy / 5) ** 2
            if d <= 1:
                crater = (dx + 3) ** 2 + (dy * 2 + 2) ** 2 < 7 or (dx - 3) ** 2 + (dy * 2 - 3) ** 2 < 6
                ch, col = ("o", "#c9b46a") if crater else (("@", "#fff3c4") if d < .6 else ("%", "#e6d28c"))
                put(g, 104 + dx, 9 + dy, ch, col)
            elif d <= 1.5:
                put(g, 104 + dx, 9 + dy, ":", "#5d5a48")
    return g


def aurora(band):
    g = {}
    base, col = [(20, "#1f8f6a"), (24, "#2a6f9e"), (17, "#5a4fa0")][band]
    for x in range(COLS):
        y = int(base + 4 * math.sin(x / 13 + band * 2) + 2 * math.sin(x / 5 + band))
        for k in range(6):
            if (x * 3 + k * 5 + band) % (k + 2) == 0:
                put(g, x, y - k, "|!:'.."[k], col)
    return g


def far_ridges():
    r = random.Random(8)
    g = {}
    for x in range(COLS):
        a = int(31 + 5 * math.sin(x / 15 + 1) + 2 * math.sin(x / 4.3))
        b = int(37 + 3.5 * math.sin(x / 10 + 3) + 1.5 * math.sin(x / 3.1))
        for y in range(a, RIVER):
            lit = math.sin((x + y) / 4) > .4
            put(g, x, y, "^" if y == a else (":" if lit else "."), "#8fb0e6" if y == a else ("#45619a" if lit else "#2b4272"))
        for y in range(b, RIVER):
            put(g, x, y, "^" if y == b else r.choice("%*:"), "#5fc0b0" if y == b else ("#276a66" if r.random() < .5 else "#1d5254"))
    return g


def front(ridge):
    r = random.Random(9)
    g = {}
    for x in range(COLS):
        top = ridge[x]
        rising = ridge[max(0, x - 2)] > ridge[min(COLS - 1, x + 2)]  # slope facing the moon
        for y in range(top, RIVER):
            depth = y - top
            if depth == 0:
                put(g, x, y, "A" if x % 3 else "M", "#9dffc0")
            else:
                ramp = "#%&8" if depth > 5 else "&%*+"
                cols = ["#3fb572", "#2f9460", "#22744c", "#185938", "#10402a"]
                put(g, x, y, r.choice(ramp), cols[min(4, depth // 3 + (0 if rising else 1))])
    for x in range(2, COLS - 2, 5):  # trees along the slopes
        y = ridge[x] + r.randint(3, 6)
        if y < RIVER - 2:
            put(g, x, y - 1, "^", "#c6ffd9")
            for dx, ch in ((-1, "/"), (0, "|"), (1, "\\")):
                put(g, x + dx, y, ch, "#7be3a1")
            put(g, x, y + 1, "|", "#8a6f4d")
    for hx in (9, 17, 26):  # village with lit windows
        y = RIVER - 5
        for i, line in enumerate((" /^\\ ", "/___\\", "|[]o|")):
            for dx, ch in enumerate(line):
                if ch != " ":
                    put(g, hx + dx, y + i, ch, "#ffd678" if ch in "[]o" else "#e8d3c0")
                else:
                    g.pop((hx + dx, y + i), None)
    for x in range(COLS):  # bridge for the train
        put(g, x, RIVER - 1, "=", "#8e7a66")
        if x % 8 == 4:
            put(g, x, RIVER, "H", "#8e7a66")
    return g


def moving_frame(ridge, f):
    """Windmills (behind the front ridge), water and fireflies for one animation frame."""
    r = random.Random(21)
    mills, water = {}, {}
    for mx in (66, 84, 112):
        base = ridge[mx]
        for y in range(base - 7, base):
            put(mills, mx, y, "|", "#dfe9f5")
        hub = base - 8
        ch, vx, vy = [("|", 0, 1), ("/", 1, -1), ("-", 1, 0), ("\\", 1, 1)][(f + mx) % 4]
        for k in range(1, 6 if vy == 0 else 5):
            put(mills, mx + vx * k, hub + vy * k, ch, "#ffffff")
            put(mills, mx - vx * k, hub - vy * k, ch, "#ffffff")
        put(mills, mx, hub, "O", "#ffd678")
    for y in range(RIVER + 1, ROWS):
        for x in range(COLS):
            wave = (x - f * (1 if y % 2 else -1) + y * 7) % 12
            if wave < 7 and not (y == RIVER + 1 and x % 8 == 4):
                put(water, x, y, "~~~--.."[wave], ["#4ea6e8", "#3a86c4", "#2a5f92"][min(2, (y - RIVER) // 3)])
        for dx in range(-7, 8):  # moon on the water
            if (dx * 3 + f + y) % 4 == 0 and abs(dx) < 9 - (y - RIVER) // 2:
                put(water, 104 + dx, y, "=", "#f2de94")
    for i in range(22):
        x, y, phase = r.randrange(COLS), r.randrange(40, 47), r.randrange(FRAMES)
        if (f + phase) % FRAMES < 5:
            put(water, x, y, "*", "#ffe27a")
    return mills, water


def name():
    g = {}
    for row, word in enumerate(("PRABHU", "SIDDARTH")):
        for li, letter in enumerate(word):
            for dy, bits in enumerate(FONT[letter].split()):
                for dx, bit in enumerate(bits):
                    if bit == "#":
                        x, y = 4 + (li * 6 + dx) * 2 - li * 1, 3 + row * 8 + dy
                        put(g, x, y, "#", "#f2f8ff")
                        put(g, x + 1, y, "#", "#f2f8ff")
    return g


def path_keys(label, points):
    n = len(points)
    body = "".join(f"{100 * i / n:.2f}%{{transform:translate({x}px,{y}px)}}" for i, (x, y) in enumerate(points))
    return f"@keyframes {label}{{{body}}}"


def render(weeks):
    ridge = front_ridge(weeks)
    css = [f".f{{opacity:0;animation:t {FRAMES * STEP:.1f}s step-end infinite}}",
           f"@keyframes t{{0%{{opacity:1}}{100 / FRAMES:.3f}%,100%{{opacity:0}}}}",
           "@keyframes glow{0%,100%{opacity:.2}50%{opacity:.95}}",
           "@keyframes twinkle{0%,100%{opacity:1}50%{opacity:.1}}"]
    frames = [moving_frame(ridge, f) for f in range(FRAMES)]

    def stack(index):
        return "".join(f'<g class="f" style="animation-delay:{f * STEP - FRAMES * STEP:.1f}s">{draw(fr[index])}</g>'
                       for f, fr in enumerate(frames))

    def mover(label, dur, inner, delay=0, timing="step-end"):
        return f'<g style="animation:{label} {dur}s {timing} {delay}s infinite">{inner}</g>'

    # clouds, birds, shooting star, train, boat, walker
    css.append(path_keys("cloud", [(-150 + 6 * i, 0) for i in range(146)]))
    css.append(path_keys("birds", [(W - 6 * i, 250 + round(math.sin(i / 4) * 2) * 10) for i in range(130)]))
    css.append(path_keys("train", [(-200 + 6 * i, (RIVER - 3) * CH) for i in range(154)]))
    css.append(path_keys("boat", [(W - 6 * i, (RIVER + 3) * CH) for i in range(136)]))
    css.append(path_keys("walk", [(c * CW - 6, (ridge[c] - 3) * CH) for c in range(1, COLS - 2)]))
    css.append("@keyframes shoot{0%{transform:translate(430px,20px);opacity:1}9%{transform:translate(250px,150px);opacity:0}"
               "100%{transform:translate(250px,150px);opacity:0}}")

    cloud = ["      .--~~--.       ", "  .-~(        )~-.   ", " (___.__.___.__.__)  "]
    parts = [draw(sky())]
    for b in range(3):
        parts.append(f'<g style="animation:glow {5 + b * 2}s ease-in-out {-b * 2}s infinite">{draw(aurora(b))}</g>')
    r = random.Random(3)
    for i in range(18):  # bright twinkling stars
        parts.append(f'<text x="{r.randrange(W)}" y="{r.randrange(12, 240)}" fill="#fff" '
                     f'style="animation:twinkle {2 + i % 4}s {-i * .37:.2f}s infinite">*</text>')
    parts.append(mover("shoot", 8, '<text fill="#fff">.</text><text x="6" y="-4" fill="#cfe3ff">,-\'\'</text>', timing="linear"))
    parts.append(f'<g transform="translate(0,205)" opacity=".75">{mover("cloud", 60, sprite(cloud, "#7f93bd"))}</g>')
    parts.append(f'<g transform="translate(0,235)" opacity=".55">{mover("cloud", 85, sprite(cloud, "#a8b8dc"), -40)}</g>')
    parts.append(mover("birds", 26, sprite(["  v    v ", "v    v   "], "#dfe9f5")))
    parts.append(draw(far_ridges()))
    parts.append(stack(0))
    parts.append(draw(front(ridge)))
    hero = (sprite([" O ", "/|\\", "/ \\"], "#ffffff", bg=True)
            + '<text x="19" y="18" fill="#ffd678" style="animation:twinkle .9s infinite">@</text>')
    parts.append(mover("walk", 40, hero))
    train = ["    __   _____   _____   _____   ", " __|[]|_|[][][]|_|[][][]|_|[][][]| ", " (o)--(o) (o)-(o) (o)-(o) (o)-(o) "]
    parts.append(mover("train", 18, sprite(train, "#ffb27a")))
    parts.append(stack(1))
    parts.append(mover("boat", 34, sprite(["    |\\    ", "    |_\\   ", " \\______/ "], "#f4e3cd")))
    title = name()
    shade = "".join(f'<rect x="{x * CW - 3}" y="{y * CH - 2}" width="{CW + 6}" height="{CH + 4}" fill="#04070f"/>' for x, y in title)
    parts.append(shade + draw(title))

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H + 28}" width="{W}" height="{H + 28}" '
        f'font-family="ui-monospace,Menlo,Consolas,DejaVu Sans Mono,monospace" font-size="10" font-weight="bold">'
        f'<style>{"".join(css)}</style><clipPath id="c"><rect width="{W}" height="{H + 28}" rx="10"/></clipPath>'
        f'<g clip-path="url(#c)"><rect width="{W}" height="{H + 28}" fill="#04070f"/>{"".join(parts)}'
        f'<text x="{W / 2}" y="{H + 18}" text-anchor="middle" font-size="14" fill="#9dffc0">'
        f'AI backend engineer in the making · the green ridge is my last year of commits</text></g></svg>')


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "dist/ascii-ghats.svg"
    token = os.environ.get("GITHUB_TOKEN")
    weeks = fetch(os.environ.get("GH_USER", "PRABHUSIDDARTH"), token) if token else sample()
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(render(weeks))
