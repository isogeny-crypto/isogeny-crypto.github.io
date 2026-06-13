import os
import json
import urllib.request
import subprocess
from pathlib import Path

REPO = "isogeny-crypto/isogeny-crypto.github.io"

QUARTO_FULL_RENDER = os.environ.get("QUARTO_PROJECT_RENDER_ALL") == "1"
CALLED_DIRECTLY    = os.environ.get("QUARTO_PROJECT_OUTPUT_DIR") is None

if not (QUARTO_FULL_RENDER or CALLED_DIRECTLY):
    print("fetch_contributors.py: skipping in preview mode.")
    raise SystemExit(0)

if CALLED_DIRECTLY:
    print("fetch_contributors.py: running standalone.")

os.makedirs(".contributors", exist_ok=True)

github_token = os.environ.get("GITHUB_TOKEN")
headers = {"User-Agent": "Mozilla/5.0"}
if github_token:
    headers["Authorization"] = f"token {github_token}"

for file_path in Path("protocols").rglob("*.qmd"):
    # 1. Sync mtime to last git commit
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", str(file_path)],
            capture_output=True, text=True
        )
        if result.stdout.strip():
            ts = float(result.stdout.strip())
            os.utime(file_path, (ts, ts))
    except Exception:
        pass

    # 2. Fetch contributors
    snippet_path = Path(".contributors") / f"{file_path.stem}.md"
    url = f"https://api.github.com/repos/{REPO}/commits?path={file_path}"

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

        snippet_path.write_text(markdown)

    except Exception as e:
        print(f"Warning: could not fetch contributors for {file_path}: {e}")
        if not snippet_path.exists():
            snippet_path.write_text("\n\n**Contributors:** Pending GitHub sync...\n")

    # 3. Warn if the qmd file is missing its include line
    content = file_path.read_text()
    expected = f"{{{{< include ../../.contributors/{file_path.stem}.md >}}}}"
    if expected not in content:
        print(f"WARNING: {file_path} is missing its contributor include line:")
        print(f"  Add this at the bottom: {expected}")