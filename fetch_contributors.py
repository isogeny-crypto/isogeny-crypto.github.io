import os
import json
import urllib.request
import subprocess
from pathlib import Path

# Set to your specific repository
REPO = "isogeny-crypto/isogeny-crypto.github.io"

os.makedirs(".contributors", exist_ok=True)
qmd_files = Path("protocols").rglob("*.qmd")

for file_path in qmd_files:
    # --- 1. SYNC TIMESTAMPS WITH GIT COMMIT HISTORY ---
    try:
        # Ask local git for the exact UNIX timestamp of the last commit for this file
        git_cmd = ['git', 'log', '-1', '--format=%ct', str(file_path)]
        result = subprocess.run(git_cmd, capture_output=True, text=True)
        
        if result.stdout.strip():
            commit_timestamp = float(result.stdout.strip())
            # Force the file's OS modification time to match the Git commit
            os.utime(file_path, (commit_timestamp, commit_timestamp))
    except Exception as e:
        # If it's a brand new uncommitted file, fail silently and use today's date
        pass 
    # --------------------------------------------------

    # --- 2. FETCH CONTRIBUTORS FROM GITHUB API ---
    snippet_path = Path(".contributors") / f"{file_path.stem}.md"
    url = f"https://api.github.com/repos/{REPO}/commits?path={file_path}"
    
    try:
        # Setup headers
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # Check for GitHub Token to bypass the 60 requests/hr limit
        github_token = os.environ.get("GITHUB_TOKEN")
        if github_token:
            headers['Authorization'] = f"token {github_token}"

        req = urllib.request.Request(url, headers=headers)
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