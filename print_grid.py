

#!/usr/bin/env python3

"""Fetch a Google Doc of coordinate/character data and print the grid."""

import re
import sys
from urllib.request import urlopen


def extract_doc_id(url):
    m = re.search(r"/document/d/([A-Za-z0-9_-]+)", url)
    if m:
        return m.group(1)
    m = re.search(r"[?&]id=([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else None


def fetch_url_text(url, timeout=10):
    from urllib.request import Request, urlopen

    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible)"})
    with urlopen(req, timeout=timeout) as fh:
        return fh.read().decode("utf-8", errors="replace")


def fetch_doc_text(url):
    """Return text for `url`. Prefer Google Docs txt export when possible."""
    doc_id = extract_doc_id(url)
    if doc_id:
        export = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
        try:
            return fetch_url_text(export)
        except Exception:
            pass
    return fetch_url_text(url)


def is_int(s):
    try:
        int(s)
        return True
    except Exception:
        return False


def parse_text_to_points(text):
    """Return mapping (x,y) -> character.

    Handles inline triplets (e.g. `x y char`), `U+HEX x y` tokens, and
    vertical triplets where three consecutive lines are `x`, `char`, `y`.
    """
    points = {}
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    ru = re.compile(r"U\+([0-9A-Fa-f]{4,6})\s+(-?\d+)\s+(-?\d+)")

    malformed_inline = 0
    for line in lines:
        m = ru.search(line)
        if m:
            ch = chr(int(m.group(1), 16))
            x = int(m.group(2))
            y = int(m.group(3))
            points[(x, y)] = ch
            continue

        toks = re.split(r"[\s,]+", line)
        if len(toks) < 3:
            continue

        found = False
        for i in range(len(toks) - 2):
            a, b, c = toks[i], toks[i + 1], toks[i + 2]
            if is_int(a) and is_int(b) and not is_int(c):
                token = c.strip("'\"")
                if token:
                    points[(int(a), int(b))] = token
                    found = True
                    break
            if is_int(a) and not is_int(b) and is_int(c):
                token = b.strip("'\"")
                if token:
                    points[(int(a), int(c))] = token
                    found = True
                    break
            if not is_int(a) and is_int(b) and is_int(c):
                token = a.strip("'\"")
                if token:
                    points[(int(b), int(c))] = token
                    found = True
                    break
        if not found:
            malformed_inline += 1

    raw_lines = text.splitlines()
    for i in range(len(raw_lines) - 2):
        a_raw, b_raw, c_raw = raw_lines[i], raw_lines[i + 1], raw_lines[i + 2]
        a, b, c = a_raw.strip(), b_raw.strip(), c_raw.strip()
        if is_int(a) and (not is_int(b)) and is_int(c) and b:
            points[(int(a), int(c))] = b

    if malformed_inline > 0:
        print(f"Warning: {malformed_inline} inline lines were ignored (malformed)", file=sys.stderr)

    return points


def print_grid_from_doc_url(url):
    """Fetch `url`, parse points, and print the assembled grid.

    Y increases downward (row 0 is the top).
    """
    text = fetch_doc_text(url)
    points = parse_text_to_points(text)
    if not points:
        print("No coordinate data found")
        return

    xs = [x for (x, y) in points.keys()]
    ys = [y for (x, y) in points.keys()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    width = max_x - min_x + 1
    height = max_y - min_y + 1

    grid = [[" " for _ in range(width)] for _ in range(height)]
    for (x, y), ch in points.items():
        grid[y - min_y][x - min_x] = ch

    for row in grid:
        print("".join(row))


def _cli(argv):
    if len(argv) < 2:
        print("Usage: python print_grid.py <google-doc-url>")
        return 1
    print_grid_from_doc_url(argv[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv))
