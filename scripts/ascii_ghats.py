"""Animated ASCII night over the Western Ghats. The front ridge is the last year of contributions."""
import json, math, os, random, sys, urllib.request

COLS, ROWS, CW, CH, FRAMES = 90, 36, 8, 13, 12
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
    return [max(0, int(18 + 16 * math.sin(i / 5) + r.randint(-12, 22))) for i in range(53)]


def front_ridge(weeks):
    """Top row of the front ridge for every column: busier weeks stand taller."""
    top = max(weeks + [1])
    raw = []
    for c in range(COLS):
        p = c * (len(weeks) - 1) / (COLS - 1)
        i = int(p)
        j = min(i + 1, len(weeks) - 1)
        raw.append(weeks[i] + (weeks[j] - weeks[i]) * (p - i))
    smooth = [sum(raw[max(0, c - 2):c + 3]) / len(raw[max(0, c - 2):c + 3]) for c in range(COLS)]
    return [round(28 - 9 * math.sqrt(v / top)) for v in smooth]


def scene(weeks, f):
    r = random.Random(4)
    g = {}

    def put(x, y, ch, col):
        if 0 <= x < COLS and 0 <= y < ROWS:
            g[x, y] = (ch, col)

    for i in range(150):  # stars
        x, y, phase = r.randrange(COLS), r.randrange(19), r.randrange(FRAMES)
        lit = (f + phase) % FRAMES < 3 and i % 3 == 0
        put(x, y, "*" if lit else ".", "#ffffff" if lit else "#4d6385")
    for dy in range(-3, 4):  # moon
        for dx in range(-6, 7):
            d = (dx / 6) ** 2 + (dy / 3.2) ** 2
            if d <= 1:
                put(78 + dx, 5 + dy, "@" if d < .55 else "o", "#fff1bd" if d < .55 else "#d8c47e")
    for x in range(COLS):  # two far ridges
        a = int(19 + 3 * math.sin(x / 9) + 1.6 * math.sin(x / 3.7))
        b = int(23 + 2.4 * math.sin(x / 7 + 2) + math.sin(x / 2.9))
        for y in range(a, ROWS):
            put(x, y, "^" if y == a else ":", "#6f8fc4" if y == a else "#2b3f66")
        for y in range(b, ROWS):
            put(x, y, "^" if y == b else "%", "#4fa39a" if y == b else "#1d4a4c")
    ridge = front_ridge(weeks)
    for x in range(COLS):
        for y in range(ridge[x], 31):
            if y == ridge[x]:
                put(x, y, "A", "#8dffb0")
            else:
                put(x, y, "#&%#"[(x * 7 + y * 3) % 4], ["#2f9e62", "#23794c", "#1a5a3a"][min(2, (y - ridge[x]) // 3)])
    for mx in (55, 68, 84):  # windmills of the Palghat gap
        base = ridge[mx]
        for y in range(base - 4, base):
            put(mx, y, "|", "#dfe9f5")
        hub, step = base - 5, (f + mx) % 4
        ch, vx, vy = [("|", 0, 1), ("/", 1, -1), ("-", 1, 0), ("\\", 1, 1)][step]
        for k in (1, 2, 3):
            put(mx + vx * k, hub + vy * k, ch, "#ffffff")
            put(mx - vx * k, hub - vy * k, ch, "#ffffff")
        put(mx, hub, "o", "#ffd678")
    for y in range(31, ROWS):  # river
        for x in range(COLS):
            wave = (x - f * (1 if y % 2 else -1) + y * 5) % 12
            put(x, y, "~" if wave < 4 else "-" if wave < 6 else " ", "#3f8fd0" if wave < 4 else "#275a86")
        for dx in range(-4, 5):
            if (dx + f + y) % 3 == 0:
                put(78 + dx, y, "=", "#e9d58c")
    for i in range(14):  # fireflies
        x, y, phase = r.randrange(COLS), r.randrange(27, 31), r.randrange(FRAMES)
        if (f + phase) % FRAMES < 5:
            put(x, y, "*", "#ffe27a")
    for key in [k for k in g if k[0] < 53 and 1 <= k[1] <= 13 and g[k][0] in ".*"]:
        del g[key]  # keep the sky behind the name clear
    for row, word in enumerate(("PRABHU", "SIDDARTH")):
        for li, letter in enumerate(word):
            for dy, bits in enumerate(FONT[letter].split()):
                for dx, bit in enumerate(bits):
                    if bit == "#":
                        put(3 + li * 6 + dx, 2 + row * 6 + dy, "#", "#eef6ff")
    return g


def draw(cells):
    """One <text> per same-colour run, with a fixed width so every font lines up."""
    out = []
    for y in range(ROWS):
        x = 0
        while x < COLS:
            if (x, y) not in cells or cells[x, y][0] == " ":
                x += 1
                continue
            col, run, start = cells[x, y][1], "", x
            while (x, y) in cells and cells[x, y][1] == col and cells[x, y][0] != " ":
                run += cells[x, y][0]
                x += 1
            run = run.replace("&", "&amp;")
            n = x - start
            out.append(f'<text x="{start * CW}" y="{y * CH + 11}" textLength="{n * CW}" fill="{col}">{run}</text>')
    return "".join(out)


def render(weeks):
    frames = [scene(weeks, f) for f in range(FRAMES)]
    keys = set().union(*frames)
    still = {k: frames[0][k] for k in keys if all(fr.get(k) == frames[0].get(k) for fr in frames)}
    moving = "".join(
        f'<g class="f" style="animation-delay:{f * .2 - FRAMES * .2:.1f}s">'
        + draw({k: v for k, v in fr.items() if k not in still}) + "</g>"
        for f, fr in enumerate(frames))
    w, h = COLS * CW, ROWS * CH
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h + 30}" width="{w}" height="{h + 30}" '
        f'font-family="ui-monospace,Menlo,Consolas,DejaVu Sans Mono,monospace" font-size="13" font-weight="bold">'
        f'<style>.f{{opacity:0;animation:t {FRAMES * .2:.1f}s step-end infinite}}'
        f'@keyframes t{{0%{{opacity:1}}{100 / FRAMES:.3f}%,100%{{opacity:0}}}}</style>'
        f'<rect width="{w}" height="{h + 30}" rx="10" fill="#050914"/>{draw(still)}{moving}'
        f'<text x="{w / 2}" y="{h + 20}" text-anchor="middle" font-size="15" fill="#8dffb0">'
        f'AI backend engineer in the making · the green ridge is my last year of commits</text></svg>')


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "dist/ascii-ghats.svg"
    token = os.environ.get("GITHUB_TOKEN")
    weeks = fetch(os.environ.get("GH_USER", "PRABHUSIDDARTH"), token) if token else sample()
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(render(weeks))
