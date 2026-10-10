import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
STORE = "https://www.boat-lifestyle.com"


def load_env():
    """Read KEY=VALUE lines from .env so scheduled runs can see the token."""
    f = ROOT / ".env"
    if not f.exists():
        return
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"'))


load_env()
os.chdir(ROOT)

crawl = subprocess.run(
    [sys.executable, "-m", "scrapy", "crawl", "shopify", "-a", f"store={STORE}"])
if crawl.returncode != 0:
    print("Crawl failed, skipping alerts.")
    sys.exit(1)

subprocess.run([sys.executable, "alert.py"], check=True)
print("Done.")