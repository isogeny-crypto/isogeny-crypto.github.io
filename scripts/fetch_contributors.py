import os
import json
import urllib.request
import subprocess
from pathlib import Path

REPO = "isogeny-crypto/isogeny-crypto.github.io"
os.chdir(Path(__file__).resolve().parent.parent)  # paths below are relative to the repo root
CONTRIBUTORS_DIR = Path(".contributors")

QUARTO_FULL_RENDER = os.environ.get("QUARTO_PROJECT_RENDER_ALL") == "1"
CALLED_DIRECTLY    = os.environ.get("QUARTO_PROJECT_OUTPUT_DIR") is None

if not (QUARTO_FULL_RENDER or CALLED_DIRECTLY):
    print("fetch_contributors.py: skipping in preview mode.")
    raise SystemExit(0)

if CALLED_DIRECTLY:
    print("fetch_contributors.py: running standalone.")

def snippet_path_for(file_path):
    """Map schemes/key-exchange/sidh.qmd -> .contributors/schemes/key-exchange/sidh.md.

    Keyed by source path (not title) so that pages whose titles contain one
    another, e.g. FESTA / QFESTA, can never pick up each other's snippet.
    contributors.lua computes the same path from the page being rendered.
    """
    return CONTRIBUTORS_DIR / file_path.with_suffix(".md")

def write_snippet(path, markdown):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")

PENDING = "\n\n**Contributors:** Pending GitHub sync...\n"

scheme_files = sorted(Path("schemes").rglob("*.qmd"))

# Create placeholder snippets for any .qmd files that don't have one yet,
# so every page renders even if the API fetch below fails.
for file_path in scheme_files:
    snippet_path = snippet_path_for(file_path)
    if not snippet_path.exists():
        write_snippet(snippet_path, PENDING)

github_token = os.environ.get("GITHUB_TOKEN")
headers = {"User-Agent": "isogeny-crypto-wiki-build"}
if github_token:
    headers["Authorization"] = f"token {github_token}"

for file_path in scheme_files:
    # 1. Sync mtime to last git commit (drives the page's "Modified" date)
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(file_path)],
            capture_output=True, text=True
        )
        if result.stdout.strip():
            ts = float(result.stdout.strip())
            os.utime(file_path, (ts, ts))
    except Exception:
        pass

    # 2. Fetch contributors
    snippet_path = snippet_path_for(file_path)
    url = (f"https://api.github.com/repos/{REPO}/commits"
           f"?path={file_path.as_posix()}&per_page=100")

    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        commits = json.loads(response.read())

        handles = set()
        for commit in commits:
            if isinstance(commit, dict) and commit.get("author"):
                login = commit["author"].get("login")
                if login:
                    handles.add(login)

        if handles:
            links = [f"[\\@{h}](https://github.com/{h})" for h in sorted(handles)]
            markdown = f"\n\n**Contributors:** {', '.join(links)}\n"
        else:
            markdown = "\n\n**Contributors:** No GitHub history found yet.\n"

        write_snippet(snippet_path, markdown)

    except Exception as e:
        print(f"Warning: could not fetch contributors for {file_path}: {e}")
