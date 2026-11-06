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

    def test_only_switchboard_can_create_link_or_archive_rooms(self):
        for name in NAMES:
            if name == "switchboard-agent":
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
        self.assertEqual(sorted(kinds["room"]), ["Parvati Trek", "Pinewood HQ"])
        self.assertEqual(len(kinds["group"]), 1)


if __name__ == "__main__":
    unittest.main()
