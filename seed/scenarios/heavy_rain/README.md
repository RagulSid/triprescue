# Scenario: Heavy rain cancels the afternoon trek (`heavy_rain`)

_Synthetic sample data. Pinewood Holidays, the trip, people and suppliers are fictional._

The switchboard opens a private room **Parvati Rain Disruption** with the roles `ops-desk`, `transport`, `itinerary`.

## Messages to post (copy each one exactly)

Post one at a time and wait for the result before the next. First run of the day only: send `!reset @switchboard-agent` and `!reset @support-agent` in #parvati-trek.

1. In **#parvati-trek (new message)**:

   ```text
   @switchboard-agent Scenario: heavy_rain. Weather alert, Day 3, 12:10 (sample district desk): heavy rain from 14:00 to 20:00 today. The Parvati valley trails are closed this afternoon, so all guided treks are cancelled. Roads to Kasol stay open. Open the disruption room as your instructions describe.
   ```

   Wait for: the private channel 'Parvati Rain Disruption' opens; the specialists answer; switchboard posts a handover note and releases ops-desk; support-agent assumes it and sends you one proposal (no message from you needed).

2. In **'Parvati Rain Disruption'**:

   ```text
   @ops-desk Approved with one change: do both: the woodcraft workshop today and the trek tomorrow morning. Re-check it before I give final approval.
   ```

   Wait for: the re-checked proposal.

3. In **'Parvati Rain Disruption'**:

   ```text
   @ops-desk Final approval: approved as re-checked. Record it and tell the travelers.
   ```

   Wait for: "Approval recorded" and support-agent's message to travelers in #parvati-trek.

4. In **#parvati-trek**:

   ```text
   @switchboard-agent The plan is approved and the travelers have been told. Close the room as your instructions describe.
   ```

   Wait for: one closing note in #parvati-trek and one summary in #pinewood-hq.

## Expected outcome

- **Itinerary:** today's 15:30 trek is cancelled. Two alternatives: an indoor activity today (R1 cooking class 8,000 INR or R2 woodcraft workshop 5,000 INR, both CONFIRMED), or the trek tomorrow inside Tenzin's 09:00 to 12:00 window (0 INR, CONFIRMED). R3 hot-spring pools (27,000 INR) is ADVERTISED ONLY and BLOCKED BY CAP.
- **Transport:** tomorrow's Tosh departure can move from 10:00 to 14:00 at 0 INR (CONFIRMED); seats for 20 are not in the sheet.
- **Proposal:** one plan, for example R2 today plus the trek tomorrow, within the 25,000 INR cap, group together.
- **Organizer's change:** "do both" (workshop today, trek tomorrow); itinerary re-checks.
- **Travelers told:** the approved plan only.

## Check it

- A private channel **Parvati Rain Disruption** appears; a traveler account cannot see it.
- Options over 25,000 INR are marked BLOCKED BY CAP and left out of the proposal (here: R3).
- switchboard-agent posts a handover note and releases `ops-desk`; support-agent assumes it and sends one proposal without being asked.
- After your final approval there is a line starting `Approval recorded:`, and #parvati-trek gets the approved times only (no options, names or health details).
- On close: one note in #parvati-trek, one summary in #pinewood-hq, and the room shows as archived in Switch Console.

Optional developer check (reads the local Switch database; assumes Switch Console's Windows layout, see `scripts/run_scenario.py`):

```text
python scripts/run_scenario.py heavy_rain --verify
```
