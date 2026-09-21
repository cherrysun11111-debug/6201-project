import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    subprocess.run([sys.executable, *args], cwd=PROJECT_ROOT, env=env, check=True)


def main() -> None:
    run(["-m", "ecrisk.data", "--rows", "420", "--seed", "6201"])
    run(["-m", "ecrisk.train"])
    run(["-m", "ecrisk.evaluate"])
    run(["-m", "ecrisk.batch"])
    run(["-m", "unittest", "discover", "-s", "tests"])
    print("\nPipeline complete. Reports are in the reports directory.")


if __name__ == "__main__":
    main()

