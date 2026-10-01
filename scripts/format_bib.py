"""Rewrite references.bib in the canonical layout.

  python3 scripts/format_bib.py           # rewrite in place (npm run format)
  python3 scripts/format_bib.py --check   # exit 1 if not formatted (used by lint.py)

Canonical layout: lowercase entry types and field names, two-space indent,
`name = {value}`, fields in FIELD_ORDER, no trailing comma, page ranges with
`--`, whitespace inside values collapsed, one blank line between entries.
Entry order and `%` comment lines are preserved.
"""
import re
import sys
from pathlib import Path

BIB = Path(__file__).resolve().parent.parent / "references.bib"
FIELD_ORDER = ["author", "title", "booktitle", "journal", "volume", "number",
               "pages", "year", "publisher", "url"]

def parse(text):
    """Yield ("text", str) chunks and ("entry", type, key, [(name, value)]) entries."""
    pos = 0
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        if m.start() < pos:
            continue
        yield ("text", text[pos:m.start()])
        i, fields = m.end(), []
        while True:
            f = re.compile(r"\s*(\w+)\s*=\s*").match(text, i)
            if not f:
                break
            name, i = f.group(1), f.end()
            if text[i] in "{\"":
                # {...} ends at the matching brace; "..." at the first quote outside braces
                quoted, depth, j = text[i] == "\"", 0, i + 1
                if not quoted:
                    depth = 1
                while True:
                    c = text[j]
                    if c == "{":
                        depth += 1
                    elif c == "}":
                        depth -= 1
                    if (depth == 0 and not quoted and c == "}") or (quoted and c == "\"" and depth == 0):
                        break
                    j += 1
                value, i = text[i + 1:j], j + 1
            else:
                v = re.compile(r"[^,}\s]+").match(text, i)
                value, i = v.group(0), v.end()
            fields.append((name.lower(), value))
            c = re.compile(r"\s*,?").match(text, i)
            i = c.end()
        end = re.compile(r"\s*\}").match(text, i)
        if not end:
            raise SystemExit(f"format_bib: can't parse entry '{m.group(2)}'")
        pos = end.end()
        yield ("entry", m.group(1).lower(), m.group(2), fields)
    yield ("text", text[pos:])

def format_bib(text):
    blocks = []
    for item in parse(text):
        if item[0] == "text":
            chunk = "\n".join(l.rstrip() for l in item[1].strip().splitlines())
            if chunk:
                blocks.append(chunk)
            continue
        _, etype, key, fields = item
        rank = {n: i for i, n in enumerate(FIELD_ORDER)}
        fields = sorted(fields, key=lambda f: (rank.get(f[0], len(rank)), f[0]))
        lines = []
        for name, value in fields:
            value = re.sub(r"\s+", " ", value).strip()
            if name == "pages":
                value = re.sub(r"^(\d+)\s*-+\s*(\d+)$", r"\1--\2", value)
            lines.append(f"  {name} = {{{value}}}")
        blocks.append(f"@{etype}{{{key},\n" + ",\n".join(lines) + "\n}")
    return "\n\n".join(blocks) + "\n"

if __name__ == "__main__":
    original = BIB.read_text(encoding="utf-8")
    formatted = format_bib(original)
    if "--check" in sys.argv:
        sys.exit(0 if formatted == original else 1)
    BIB.write_text(formatted, encoding="utf-8")
    print("format_bib: references.bib " + ("unchanged." if formatted == original else "reformatted."))
