"""Check that this machine is ready to run TripRescue.

Usage: python scripts/setup.py

Checks Python, the seed data, Docker, Claude Code and the .env file.
Never prints token values. Exits 0 only when every check passes.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_ENV = [
    "SLACK_WORKSPACE_ID",
    "SLACK_APP_TOKEN",
    "SLACK_BOT_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_BOT_USERNAME",
]
ENV_PREFIXES = {"SLACK_WORKSPACE_ID": "T", "SLACK_APP_TOKEN": "xapp-", "SLACK_BOT_TOKEN": "xoxb-"}


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return subprocess.CompletedProcess(cmd, 1, "", str(exc))


def check_python():
    ok = sys.version_info >= (3, 10)
    return ok, f"Python {sys.version.split()[0]}" + ("" if ok else " (need 3.10+)")


def check_seed():
    files = sorted((ROOT / "seed").glob("*.json"))
    if not files:
        return False, "no seed/*.json files found"
    for path in files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return False, f"{path.name} is not valid JSON: {exc}"
    return True, f"{len(files)} seed files parse"


def check_docker():
    docker = shutil.which("docker")
    if not docker:
        return False, "docker not found; install Docker Desktop"
    result = run([docker, "info", "--format", "{{.ServerVersion}}"])
    if result.returncode != 0 or not result.stdout.strip():
        return False, "Docker is installed but the engine is not running; start Docker Desktop"
    return True, f"Docker engine {result.stdout.strip()}"


def check_claude():
    claude = shutil.which("claude")
    if not claude:
        return False, "claude not found; install Claude Code"
    result = run([claude, "auth", "status"])
    try:
        logged_in = json.loads(result.stdout).get("loggedIn", False)
    except json.JSONDecodeError:
        logged_in = False
    if not logged_in:
        return False, "Claude Code is installed but not signed in; run: claude auth login"
    return True, "Claude Code signed in"


def read_env(path):
    values = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.split("#", 1)[0].strip()
    return values


def check_env():
    env_path = ROOT / ".env"
    if not env_path.exists():
        shutil.copyfile(ROOT / ".env.example", env_path)
        return False, "created .env from .env.example; fill in the values"
    values = read_env(env_path)
    missing = [key for key in REQUIRED_ENV if not values.get(key)]
    if missing:
        return False, "empty in .env: " + ", ".join(missing)
    wrong = [key for key, prefix in ENV_PREFIXES.items() if not values[key].startswith(prefix)]
    if wrong:
        return False, "unexpected format in .env: " + ", ".join(wrong)
    return True, "all required .env keys are set"


def main():
    checks = [
        ("Python", check_python),
        ("Seed data", check_seed),
        ("Docker", check_docker),
        ("Claude Code", check_claude),
        (".env", check_env),
    ]
    failed = 0
    for name, check in checks:
        ok, detail = check()
        failed += not ok
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    print()
    print("All checks passed." if not failed else f"{failed} check(s) failed.")
    print("Switch Console must also be open with the local server running; this script cannot check that.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
