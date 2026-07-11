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

def get_qmd_title(file_path):
    """Extract the title field from a .qmd YAML frontmatter."""
    with open(file_path, "r") as f:
        lines = f.readlines()
    in_frontmatter = False
    for line in lines:
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter and line.startswith("title:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return file_path.stem  # fallback to filename stem if no title found

def title_to_key(title):
    """Lowercase the title for use as a snippet filename key."""
    return title.strip().lower()

os.makedirs(".contributors", exist_ok=True)

# Create placeholder snippets for any .qmd files that don't have one yet,
# so Quarto never fails on a missing include before the API fetch runs.
for file_path in Path("schemes").rglob("*.qmd"):
    title = get_qmd_title(file_path)
    key = title_to_key(title)
    snippet_path = Path(".contributors") / f"{key}.md"
    if not snippet_path.exists():
        snippet_path.write_text("\n\n**Contributors:** Pending GitHub sync...\n")

github_token = os.environ.get("GITHUB_TOKEN")
headers = {"User-Agent": "Mozilla/5.0"}
if github_token:
    headers["Authorization"] = f"token {github_token}"

for file_path in Path("schemes").rglob("*.qmd"):
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
    title = get_qmd_title(file_path)
    key = title_to_key(title)
    snippet_path = Path(".contributors") / f"{key}.md"
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