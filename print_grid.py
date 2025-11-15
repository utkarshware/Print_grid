
#!/usr/bin/env python3

"""Simple solution for the decoding exercise.

One public function: `print_grid_from_doc_url(url)`
It fetches the Google Doc (text export), parses coordinate/character
entries and prints the resulting grid. The implementation is intentionally
small and easy to follow.
"""

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
    # include a simple User-Agent to avoid being blocked or served different content
    from urllib.request import Request, urlopen

    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible)"})
    with urlopen(req, timeout=timeout) as fh:
        return fh.read().decode("utf-8", errors="replace")


def fetch_doc_text(url):
    """Try the docs export URL first; fall back to the original URL."""
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
    """Return dict mapping (x,y) -> char.

    Supports three simple forms seen in the exercises:
    - inline triplets on one line: `x y char`, `x char y`, or `char x y`
    - lines with a U+HEX code and two ints: `U+2588 1 2`
    - vertical triplets where `x`, then `char`, then `y` appear on three lines
    """
    points = {}
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # U+HEX followed by x y (allow negative coords)
    ru = re.compile(r"U\+([0-9A-Fa-f]{4,6})\s+(-?\d+)\s+(-?\d+)")

    # first pass: inline triplets or U+ entries
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

        # scan windows of 3 tokens
        found = False
        for i in range(len(toks) - 2):
            a, b, c = toks[i], toks[i + 1], toks[i + 2]
            # x y char
            if is_int(a) and is_int(b) and not is_int(c):
                token = c.strip("'\"")
                if token:
                    points[(int(a), int(b))] = token
                    found = True
                    break
            # x char y
            if is_int(a) and not is_int(b) and is_int(c):
                token = b.strip("'\"")
                if token:
                    points[(int(a), int(c))] = token
                    found = True
                    break
            # char x y
            if not is_int(a) and is_int(b) and is_int(c):
                token = a.strip("'\"")
                if token:
                    points[(int(b), int(c))] = token
                    found = True
                    break
        if not found:
            malformed_inline += 1

    # second pass: vertical triplets (x, char, y) on consecutive lines.
    # Use raw lines (keep blanks) and test their stripped forms so we don't
    # change the meaning of 'consecutive' if the doc intentionally includes blanks.
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
    """Fetch the document at `url`, parse coordinates, and print the grid.

    Note: y increases downwards (row 0 is the top row)."""
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
