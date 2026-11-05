# Scenario: Coach HT-22 cancelled (`coach_cancelled`)

_Synthetic sample data. Pinewood Holidays, the trip, people and suppliers are fictional._

The switchboard opens a private room **Parvati Coach Disruption** with the roles `ops-desk`, `transport`, `hotel`, `itinerary`.

## Messages to post (copy each one exactly)

Post one at a time and wait for the result before the next. First run of the day only: send `!reset @switchboard-agent` and `!reset @support-agent` in #parvati-trek.

1. In **#parvati-trek (new message)**:

   ```text
   @switchboard-agent Scenario: coach_cancelled. Notice from dispatch, Day 3, 06:52: Coach HT-22 (Manali to Kasol, 08:30) is withdrawn for today due to a mechanical fault. We cannot provide a replacement vehicle. Open the disruption room as your instructions describe.
   ```

   Wait for: the private channel 'Parvati Coach Disruption' opens and switchboard posts "ready to draft one proposal".

2. In **'Parvati Coach Disruption'**:

   ```text
   @switchboard-agent You're needed on another disruption. Hand the ops desk over to support-agent now, as your instructions describe.
   ```

   Wait for: support-agent assumes the ops-desk role.

3. In **'Parvati Coach Disruption'**:

   ```text
   @ops-desk Send me the proposal.
   ```

   Wait for: one proposal.

4. In **'Parvati Coach Disruption'**:

   ```text
   @ops-desk Approved with one change: start tomorrow's trek at 09:30 instead of 09:00. Re-check it before I give final approval.
   ```

   Wait for: the re-checked proposal.

5. In **'Parvati Coach Disruption'**:

   ```text
   @ops-desk Final approval: approved as re-checked. Record it and tell the travelers.
   ```

   Wait for: "Approval recorded" and support-agent's message to travelers in #parvati-trek.

6. In **#parvati-trek**:

   ```text
   @switchboard-agent The plan is approved and the travelers have been told. Close the room as your instructions describe.
   ```

   Wait for: one closing note in #parvati-trek and one summary in #pinewood-hq.

## Expected outcome

- **Transport:** A (two tempo travellers, 10:00 to 15:30, 18,400 INR) CONFIRMED; B (state bus, 11:15 to 17:30, 9,000 INR) CONFIRMED but no seat count; C (private coach, 31,000 INR) ADVERTISED ONLY and BLOCKED BY CAP.
- **Hotel:** Riverbend Camp holds rooms to 20:00 and dinner to 20:30 (CONFIRMED); A and B both make it.
- **Itinerary:** today's 15:30 trek cannot run; it moves to tomorrow inside Tenzin's 09:00 to 12:00 window, which needs tomorrow's Tosh departure moved from 10:00 to 14:00 (0 INR, CONFIRMED by transport).
- **Proposal:** one plan, Option A, 18,400 of 25,000 INR, group together.
- **Organizer's change:** trek at 09:30; itinerary re-checks; nothing else moves.
- **Travelers told:** the approved times only.
- **Open items for a person:** seats for 20 at 14:00 to Tosh; trek duration; Kasol to camp transfer time.

## Check it

```text
python scripts/run_scenario.py coach_cancelled --verify
```

Run it with the Python inside the local Switch server (see `scripts/run_scenario.py`).
