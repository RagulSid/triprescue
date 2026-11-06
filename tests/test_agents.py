"""Agent folders, permissions and the Console registration data stay consistent."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import setup  # noqa: E402

REGISTRY = json.loads((ROOT / "agents" / "agents.json").read_text(encoding="utf-8"))
NAMES = [a["name"] for a in REGISTRY["agents"]]
ROOM_ADMIN = ["create_room", "update_room", "link_rooms", "unlink_rooms"]


def settings(name):
    return json.loads((ROOT / "agents" / name / ".claude" / "settings.json").read_text(encoding="utf-8"))


def denied(name):
    return set(settings(name)["permissions"]["deny"])


class AgentTests(unittest.TestCase):
    def test_registry_matches_folders(self):
        folders = sorted(p.name for p in (ROOT / "agents").iterdir() if p.is_dir())
        self.assertEqual(sorted(NAMES), folders)

    def test_every_agent_has_a_model_and_safe_defaults(self):
        for name in NAMES:
            s = settings(name)
            self.assertRegex(s.get("model", ""), r"^claude-", name)
            for rule in ("Read(../../.env)", "Read(../../docs/**)", "Edit", "Write", "Bash"):
                self.assertIn(rule, denied(name), f"{name} must deny {rule}")

    def test_only_coordinator_can_create_link_or_archive_rooms(self):
        for name in NAMES:
            if name == "coordinator-agent":
                self.assertFalse(denied(name) & {f"mcp__switch__{t}" for t in ROOM_ADMIN + ["archive_room"]})
                continue
            for tool in ROOM_ADMIN + ["archive_room", "create_agent"]:
                self.assertIn(f"mcp__switch__{tool}", denied(name), f"{name} must deny {tool}")

    def test_support_agent_cannot_invite_but_can_take_the_ops_desk(self):
        d = denied("support-agent")
        self.assertIn("mcp__switch__invite_agent_to_room", d)
        for tool in ("assume_role", "release_role", "list_roles", "read_context",
                     "send_targeted_message", "post_message", "connect_to_room"):
            self.assertNotIn(f"mcp__switch__{tool}", d)

    def test_tools_each_agent_loads_are_not_denied(self):
        for name in NAMES:
            text = (ROOT / "agents" / name / "CLAUDE.md").read_text(encoding="utf-8")
            loaded = set(re.findall(r"mcp__switch__\w+", " ".join(re.findall(r"select:[^`]+", text))))
            self.assertTrue(loaded, f"{name}: no ToolSearch select line")
            self.assertFalse(loaded & denied(name), f"{name} loads a denied tool: {loaded & denied(name)}")

    def test_addressing_lets_travelers_reach_support_only(self):
        addressing = {a["name"]: a["addressing"] for a in REGISTRY["agents"]}
        self.assertEqual(addressing.pop("support-agent"), "anyone")
        self.assertEqual(set(addressing.values()), {"owner-agents"})

    def test_template_lists_every_agent_and_room(self):
        doc = json.loads(setup.template())
        self.assertEqual(doc["version"], 2)
        kinds = {}
        for res in doc["resources"].values():
            kinds.setdefault(res["type"], []).append(res["name"])
        self.assertEqual(sorted(kinds["agent"]), sorted(NAMES))
        self.assertEqual(sorted(kinds["room"]), ["Parvati Trek", "Pinewood HQ", "Switch Summit"])
        self.assertEqual(len(kinds["group"]), 1)


class ConsoleSetupDocTests(unittest.TestCase):
    def test_console_setup_md_matches_the_registry(self):
        doc = (ROOT / "CONSOLE_SETUP.md").read_text(encoding="utf-8")
        for a in REGISTRY["agents"]:
            with self.subTest(agent=a["name"]):
                for value in (f"### {a['name']}", a["description"], a["instructions"], f"agents\\{a['name']}`",
                              settings(a["name"])["model"]):
                    self.assertIn(value, doc)
        for r in REGISTRY["rooms"]:
            with self.subTest(room=r["name"]):
                for value in (f"| Name | `{r['name']}` |", r["description"], r["instructions_file"]):
                    self.assertIn(value, doc)
        self.assertEqual(doc.count("\n### "), len(REGISTRY["agents"]) + len(REGISTRY["rooms"]))


class RoomConfigTests(unittest.TestCase):
    def test_coordinator_and_scripts_take_room_names_from_config(self):
        cfg = json.loads((ROOT / "rooms" / "rooms.json").read_text(encoding="utf-8"))
        self.assertEqual((cfg["trip_room"], cfg["summit_room"], cfg["hq_room"]), ("Parvati Trek", "Switch Summit", "Pinewood HQ"))
        brief = (ROOT / "agents" / "coordinator-agent" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("../../rooms/rooms.local.json", brief)
        self.assertIn("../../rooms/rooms.json", brief)
        self.assertNotIn("named exactly `Parvati Trek`", brief)
        import run_scenario
        self.assertEqual((run_scenario.TRIP, run_scenario.HQ), (run_scenario.ROOMS["trip_room"], run_scenario.ROOMS["hq_room"]))

    def test_local_override_wins_and_is_gitignored(self):
        import tempfile
        import run_scenario
        with tempfile.TemporaryDirectory() as tmp:
            rooms = Path(tmp) / "rooms"
            rooms.mkdir()
            (rooms / "rooms.json").write_text(json.dumps({"trip_room": "Parvati Trek", "hq_room": "Pinewood HQ"}), encoding="utf-8")
            self.assertEqual(run_scenario.load_rooms(Path(tmp))["trip_room"], "Parvati Trek")
            (rooms / "rooms.local.json").write_text(json.dumps({"trip_room": "Bot: Parvati Trek"}), encoding="utf-8")
            got = run_scenario.load_rooms(Path(tmp))
            self.assertEqual((got["trip_room"], got["hq_room"]), ("Bot: Parvati Trek", "Pinewood HQ"))
        self.assertIn("rooms/rooms.local.json", (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())

    def test_coordinator_may_read_the_config(self):
        self.assertIn("Read(../../rooms/**)", settings("coordinator-agent")["permissions"]["allow"])


if __name__ == "__main__":
    unittest.main()
