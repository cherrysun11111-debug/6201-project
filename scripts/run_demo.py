import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    print("Starting demo at http://127.0.0.1:8000")
    subprocess.run([sys.executable, "-m", "ecrisk.app"], cwd=PROJECT_ROOT, env=env, check=True)


if __name__ == "__main__":
    main()

