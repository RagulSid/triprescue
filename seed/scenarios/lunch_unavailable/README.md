# Scenario: Camp kitchen cannot serve lunch (`lunch_unavailable`)

_Synthetic sample data. Pinewood Holidays, the trip, people and suppliers are fictional._

The switchboard opens a private room **Parvati Lunch Disruption** with the roles `ops-desk`, `hotel`, `itinerary`.

## Messages to post (copy each one exactly)

Post one at a time and wait for the result before the next. First run of the day only: send `!reset @switchboard-agent` and `!reset @support-agent` in #parvati-trek.

1. In **#parvati-trek (new message)**:

   ```text
   @switchboard-agent Scenario: lunch_unavailable. Message from Riverbend Camp, Day 3, 09:40: our cooking gas delivery is delayed, so the kitchen cannot serve the group lunch on arrival today. Dinner is not affected. Open the disruption room as your instructions describe.
   ```

   Wait for: the private channel 'Parvati Lunch Disruption' opens; the specialists answer; switchboard posts a handover note and releases ops-desk; support-agent assumes it and sends you one proposal (no message from you needed).

2. In **'Parvati Lunch Disruption'**:

   ```text
   @ops-desk Approved with one change: add the packed lunch boxes as well as the evening snack. Re-check it before I give final approval.
   ```

   Wait for: the re-checked proposal.

3. In **'Parvati Lunch Disruption'**:

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

- **Hotel:** M1 packed lunch boxes 13:30 (6,000 INR) and M2 evening snack 18:30 (3,500 INR), both CONFIRMED; M3 catered lunch (26,000 INR) ADVERTISED ONLY and BLOCKED BY CAP. Hotel proposes the evening snack within the cap.
- **Itinerary:** M1 fits before the 14:00 check-in; M2 fits after the 15:30 trek and before dinner.
- **Proposal:** one plan, M2 evening snack (3,500 of 25,000 INR).
- **Organizer's change:** add M1 as well (total 9,500 INR, within the cap); hotel and itinerary re-check.
- **Travelers told:** the approved meal plan only.

## Check it

- A private channel **Parvati Lunch Disruption** appears; a traveler account cannot see it.
- Options over 25,000 INR are marked BLOCKED BY CAP and left out of the proposal (here: M3).
- switchboard-agent posts a handover note and releases `ops-desk`; support-agent assumes it and sends one proposal without being asked.
- After your final approval there is a line starting `Approval recorded:`, and #parvati-trek gets the approved times only (no options, names or health details).
- On close: one note in #parvati-trek, one summary in #pinewood-hq, and the room shows as archived in Switch Console.

Optional developer check (reads the local Switch database; assumes Switch Console's Windows layout, see `scripts/run_scenario.py`):

```text
python scripts/run_scenario.py lunch_unavailable --verify
```
