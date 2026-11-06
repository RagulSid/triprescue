"""The Switch Summit event: seed data, the venue-agent, and the event settings every scenario uses.

Run: python -m unittest discover tests
"""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUMMIT = ROOT / "seed" / "summit"
VIP = ROOT / "seed" / "scenarios" / "vip_guests"
sys.path.insert(0, str(ROOT / "scripts"))
import run_scenario  # noqa: E402

EVENTS = json.loads((ROOT / "seed" / "events.json").read_text(encoding="utf-8"))["events"]


def load(name):
    return json.loads((SUMMIT / name).read_text(encoding="utf-8"))


class EventSettingsTests(unittest.TestCase):
    def test_every_event_points_at_real_files_and_rooms(self):
        rooms = json.loads((ROOT / "rooms" / "rooms.json").read_text(encoding="utf-8"))
        for key, e in EVENTS.items():
            with self.subTest(event=key):
                self.assertIn(e["room_key"], rooms)
                for rel in (e["facts_file"], e["room_file"], e["reference"]["path"]):
                    self.assertTrue((ROOT / rel).is_file(), rel)
                self.assertIn(e["audience"], {"travelers", "attendees"})
                self.assertGreater(e["cap_inr"], 0)

    def test_trek_settings_match_what_the_trek_used_before(self):
        e = EVENTS["parvati"]
        self.assertEqual((e["room_key"], e["room_file"], e["link_label"], e["cap_inr"]),
                         ("trip_room", "rooms/parvati-disruption.md", "parent trip", 25000))
        self.assertEqual(e["reference"], {"name": "Pinewood supplier sheet", "path": "seed/supplier_sheet.json"})
        self.assertEqual(e["label"], run_scenario.TRIP_LABEL)

    def test_room_file_states_the_event_cap(self):
        for key, e in EVENTS.items():
            with self.subTest(event=key):
                self.assertIn(f"{e['cap_inr']:,} INR", (ROOT / e["room_file"]).read_text(encoding="utf-8"))


class SummitSeedTests(unittest.TestCase):
    def test_attendee_needs_are_counts_only(self):
        event = load("event.json")
        diets = {k: v for k, v in event["meal_counts"].items() if not k.startswith("_") and k != "nut_free"}
        self.assertEqual(sum(diets.values()), event["attendees"])
        for value in list(event["seating_needs"].values()) + list(event["meal_counts"].values()):
            self.assertTrue(isinstance(value, int) or str(value).startswith("Counts only"))
        # No person-level records anywhere in the summit seed.
        for f in SUMMIT.glob("*.json"):
            with self.subTest(file=f.name):
                self.assertNotRegex(f.read_text(encoding="utf-8"), r'"(attendee_name|first_name|last_name|email|phone)"')

    def test_labels_and_cap(self):
        cap = EVENTS["summit"]["cap_inr"]
        sheet, ads = load("venue_sheet.json"), load("advertised_options.json")
        confirmed = sheet["seating"] + sheet["catering"]
        advertised = ads["seating"] + ads["catering"]
        self.assertTrue(all(o["status"] == "CONFIRMED" for o in confirmed))
        self.assertTrue(all(o["status"] == "ADVERTISED ONLY" for o in advertised))
        self.assertEqual(sorted(o["id"] for o in confirmed + advertised if o["cost"] > cap), ["V3"])

    def test_only_v1_seats_the_guests_together_at_the_front(self):
        needs = load("event.json")["seating_needs"]
        guests = json.loads((VIP / "delegation.json").read_text(encoding="utf-8"))["guests"]
        front = needs["speakers"] + needs["vip_front_row"] + guests
        options = load("venue_sheet.json")["seating"] + load("advertised_options.json")["seating"]
        ok = sorted(o["id"] for o in options
                    if o.get("front_row", True) and o["together"] and o.get("front_seats_after", 0) >= front
                    and o["cost"] <= EVENTS["summit"]["cap_inr"])
        self.assertEqual(ok, ["V1"])

    def test_hall_a_still_seats_everyone(self):
        event = load("event.json")
        guests = json.loads((VIP / "delegation.json").read_text(encoding="utf-8"))["guests"]
        hall_a = next(r for r in event["rooms"] if r["id"] == "hall-a")
        v1 = next(o for o in load("venue_sheet.json")["seating"] if o["id"] == "V1")
        self.assertGreaterEqual(hall_a["seats"] + v1["seats_added"], event["attendees"] + guests)

    def test_kitchen_can_take_the_guests_and_the_speech_fits_the_break(self):
        k1 = next(o for o in load("venue_sheet.json")["catering"] if o["id"] == "K1")
        guests = json.loads((VIP / "delegation.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(k1["max_extra_meals"], guests["guests"])
        self.assertEqual(k1["meals"], guests["guests"])
        agenda = {i["item"]: i for i in load("event.json")["today"]}
        minutes = lambda hhmm: int(hhmm[:2]) * 60 + int(hhmm[3:])
        speech = guests["welcome_speech"]["length_minutes"]
        brk = agenda["Coffee break"]
        self.assertEqual(agenda["Opening keynote"]["end"], brk["time"])
        self.assertLess(speech, minutes(brk["end"]) - minutes(brk["time"]))  # the keynote shift is absorbed by the break
        told = json.loads((VIP / "scenario.json").read_text(encoding="utf-8"))["expected"]["travelers_told"]
        for t in ("09:30", "09:35", "10:35"):
            self.assertIn(t, told)
        self.assertNotRegex(told, r"(?i)vegan|vegetarian|diet|allerg|Harbourline")

    def test_delegation_has_counts_and_no_names(self):
        d = json.loads((VIP / "delegation.json").read_text(encoding="utf-8"))
        self.assertEqual(d["diet"]["vegetarian"], d["guests"])
        self.assertFalse({"names", "guest_names", "people"} & set(d))

    def test_everything_is_marked_synthetic(self):
        for f in SUMMIT.glob("*.json"):
            with self.subTest(file=f.name):
                self.assertRegex(f.read_text(encoding="utf-8"), r"(?i)synthetic sample data")


class VenueAgentTests(unittest.TestCase):
    def test_seating_role_goes_to_venue_agent(self):
        self.assertEqual(run_scenario.ROLE_AGENT["seating"], "venue-agent")
        brief = (ROOT / "agents" / "coordinator-agent" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("`seating` → `venue-agent`", brief)
        self.assertIn("**Holder:** `venue-agent`", (ROOT / "rooms" / "roles" / "seating.md").read_text(encoding="utf-8"))

    def test_venue_agent_is_haiku_and_cannot_admin_rooms(self):
        s = json.loads((ROOT / "agents" / "venue-agent" / ".claude" / "settings.json").read_text(encoding="utf-8"))
        self.assertEqual(s["model"], "claude-haiku-5-5")
        for tool in ("create_room", "archive_room", "link_rooms", "update_room"):
            self.assertIn(f"mcp__switch__{tool}", s["permissions"]["deny"])

    def test_support_agent_keeps_attendee_needs_private(self):
        brief = (ROOT / "agents" / "support-agent" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("Switch Summit", brief)
        self.assertIn("../../seed/summit/event.json", brief)
        self.assertIn("tie a diet, an allergy or an accessibility need to a person", brief)

    def test_plain_word_check_covers_the_summit_scenario(self):
        self.assertIsNotNone(run_scenario.TECHNICAL.search("Opened for vip_guests"))
        self.assertIsNone(run_scenario.TECHNICAL.search(
            "Update: we welcome a partner delegation at 09:30, and the keynote now runs 09:35 to 10:35."))

    def test_catering_agent_drafts_and_never_sends(self):
        self.assertEqual(run_scenario.ROLE_AGENT["catering"], "catering-agent")
        brief = (ROOT / "agents" / "catering-agent" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("draft for the organizer", brief)
        self.assertIn("counts only", brief)
        s = json.loads((ROOT / "agents" / "catering-agent" / ".claude" / "settings.json").read_text(encoding="utf-8"))
        self.assertEqual(s["model"], "claude-haiku-5-5")
        self.assertIn("`catering` → `catering-agent`",
                      (ROOT / "agents" / "coordinator-agent" / "CLAUDE.md").read_text(encoding="utf-8"))

    def test_itinerary_agent_drafts_the_welcome_speech(self):
        brief = (ROOT / "agents" / "itinerary-agent" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("**Speech drafts:**", brief)
        self.assertIn("at most 5 sentences", brief)

    def test_summit_guide_uses_the_attendee_room_and_cap(self):
        s = run_scenario.load_scenario("vip_guests")
        guide = run_scenario.render_guide(s)
        self.assertIn("the attendee room (#switch-summit)", guide)
        self.assertIn("Options over 60,000 INR", guide)
        self.assertIn("an attendee account cannot see it", guide)
        self.assertNotRegex(guide, re.compile(r"trip room|25,000"))

if __name__ == "__main__":
    unittest.main()
