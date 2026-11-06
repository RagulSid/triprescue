# Scenario: Heavy rain cancels the afternoon trek (`heavy_rain`)

_Synthetic sample data. Pinewood Holidays, the trip, people and suppliers are fictional._

switchboard-agent opens a private room **Parvati Rain Disruption** with the roles `ops-desk`, `transport`, `itinerary`.

## Messages to post (copy each one exactly)

Post one at a time and wait for the result before the next. First run of the day only: send `!reset @switchboard-agent` and `!reset @support-agent` in the trip room.

1. In **the trip room (#parvati-trek, or your Telegram group)**:

   ```text
   @switchboard-agent Weather alert: heavy rain from 14:00 to 20:00 today and the trails are closed, so the 15:30 trek with Tenzin is off. Can you rework the afternoon?
   ```

   Wait for: one plain sentence back in the trip room; the private channel 'Parvati Rain Disruption' opens; the specialists answer; switchboard-agent posts a handover note and releases ops-desk; support-agent assumes it and sends you one proposal (no message from you needed).

2. In **'Parvati Rain Disruption'**:

   ```text
   @ops-desk Approved with one change: do both: the woodcraft workshop today and the trek tomorrow morning. Re-check it before I give final approval.
   ```

   Wait for: the re-checked proposal.

3. In **'Parvati Rain Disruption'**:

   ```text
   @ops-desk Final approval: approved as re-checked. Record it and tell the travelers.
   ```

   Wait for: "Approval recorded" and support-agent's message to travelers in the trip room.

4. In **the trip room (#parvati-trek, or your Telegram group)**:

   ```text
   @switchboard-agent The plan is approved and the travelers have been told. Please close the disruption room.
   ```

   Wait for: one closing note in the trip room and one summary in #pinewood-hq.

## Other ways to say it

This scenario: Heavy rain closes the valley trails this afternoon, so today's guided trek cannot run; roads stay open. The coordinator matches your own words to it, so any of these work as message 1:

- `@switchboard-agent It's going to pour this afternoon and the valley trails are shut. What do we do instead of the trek?`
- `@switchboard-agent Rain has cancelled today's trek. The roads to Kasol are fine.`

If it is unsure, it asks one short question; answer it in the same thread. To force this scenario, add a line `Scenario: heavy_rain`.

## Expected outcome

- **Itinerary:** today's 15:30 trek is cancelled. Two alternatives: an indoor activity today (R1 cooking class 8,000 INR or R2 woodcraft workshop 5,000 INR, both CONFIRMED), or the trek tomorrow inside Tenzin's 09:00 to 12:00 window (0 INR, CONFIRMED). R3 hot-spring pools (27,000 INR) is ADVERTISED ONLY and BLOCKED BY CAP.
- **Transport:** tomorrow's Tosh departure can move from 10:00 to 14:00 at 0 INR (CONFIRMED); seats for 20 are not in the sheet.
- **Proposal:** one plan, for example R2 today plus the trek tomorrow, within the 25,000 INR cap, group together.
- **Organizer's change:** "do both" (workshop today, trek tomorrow); itinerary re-checks.
- **Travelers told:** the approved plan only.

## Check it

- The coordinator answers in the trip room with one plain sentence (no scenario name, room id or tool name).
- A private channel **Parvati Rain Disruption** appears; a traveler account cannot see it.
- Options over 25,000 INR are marked BLOCKED BY CAP and left out of the proposal (here: R3).
- switchboard-agent posts a handover note and releases `ops-desk`; support-agent assumes it and sends one proposal without being asked.
- After your final approval there is a line starting `Approval recorded:`, and the trip room gets the approved times only (no options, names or health details).
- On close: one note in the trip room, one summary in #pinewood-hq, and the room shows as archived in Switch Console.

Optional developer check (reads the local Switch database; assumes Switch Console's Windows layout, see `scripts/run_scenario.py`):

```text
python scripts/run_scenario.py --verify
```
