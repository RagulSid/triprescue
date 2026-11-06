"""Checks that the seed data matches the scenario and the room rules.

Run: python -m unittest discover tests
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "seed"
ROOMS = ROOT / "rooms"
CAP_INR = 25000
LABELS = {"CONFIRMED", "ADVERTISED ONLY"}


def load(name):
    return json.loads((SEED / name).read_text(encoding="utf-8"))


class SeedTests(unittest.TestCase):
    def test_every_option_is_labeled(self):
        sheet = load("supplier_sheet.json")
        advertised = load("advertised_options.json")
        for option in sheet["transport"]:
            self.assertEqual(option["status"], "CONFIRMED", option["id"])
        for option in advertised["transport"]:
            self.assertEqual(option["status"], "ADVERTISED ONLY", option["id"])
        for key in ("hotel", "guide", "knock_on"):
            self.assertIn(sheet[key]["status"], LABELS, key)

    def test_cap_blocks_only_option_c(self):
        options = load("supplier_sheet.json")["transport"] + load("advertised_options.json")["transport"]
        over_cap = sorted(o["id"] for o in options if o["cost"] > CAP_INR)
        self.assertEqual(over_cap, ["C"])

    def test_option_a_seats_the_whole_group(self):
        group = load("trip.json")["travelers"]
        option_a = next(o for o in load("supplier_sheet.json")["transport"] if o["id"] == "A")
        self.assertGreaterEqual(option_a["seats"], group)

    def test_trip_dinner_matches_the_hotel_hold(self):
        """Travelers ask about dinner; support-agent reads trip.json only, so the hold must be there too."""
        dinner = next(i for i in load("trip.json")["today"] if "Dinner" in i["item"])
        hold = load("supplier_sheet.json")["hotel"]["dinner_held_until"]
        self.assertIn(hold, dinner["item"])
        self.assertLess(dinner["time"], hold)
        self.assertEqual(dinner["ref"], load("supplier_sheet.json")["hotel"]["id"])

    def test_traveler_count_matches_trip(self):
        self.assertEqual(len(load("travelers.json")["travelers"]), load("trip.json")["travelers"])

    def test_emails_use_reserved_domain(self):
        text = "".join(p.read_text(encoding="utf-8") for p in SEED.rglob("*") if p.is_file())
        domains = set(re.findall(r"\b[\w.+-]+@([\w-]+(?:\.[\w-]+)+)", text))
        self.assertEqual(domains, {"example.com"})


TREK_ROOMS = {"parvati-disruption.md", "parvati-trek.md", "pinewood-hq.md"}
SUMMIT_ROOMS = {"summit-disruption.md", "switch-summit.md"}


class RoomRuleTests(unittest.TestCase):
    def test_every_room_file_belongs_to_an_event(self):
        self.assertEqual({p.name for p in ROOMS.glob("*.md")}, TREK_ROOMS | SUMMIT_ROOMS)

    def test_summit_rooms_have_their_five_rules(self):
        for name in SUMMIT_ROOMS:
            text = (ROOMS / name).read_text(encoding="utf-8")
            with self.subTest(room=name):
                self.assertIn("60,000 INR", text)
                self.assertIn("Every registered attendee and invited guest gets a seat", text)
                self.assertIn("the organizer approves", text)
                self.assertIn("ADVERTISED ONLY", text)
                self.assertIn("counts only", text)
                self.assertNotIn("25,000", text)

    def test_every_room_has_all_four_rules(self):
        for path in (ROOMS / n for n in sorted(TREK_ROOMS)):
            text = path.read_text(encoding="utf-8")
            with self.subTest(room=path.name):
                self.assertIn("25,000 INR", text)
                self.assertIn("Keep the group together", text)
                self.assertIn("the organizer approves", text)
                self.assertIn("ADVERTISED ONLY", text)


if __name__ == "__main__":
    unittest.main()
