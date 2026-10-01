"""Check the wiki sources against the rules in CONTRIBUTING.md.

Run from the repository root:  python3 scripts/lint.py   (or: npm run lint)
Runs before rendering in CI; exits non-zero if any error is found.

  references.bib  canonical format (scripts/format_bib.py), duplicate keys/URLs,
                  misspelt or missing fields, scheme entries matching index.qmd
                  in year order, follow-up keys sorted and well-formed
  index.qmd       entry format, year order, disc percentages, links,
                  and a references.bib entry for every listed scheme
  schemes/**      filename, frontmatter, section order, citations that
                  exist, Overview cites the paper, no template leftovers,
                  page linked from index.qmd, Couveignes / Rostovtsev-Stolbunov
                  linked to their ePrints
  all files       no emoji (every file Git would commit)

Pages with `draft: true` are only checked for their filename. Pages in
LEGACY predate the template: their problems are reported as warnings
until they are rewritten (then remove them from the set).
"""
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

from format_bib import format_bib, parse

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = ["Overview", "Scheme Design", "Security Assumptions", "Progress"]
LISTS = {"Key Establishment": "key-establishment", "Digital Signature": "digital-signature"}
LEGACY = set()
CRS_EPRINTS = {"Couveignes": "eprint.iacr.org/2006/291", "Rostovtsev": "eprint.iacr.org/2006/145"}
EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]")

BIB_FIELDS = {
    "author", "title", "booktitle", "journal", "year", "pages", "publisher",
    "url", "volume", "number", "doi", "editor", "series", "note", "month",
}
BIB_REQUIRED = {
    "inproceedings": {"author", "title", "booktitle", "year", "url"},
    "article": {"author", "title", "journal", "year", "url"},
    "misc": {"author", "title", "year", "url"},
}

errors, warnings = [], []

def report(where, msg, warn=False):
    (warnings if warn else errors).append(f"{where}: {msg}")

def normalize(name):
    """Scheme name -> key/filename: 'POKÉ' -> 'poke', '$\\Pi$-SIDE' -> 'piside'."""
    name = name.replace("\\Pi", "pi")
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", name.lower())

def strip_code_and_comments(text):
    text = re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)

def citation_keys(text):
    keys = set()
    for group in re.findall(r"\[[^\[\]]*@[^\[\]]*\]", text):
        for key in re.findall(r"(?<![\w\\])@([\w][\w:.#$%&\-+?<>~/]*)", group):
            keys.add(key.rstrip(".,;:"))
    return keys

# --- references.bib ------------------------------------------------------

bib_text = (ROOT / "references.bib").read_text(encoding="utf-8")
if format_bib(bib_text) != bib_text:
    report("references.bib", "not in canonical format; run `npm run format`")

bib = {}          # key -> {field: value}
scheme_keys = []  # entries before the "% Follow-up work" marker, in file order
followup_keys = []
urls = {}
in_followup = False
for item in parse(bib_text):
    if item[0] == "text":
        in_followup = in_followup or bool(re.search(r"^% Follow-up work", item[1], re.M))
        continue
    _, etype, key, field_list = item
    fields = dict(field_list)
    where = f"references.bib [{key}]"
    if key in bib:
        report(where, "duplicate key")
    bib[key] = fields
    (followup_keys if in_followup else scheme_keys).append(key)
    for name in fields:
        if name not in BIB_FIELDS:
            report(where, f"unknown field '{name}' (typo?)")
    missing = BIB_REQUIRED.get(etype, {"author", "title", "year"}) - set(fields)
    if missing:
        report(where, f"missing field(s): {', '.join(sorted(missing))}")
    if not re.fullmatch(r"\d{4}", fields.get("year", "")):
        report(where, "year must be four digits")
    if "pages" in fields and not re.fullmatch(r"\d+(--\d+)?", fields["pages"]):
        report(where, "pages must look like 12--34")
    if re.search(r"\\['\"`^~=.cuvH]", " ".join(fields.values())):
        report(where, "write accented letters as Unicode (é), not LaTeX (\\'e)")
    u = fields.get("url", "").rstrip("/")
    if u in urls:
        report(where, f"same url as [{urls[u]}]: duplicate entry?")
    urls[u] = key

for prev, key in zip(scheme_keys, scheme_keys[1:]):
    if int(bib[key].get("year", 0) or 0) < int(bib[prev].get("year", 0) or 0):
        report(f"references.bib [{key}]", f"scheme entries must be in year order (comes after [{prev}])")
for key in followup_keys:
    if not re.fullmatch(r"[a-z]+\d{4}[a-z]+", key):
        report(f"references.bib [{key}]", "follow-up key must be <surname><year><titleword>, e.g. castryck2023efficient")
if followup_keys != sorted(followup_keys):
    report("references.bib", "follow-up entries must be sorted by key")

# Scheme names map to keys directly, or to one part of a joint key (msidh-mdsidh).
bib_names = {part: key for key in bib for part in key.split("-")}

# --- index.qmd -----------------------------------------------------------

index_text = (ROOT / "index.qmd").read_text(encoding="utf-8")
current_list = None
last_year = {}
index_names = set()
for lineno, line in enumerate(index_text.splitlines(), 1):
    where = f"index.qmd:{lineno}"
    heading = re.match(r"^###\s+(.*)$", line)
    if heading:
        current_list = LISTS.get(heading.group(1).strip())
        continue
    entry = re.match(r"^- \[\]\{([^}]*)\}\s+(.*?)\s*$", line)
    if not entry:
        continue
    discs, rest = entry.groups()

    pct = dict(re.findall(r"([a-z])=(\d+)", discs))
    if not pct or set(pct) - {"r", "g", "b"} or sum(map(int, pct.values())) != 100:
        report(where, f"disc '{{{discs}}}' must use r/g/b percentages summing to 100")

    year = re.search(r"\((\d{4})(?:--(\d{4}))?\)$", rest)
    if not year:
        report(where, "must end with (YYYY) or (YYYY--YYYY), using two hyphens")
        continue
    start = int(year.group(1))
    if year.group(2) and int(year.group(2)) < start:
        report(where, "range ends before it starts")
    if start < last_year.get(current_list, 0):
        report(where, f"out of chronological order ({start} after {last_year[current_list]})")
    last_year[current_list] = max(start, last_year.get(current_list, 0))

    name = rest[: year.start()].strip()
    link = re.match(r"^\[(.*)\]\(([^)]*)\)$", name)
    if link:
        name, target = link.groups()
        m = re.match(r"^/schemes/([a-z-]+)/[a-z0-9]+\.qmd$", target)
        if not m:
            report(where, f"link '{target}' must look like /schemes/<section>/<name>.qmd")
        elif not (ROOT / target.lstrip("/")).exists():
            report(where, f"link target '{target}' does not exist")
        elif current_list and m.group(1) != current_list:
            report(where, f"'{target}' is listed under the wrong section")
    index_names.add(normalize(name))
    if normalize(name) not in bib_names:
        report(where, f"no references.bib entry for '{name}' (expected key '{normalize(name)}')")
    elif bib[bib_names[normalize(name)]].get("year") != str(start):
        report(where, f"year {start} differs from references.bib year "
                      f"{bib[bib_names[normalize(name)]].get('year')}")

for key in scheme_keys:
    for part in key.split("-"):
        if part not in index_names:
            report(f"references.bib [{key}]", f"'{part}' is not a scheme in index.qmd; move follow-up papers below the '% Follow-up work' line")

# --- scheme pages --------------------------------------------------------

for path in sorted((ROOT / "schemes").rglob("*.qmd")):
    rel = path.relative_to(ROOT).as_posix()
    legacy = rel in LEGACY
    text = path.read_text(encoding="utf-8")

    if not re.fullmatch(r"[a-z0-9]+\.qmd", path.name):
        report(rel, "filename must be lowercase letters and digits only")

    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    meta = dict(re.findall(r"^(\w[\w-]*):\s*(.*?)\s*$", fm.group(1), re.M)) if fm else {}
    meta = {k: v.strip("\"'") for k, v in meta.items()}
    if meta.get("draft") == "true":
        continue
    for field in ("title", "subtitle", "date"):
        if not meta.get(field):
            report(rel, f"frontmatter is missing '{field}'", legacy)
    if meta.get("date") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta["date"]):
        report(rel, "date must be YYYY-MM-DD", legacy)
    if meta.get("title") and normalize(meta["title"]) != path.stem:
        report(rel, f"filename should be '{normalize(meta['title'])}.qmd' to match the title", legacy)

    raw_body = text[fm.end():] if fm else text
    if re.search(r"SHORTNAME|YYYY-MM-DD|<!--", raw_body):
        report(rel, "template placeholders or <!-- comments --> left in the page", legacy)
    body = strip_code_and_comments(raw_body)

    if re.search(r"^# ", body, re.M):
        report(rel, "don't use '#' headings; the title comes from the frontmatter", legacy)
    h2 = [re.sub(r"\s*\{.*\}\s*$", "", h).strip() for h in re.findall(r"^## (.*)$", body, re.M)]
    if "References" in h2:
        report(rel, "remove the 'References' section; it is added automatically", legacy)
    if h2 != SECTIONS:
        report(rel, f"sections must be {' / '.join(SECTIONS)}, found {' / '.join(h2) or 'none'}", legacy)

    for key in sorted(citation_keys(body) - set(bib)):
        report(rel, f"cites [@{key}], which is not in references.bib")
    overview = re.search(r"^## Overview.*?$(.*?)(?=^## |\Z)", body, re.S | re.M)
    if overview and not citation_keys(overview.group(1)):
        report(rel, "Overview must cite the paper that introduces the scheme", legacy)

    for block in re.findall(r"^```\{(\.tikz[^}]*)\}", raw_body, re.M):
        if "fig-alt=" not in block:
            report(rel, "TikZ diagram has no fig-alt text", warn=True)

    if f"](/{rel})" not in index_text:
        report(rel, "not linked from index.qmd", legacy)

    for name, eprint in CRS_EPRINTS.items():
        if name in body and eprint not in body:
            report(rel, f"mentions {name} without linking https://{eprint}", warn=True)

# --- emoji, in every file Git would commit ---------------------------------

def repo_files():
    try:
        out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
        return [ROOT / f for f in out.splitlines()]
    except (OSError, subprocess.CalledProcessError):  # no git: walk, skipping generated dirs
        skip = {".git", "node_modules", "docs", "_site", ".quarto", ".contributors",
                ".tikz-cache", "papers", "__pycache__"}
        return [p for p in ROOT.rglob("*") if p.is_file() and not skip & set(p.relative_to(ROOT).parts)]

for path in repo_files():
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        continue  # binary or unreadable
    for lineno, line in enumerate(lines, 1):
        hit = EMOJI.search(line)
        if hit:
            report(f"{path.relative_to(ROOT).as_posix()}:{lineno}", f"emoji U+{ord(hit.group()):04X} is not allowed")

# --- summary -------------------------------------------------------------

for w in warnings:
    print(f"warning: {w}")
for e in errors:
    print(f"error:   {e}")
print(f"lint: {len(errors)} error(s), {len(warnings)} warning(s).")
sys.exit(1 if errors else 0)
