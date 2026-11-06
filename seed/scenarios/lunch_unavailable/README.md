# Scenario: Camp kitchen cannot serve lunch (`lunch_unavailable`)

_Synthetic sample data. Pinewood Holidays, the trip, people and suppliers are fictional._

switchboard-agent opens a private room **Parvati Lunch Disruption** with the roles `ops-desk`, `hotel`, `itinerary`.

## Messages to post (copy each one exactly)

Post one at a time and wait for the result before the next. First run of the day only: send `!reset @switchboard-agent` and `!reset @support-agent` in the trip room.

1. In **the trip room (#parvati-trek, or your Telegram group)**:

   ```text
   @switchboard-agent Riverbend Camp says their cooking gas delivery is late, so they can't serve lunch when we arrive today. Dinner is fine.
   ```

   Wait for: one plain sentence back in the trip room; the private channel 'Parvati Lunch Disruption' opens; the specialists answer; switchboard-agent posts a handover note and releases ops-desk; support-agent assumes it and sends you one proposal (no message from you needed).

2. In **'Parvati Lunch Disruption'**:

   ```text
   @ops-desk Approved with one change: add the packed lunch boxes as well as the evening snack. Re-check it before I give final approval.
   ```

   Wait for: the re-checked proposal.

3. In **'Parvati Lunch Disruption'**:

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

This scenario: Riverbend Camp cannot serve the group lunch on arrival today; dinner is not affected. The coordinator matches your own words to it, so any of these work as message 1:

- `@switchboard-agent The camp kitchen can't do lunch today. Can you find something for the group?`
- `@switchboard-agent No lunch at Riverbend today because of a gas problem. Please sort out food for 20 people.`

If it is unsure, it asks one short question; answer it in the same thread. To force this scenario, add a line `Scenario: lunch_unavailable`.

## Expected outcome

- **Hotel:** M1 packed lunch boxes 13:30 (6,000 INR) and M2 evening snack 18:30 (3,500 INR), both CONFIRMED; M3 catered lunch (26,000 INR) ADVERTISED ONLY and BLOCKED BY CAP. Hotel proposes the evening snack within the cap.
- **Itinerary:** M1 fits before the 14:00 check-in; M2 fits after the 15:30 trek and before dinner.
- **Proposal:** one plan, M2 evening snack (3,500 of 25,000 INR).
- **Organizer's change:** add M1 as well (total 9,500 INR, within the cap); hotel and itinerary re-check.
- **Travelers told:** the approved meal plan only.

## Check it

- The coordinator answers in the trip room with one plain sentence (no scenario name, room id or tool name).
- A private channel **Parvati Lunch Disruption** appears; a traveler account cannot see it.
- Options over 25,000 INR are marked BLOCKED BY CAP and left out of the proposal (here: M3).
- switchboard-agent posts a handover note and releases `ops-desk`; support-agent assumes it and sends one proposal without being asked.
- After your final approval there is a line starting `Approval recorded:`, and the trip room gets the approved times only (no options, names or health details).
- On close: one note in the trip room, one summary in #pinewood-hq, and the room shows as archived in Switch Console.

Optional developer check (reads the local Switch database; assumes Switch Console's Windows layout, see `scripts/run_scenario.py`):

```text
python scripts/run_scenario.py --verify
```
