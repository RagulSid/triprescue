"""Checks every scenario in seed/scenarios/ against the room rules.

Run: python -m unittest discover tests
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ROOT / "seed" / "scenarios"
ROLES = ROOT / "rooms" / "roles"
EVENTS = json.loads((ROOT / "seed" / "events.json").read_text(encoding="utf-8"))["events"]
LABELS = {"CONFIRMED", "ADVERTISED ONLY"}
EXPECTED_NAMES = {"coach_cancelled", "heavy_rain", "traveler_sick", "vip_guests"}
REQUIRED_KEYS = {"name", "event", "title", "room_name", "trigger", "notice", "roles", "data_files", "changed_facts",
                 "asks", "options", "organizer_change", "expected"}
# Words that would mean medical content rather than logistics.
MEDICAL_WORDS = re.compile(r"\b(diagnos\w*|symptom\w*|medicat\w*|dose|prescri\w*|fever|infection|treatment)\b", re.I)


def scenarios():
    for path in sorted(SCENARIOS.iterdir()):
        if path.is_dir():
            yield path, json.loads((path / "scenario.json").read_text(encoding="utf-8"))


class ScenarioTests(unittest.TestCase):
    def test_the_expected_scenarios_exist(self):
        self.assertEqual({s["name"] for _, s in scenarios()}, EXPECTED_NAMES)

    def test_every_scenario_names_a_known_event(self):
        for path, s in scenarios():
            with self.subTest(scenario=path.name):
                self.assertIn(s["event"], EVENTS)
        self.assertEqual({s["name"] for _, s in scenarios() if s["event"] == "summit"}, {"vip_guests"})

    def test_shape_and_files(self):
        for path, s in scenarios():
            with self.subTest(scenario=path.name):
                self.assertEqual(s["name"], path.name)
                self.assertTrue(REQUIRED_KEYS <= set(s), REQUIRED_KEYS - set(s))
                self.assertGreater(len(s["notice"]), 40)
                self.assertTrue(s["expected"]["notes"])
                for rel in s["data_files"]:
                    self.assertTrue((ROOT / rel).is_file(), rel)
                    if rel.endswith(".json"):
                        json.loads((ROOT / rel).read_text(encoding="utf-8"))
                for o in s["options"]:
                    self.assertTrue((ROOT / o["source"]).is_file(), o["source"])

    def test_roles_exist_and_ops_desk_is_first(self):
        for path, s in scenarios():
            with self.subTest(scenario=path.name):
                self.assertEqual(s["roles"][0], "ops-desk")
                for role in s["roles"]:
                    self.assertTrue((ROLES / f"{role}.md").is_file(), role)
                self.assertEqual(set(s["asks"]), set(s["roles"]) - {"ops-desk"})

    def test_readme_matches_scenario_json(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("run_scenario", ROOT / "scripts" / "run_scenario.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for path, s in scenarios():
            with self.subTest(scenario=path.name):
                readme = (path / "README.md").read_text(encoding="utf-8")
                self.assertEqual(readme, mod.render_guide(s),
                                 "README.md is stale: run python scripts/run_scenario.py --write-guides")
                self.assertLess(readme.index("## Messages to post"), readme.index("## Expected outcome"))
                self.assertIn(s["trigger"]["examples"][0], readme)

    def test_room_names_are_unique(self):
        names = [s["room_name"] for _, s in scenarios()]
        self.assertEqual(len(names), len(set(names)))

    def test_every_option_is_labeled(self):
        for path, s in scenarios():
            for o in s["options"]:
                with self.subTest(scenario=path.name, option=o["id"]):
                    self.assertIn(o["status"], LABELS)

    def test_options_match_their_source_files(self):
        for path, s in scenarios():
            for o in s["options"]:
                source = json.loads((ROOT / o["source"]).read_text(encoding="utf-8"))
                items = [i for v in source.values() if isinstance(v, list) for i in v if isinstance(i, dict)]
                match = next((i for i in items if i.get("id") == o["id"]), None)
                if match is None:  # options built from the supplier sheet (e.g. a trek moved to tomorrow)
                    continue
                with self.subTest(scenario=path.name, option=o["id"]):
                    self.assertEqual(match["cost"], o["cost"])
                    self.assertEqual(match["status"], o["status"])

    def test_cap_blocks_exactly_the_expected_options(self):
        for path, s in scenarios():
            with self.subTest(scenario=path.name):
                over = sorted(o["id"] for o in s["options"] if o["cost"] > EVENTS[s["event"]]["cap_inr"])
                self.assertEqual(over, sorted(s["expected"]["blocked_by_cap"]))
                for oid in s["expected"]["blocked_by_cap"]:
                    self.assertEqual(next(o for o in s["options"] if o["id"] == oid)["status"], "ADVERTISED ONLY")

    def test_expected_proposal_is_confirmed_and_within_cap(self):
        for path, s in scenarios():
            with self.subTest(scenario=path.name):
                chosen = [o for o in s["options"] if o["id"] in s["expected"]["proposal_options"]]
                self.assertEqual(len(chosen), len(s["expected"]["proposal_options"]))
                self.assertTrue(all(o["status"] == "CONFIRMED" for o in chosen))
                self.assertEqual(sum(o["cost"] for o in chosen), s["expected"]["total_cost_inr"])
                self.assertLessEqual(s["expected"]["total_cost_inr"], EVENTS[s["event"]]["cap_inr"])

    def test_only_traveler_sick_splits_the_group(self):
        for path, s in scenarios():
            with self.subTest(scenario=path.name):
                self.assertEqual(s["expected"]["split_needs_approval"], path.name == "traveler_sick")

    def test_traveler_sick_is_logistics_only(self):
        path = SCENARIOS / "traveler_sick"
        for f in path.iterdir():
            text = f.read_text(encoding="utf-8")
            with self.subTest(file=f.name):
                self.assertIsNone(MEDICAL_WORDS.search(text), MEDICAL_WORDS.search(text))
        data = json.loads((path / "return_options.json").read_text(encoding="utf-8"))
        self.assertTrue(data["sample_clinic"]["sample"])
        self.assertIn("SAMPLE DATA", data["sample_clinic"]["name"])
        s = json.loads((path / "scenario.json").read_text(encoding="utf-8"))
        self.assertIn("approve", s["organizer_change"])
        self.assertNotIn("t07", s["expected"]["travelers_told"])

    def test_everything_is_marked_synthetic(self):
        for path, _ in scenarios():
            for f in path.iterdir():
                with self.subTest(file=f"{path.name}/{f.name}"):
                    self.assertRegex(f.read_text(encoding="utf-8"), r"(?i)synthetic sample data")


if __name__ == "__main__":
    unittest.main()
