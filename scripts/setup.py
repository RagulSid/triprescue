"""Check that this machine is ready to run TripRescue, and print what to enter in Switch Console.

Usage:
  python scripts/setup.py              # run every check (exit 0 only if all pass)
  python scripts/setup.py --template   # print a Switch template (version 2) that creates the agents and rooms

The checks never read Switch Console's credentials or the Switch database, and never print
a token. They cannot see inside Switch Console: whether the agents are registered and the
rooms exist is a manual check (see README, "Set up Switch").
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "agents" / "agents.json"
MATTERMOST_CONTAINER = "mattermost"  # the bundled Mattermost container's name contains this


def run(cmd, timeout=30, cwd=None):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return subprocess.CompletedProcess(cmd, 1, "", str(exc))


def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def check_python():
    ok = sys.version_info >= (3, 10)
    return ok, f"Python {sys.version.split()[0]}" + ("" if ok else " (need 3.10+)")


def check_seed():
    files = sorted((ROOT / "seed").rglob("*.json"))
    if not files:
        return False, "no seed JSON files found"
    for path in files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return False, f"{path.relative_to(ROOT)} is not valid JSON: {exc}"
    return True, f"{len(files)} seed files parse"


def check_agents():
    problems = []
    names = [a["name"] for a in registry()["agents"]]
    for name in names:
        folder = ROOT / "agents" / name
        if not (folder / "CLAUDE.md").is_file():
            problems.append(f"{name}: CLAUDE.md missing")
        try:
            settings = json.loads((folder / ".claude" / "settings.json").read_text(encoding="utf-8"))
            if "model" not in settings:
                problems.append(f"{name}: no model in .claude/settings.json")
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"{name}: .claude/settings.json unreadable ({exc.__class__.__name__})")
    for room in registry()["rooms"]:
        if not (ROOT / room["instructions_file"]).is_file():
            problems.append(f"{room['instructions_file']} missing")
    if problems:
        return False, "; ".join(problems)
    return True, f"{len(names)} agent folders with CLAUDE.md and a model; room instruction files present"


def check_docker():
    docker = shutil.which("docker")
    if not docker:
        return False, "docker not found; install Docker Desktop"
    result = run([docker, "info", "--format", "{{.ServerVersion}}"])
    if result.returncode != 0 or not result.stdout.strip():
        return False, "Docker is installed but the engine is not running; start Docker Desktop"
    return True, f"Docker engine {result.stdout.strip()}"


def check_mattermost():
    docker = shutil.which("docker")
    if not docker:
        return False, "needs Docker"
    result = run([docker, "ps", "--filter", f"name={MATTERMOST_CONTAINER}", "--format", "{{.Names}}"])
    names = [n for n in result.stdout.split() if n]
    if not names:
        return False, ("no running Mattermost container; open Switch Console and start the local server "
                       "(Mattermost comes with it)")
    return True, f"running: {', '.join(names)}"


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


def check_secrets():
    git = shutil.which("git")
    if not git or not (ROOT / ".git").exists():
        return True, "not a git checkout; skipped"
    tracked = run([git, "ls-files", ".env"], cwd=ROOT).stdout.strip()
    if tracked:
        return False, ".env is tracked by git; remove it with: git rm --cached .env"
    return True, ".env is not tracked (no chat-app tokens are needed for the Mattermost demo)"


def check_tests():
    result = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"], timeout=120, cwd=ROOT)
    last = (result.stderr.strip().splitlines() or ["no output"])
    summary = next((l for l in reversed(last) if l.startswith(("Ran ", "OK", "FAILED"))), last[-1])
    ran = next((l for l in last if l.startswith("Ran ")), "")
    if result.returncode != 0:
        return False, f"{ran} {summary}".strip() + "; run: python -m unittest discover tests"
    return True, f"{ran}, OK".strip(", ")


def template():
    """A version 2 Switch template as JSON (JSON is valid YAML). Unverified: not yet run in Console."""
    reg = registry()
    key = lambda name: name.replace("-", "_")
    resources = {}
    for a in reg["agents"]:
        resources[key(a["name"])] = {
            "type": "agent",
            "name": a["name"],
            "description": a["description"],
            "instructions": a["instructions"],
            "provider": "claude",
            "machine": "{machine}",
            "directory": "{repo_dir}/agents/" + a["name"],
            "addressing": a["addressing"],
            "allow_existing": True,
        }
    for r in reg["rooms"]:
        resources[key(r["name"].lower().replace(" ", "_"))] = {
            "type": "room",
            "name": r["name"],
            "description": r["description"],
            "instructions": (ROOT / r["instructions_file"]).read_text(encoding="utf-8"),
            "bridge": "{bridge}",
            "channel_type": r["channel_type"],
            "agents": [key(n) for n in r["agents"]],
            "users": ["{$creator}"],
            "group": "pinewood",
        }
    resources["pinewood"] = {
        "type": "group",
        "name": "Pinewood Holidays",
        "description": "TripRescue base rooms: operator HQ, the trip room and the summit attendee room.",
    }
    doc = {
        "version": 2,
        "params": {
            "machine": {"type": "machine", "default": ["$first"], "description": "Where the agents run"},
            "bridge": {"type": "bridge", "default": ["$first"], "description": "Messaging app (Mattermost)"},
            "repo_dir": {"type": "string", "default": ROOT.as_posix(), "description": "Folder of this clone"},
        },
        "resources": resources,
    }
    return json.dumps(doc, indent=2, ensure_ascii=False)


def main():
    if "--template" in sys.argv:
        print(template())
        return 0
    checks = [
        ("Python", check_python),
        ("Seed data", check_seed),
        ("Agent folders", check_agents),
        ("Docker", check_docker),
        ("Mattermost", check_mattermost),
        ("Claude Code", check_claude),
        ("Secrets", check_secrets),
        ("Tests", check_tests),
    ]
    failed = 0
    for name, check in checks:
        ok, detail = check()
        failed += not ok
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    print()
    print("All checks passed." if not failed else f"{failed} check(s) failed.")
    print("Not checked here (look in Switch Console): the seven agents are registered and running,")
    print("and the rooms Pinewood HQ, Parvati Trek and Switch Summit exist. The fields are in CONSOLE_SETUP.md.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
