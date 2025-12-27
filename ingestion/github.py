import subprocess
import tempfile
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def clone_repo(github_url):
    url = github_url.strip().rstrip("/")
    if not url.endswith(".git"):
        url = url + ".git"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", url, tmpdir],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to clone repo: {e.stderr}")
        
        yield Path(tmpdir)