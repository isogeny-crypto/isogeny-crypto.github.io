import os
import json
import urllib.request
from pathlib import Path

# Set to your specific repository
REPO = "isogeny-crypto/isogeny-crypto.github.io"

os.makedirs(".contributors", exist_ok=True)
qmd_files = Path("protocols").rglob("*.qmd")

for file_path in qmd_files:
    snippet_path = Path(".contributors") / f"{file_path.stem}.md"
    url = f"https://api.github.com/repos/{REPO}/commits?path={file_path}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        commits = json.loads(response.read())
        
        handles = set()
        for commit in commits:
            if isinstance(commit, dict) and commit.get('author') and commit['author'].get('login'):
                handles.add(commit['author']['login'])
        
        if handles:
            links = [f"[\\@{h}](https://github.com/{h})" for h in handles]
            markdown = f"\n\n**Contributors:** {', '.join(links)}\n"
        else:
            markdown = "\n\n**Contributors:** No GitHub history found yet.\n"
            
        # Save the successful result
        with open(snippet_path, "w") as f:
            f.write(markdown)
            
    except Exception as e:
        print(f"Warning: Could not fetch GitHub API for {file_path} - {e}")
        # CRITICAL FALLBACK: Create a placeholder file so Quarto doesn't crash
        with open(snippet_path, "w") as f:
            f.write("\n\n**Contributors:** Pending GitHub sync...\n")