# Scenario: Coach HT-22 cancelled (`coach_cancelled`)

_Synthetic sample data. Pinewood Holidays, the trip, people and suppliers are fictional._

coordinator-agent opens a private room **Parvati Coach Disruption** with the roles `ops-desk`, `transport`, `hotel`, `itinerary`.

## Messages to post (copy each one exactly)

Post one at a time and wait for the result before the next. First run of the day only: send `!reset @coordinator-agent` and `!reset @support-agent` in the trip room.

1. In **the trip room (#parvati-trek, or your Telegram group)**:

   ```text
   @coordinator-agent Dispatch just called: coach HT-22 to Kasol is withdrawn today with a mechanical fault, and they have no replacement vehicle. Can you sort out a new plan?
   ```

   Wait for: one plain sentence back in the trip room; the private channel 'Parvati Coach Disruption' opens; the specialists answer; coordinator-agent posts a handover note and releases ops-desk; support-agent assumes it and sends you one proposal (no message from you needed).

2. In **'Parvati Coach Disruption'**:

   ```text
   @ops-desk Approved with one change: start tomorrow's trek at 09:30 instead of 09:00. Re-check it before I give final approval.
   ```

   Wait for: the re-checked proposal.

3. In **'Parvati Coach Disruption'**:

   ```text
   @ops-desk Final approval: approved as re-checked. Record it and tell the travelers.
   ```

   Wait for: "Approval recorded" and support-agent's message to travelers in the trip room.

4. In **the trip room (#parvati-trek, or your Telegram group)**:

   ```text
   @coordinator-agent The plan is approved and the travelers have been told. Please close the disruption room.
   ```

   Wait for: one closing note in the trip room and one summary in #pinewood-hq.

## Other ways to say it

This scenario: The Manali to Kasol coach (HT-22) is cancelled for today and the supplier has no replacement. The coordinator matches your own words to it, so any of these work as message 1:

- `@coordinator-agent Our 08:30 coach from Manali is cancelled. How do we get everyone to Kasol today?`
- `@coordinator-agent Bad news: the bus to Kasol broke down this morning and the supplier can't replace it.`

If it is unsure, it asks one short question; answer it in the same thread. To force this scenario, add a line `Scenario: coach_cancelled`.

## Expected outcome

- **Transport:** A (two tempo travellers, 10:00 to 15:30, 18,400 INR) CONFIRMED; B (state bus, 11:15 to 17:30, 9,000 INR) CONFIRMED but no seat count; C (private coach, 31,000 INR) ADVERTISED ONLY and BLOCKED BY CAP.
- **Hotel:** Riverbend Camp holds rooms to 20:00 and dinner to 20:30 (CONFIRMED); A and B both make it.
- **Itinerary:** today's 15:30 trek cannot run; it moves to tomorrow inside Tenzin's 09:00 to 12:00 window, which needs tomorrow's Tosh departure moved from 10:00 to 14:00 (0 INR, CONFIRMED by transport).
- **Proposal:** one plan, Option A, 18,400 of 25,000 INR, group together.
- **Organizer's change:** trek at 09:30; itinerary re-checks; nothing else moves.
- **Travelers told:** the approved times only.
- **Open items for a person:** seats for 20 at 14:00 to Tosh; trek duration; Kasol to camp transfer time.

## Check it

- The coordinator answers in the trip room with one plain sentence (no scenario name, room id or tool name).
- A private channel **Parvati Coach Disruption** appears; a traveler account cannot see it.
- Options over 25,000 INR are marked BLOCKED BY CAP and left out of the proposal (here: C).
- coordinator-agent posts a handover note and releases `ops-desk`; support-agent assumes it and sends one proposal without being asked.
- After your final approval there is a line starting `Approval recorded:`, and the trip room gets the approved times only (no options, names or health details).
- On close: one note in the trip room, one summary in #pinewood-hq, and the room shows as archived in Switch Console.

Optional developer check (reads the local Switch database; assumes Switch Console's Windows layout, see `scripts/run_scenario.py`):

```text
python scripts/run_scenario.py --verify
```
