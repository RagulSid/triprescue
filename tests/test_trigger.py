"""The natural-language trigger: seed/scenarios/index.json, its examples, and the briefs that use it.

Run: python -m unittest discover tests
"""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ROOT / "seed" / "scenarios"
sys.path.insert(0, str(ROOT / "scripts"))
import run_scenario  # noqa: E402

NAMES = sorted(p.name for p in SCENARIOS.iterdir() if p.is_dir())
# Offline sanity check only (the agent itself matches by meaning): words that point at one scenario.
KEYWORDS = {
    "coach_cancelled": r"\b(coach|bus|vehicle)\b",
    "heavy_rain": r"\b(rain|pour|weather|trails?)\b",
    "lunch_unavailable": r"\b(lunch|kitchen|gas|food)\b",
    "traveler_sick": r"\b(unwell|feeling well|leave the trip|go home|stop the trip)\b",
}
# Concrete facts an example may state: times, codes such as HT-22, traveler ids, numbers.
FACT = re.compile(r"\b\d{1,2}:\d{2}\b|\b[A-Z]{2}-\d+\b|\bt\d{2}\b|\b\d+\b")


def scenario(name):
    return json.loads((SCENARIOS / name / "scenario.json").read_text(encoding="utf-8"))


def seed_text(name):
    """Everything the seed data says about a scenario, without its trigger block."""
    s = scenario(name)
    s.pop("trigger")
    parts = [json.dumps(s, ensure_ascii=False)]
    parts += [(ROOT / rel).read_text(encoding="utf-8") for rel in s["data_files"]]
    parts += [p.read_text(encoding="utf-8") for p in (ROOT / "seed").glob("*.json")]
    return "\n".join(parts)


class TriggerTests(unittest.TestCase):
    def test_index_matches_scenarios(self):
        index = json.loads((SCENARIOS / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(index, run_scenario.build_index(),
                         "index.json is stale: run python scripts/run_scenario.py --write-guides")
        self.assertEqual([r["name"] for r in index["scenarios"]], NAMES)

    def test_trigger_shape(self):
        for name in NAMES:
            t = scenario(name)["trigger"]
            with self.subTest(scenario=name):
                self.assertGreater(len(t["description"]), 30)
                self.assertTrue(2 <= len(t["signs"]) <= 4)
                self.assertTrue(2 <= len(t["examples"]) <= 3)

    def test_examples_sound_like_an_organizer(self):
        for name in NAMES:
            for e in scenario(name)["trigger"]["examples"]:
                with self.subTest(scenario=name, example=e[:40]):
                    self.assertNotIn("Scenario:", e)
                    self.assertNotIn("_", e)
                    self.assertNotIn("@", e)
                    self.assertLess(len(e), 220)

    def test_examples_state_only_seeded_facts(self):
        for name in NAMES:
            corpus = seed_text(name)
            for e in scenario(name)["trigger"]["examples"]:
                for fact in FACT.findall(e):
                    with self.subTest(scenario=name, fact=fact):
                        self.assertIn(fact, corpus, f"{fact!r} in an example is not in the seed data")

    def test_each_example_points_at_its_own_scenario(self):
        for name in NAMES:
            for e in scenario(name)["trigger"]["examples"]:
                hits = {n for n, rx in KEYWORDS.items() if re.search(rx, e, re.I)}
                with self.subTest(scenario=name, example=e[:40]):
                    self.assertEqual(hits, {name})

    def test_guides_open_with_a_natural_message(self):
        for name in NAMES:
            s = scenario(name)
            first = run_scenario.messages(s)[0][1]
            with self.subTest(scenario=name):
                self.assertEqual(first, f"@{run_scenario.COORDINATOR} {s['trigger']['examples'][0]}")
                self.assertNotIn("Scenario:", first)
                guide = (SCENARIOS / name / "README.md").read_text(encoding="utf-8")
                self.assertIn(f"Scenario: {name}", guide)  # the override is documented
                self.assertLess(guide.index(first), guide.index("## Other ways to say it"))

    def test_coordinator_brief_matches_then_asks_one_question(self):
        brief = (ROOT / "agents" / run_scenario.COORDINATOR / "CLAUDE.md").read_text(encoding="utf-8")
        for phrase in ("../../seed/scenarios/index.json", "Scenario: <name>", "ONE short question", "Never invent facts",
                       "no scenario name"):
            self.assertIn(phrase, brief)
        self.assertNotIn("use `coach_cancelled`", brief)

    def test_coordinator_does_not_end_its_turn_while_roles_release(self):
        brief = (ROOT / "agents" / run_scenario.COORDINATOR / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("Do not end your turn to wait", brief)
        self.assertIn("at most 5 checks", brief)
        self.assertNotIn("then check `list_roles` once", brief)

    def test_support_agent_counts_the_latest_report_in_any_words(self):
        brief = (ROOT / "agents" / "support-agent" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("../../seed/scenarios/index.json", brief)
        self.assertIn("the organizer's own words", brief)
        self.assertIn("Only the **latest** report counts", brief)
        self.assertNotIn("the texts are the `notice` field", brief)
        self.assertIn('A question or a "what if"', brief)
        self.assertIn("is not a report", brief)

    def test_plain_word_check_catches_technical_leaks(self):
        leaks = ["Room 1a2b3c4d now links to Pinewood HQ", "Opened for coach_cancelled",
                 "Scenario: heavy_rain", "I took ops-desk", "called mcp__switch__link_rooms",
                 "id 1a2b3c4d-0000-4000-8000-00000000abcd"]
        plain = ["The disruption team is working on it, and the organizer will confirm new times here.",
                 "Update for today's travel: we leave Manali at 10:00 in two tempo travellers and reach Kasol at 15:30.",
                 "The disruption is closed. The times posted earlier stand.",
                 "Starting a session to handle this — one moment."]
        for text in leaks:
            with self.subTest(leak=text):
                self.assertIsNotNone(run_scenario.TECHNICAL.search(text))
        for text in plain:
            with self.subTest(plain=text):
                self.assertIsNone(run_scenario.TECHNICAL.search(text))


if __name__ == "__main__":
    unittest.main()
