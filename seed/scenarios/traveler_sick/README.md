# Scenario: One traveler unwell and leaving the trip (`traveler_sick`)

_Synthetic sample data. Pinewood Holidays, the trip, people and suppliers are fictional. Logistics only: no medical details or advice._

coordinator-agent opens a private room **Parvati Traveler Disruption** with the roles `ops-desk`, `transport`, `hotel`, `itinerary`.

## Messages to post (copy each one exactly)

Post one at a time and wait for the result before the next. First run of the day only: send `!reset @coordinator-agent` and `!reset @support-agent` in the trip room.

1. In **the trip room (#parvati-trek, or your Telegram group)**:

   ```text
   @coordinator-agent Tenzin says traveler t07 is unwell and wants to stop the trip and go back to Manali today. They're resting at Riverbend Camp.
   ```

   Wait for: one plain sentence back in the trip room; the private channel 'Parvati Traveler Disruption' opens; the specialists answer; coordinator-agent posts a handover note and releases ops-desk; support-agent assumes it and sends you one proposal (no message from you needed).

2. In **'Parvati Traveler Disruption'**:

   ```text
   @ops-desk Approved with one change: use the 14:00 taxi, and I approve the split: t07 returns to Manali, the other 19 continue. Re-check it before I give final approval.
   ```

   Wait for: the re-checked proposal.

3. In **'Parvati Traveler Disruption'**:

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

This scenario: One traveler (t07) is unwell and wants to leave the trip and go back to Manali today; 19 continue. The coordinator matches your own words to it, so any of these work as message 1:

- `@coordinator-agent t07 isn't feeling well and wants to go home to Manali. Can you plan their return and keep the rest of the group going?`
- `@coordinator-agent One of our travelers, t07, wants to leave the trip today because they're unwell.`

If it is unsure, it asks one short question; answer it in the same thread. To force this scenario, add a line `Scenario: traveler_sick`.

## Expected outcome

- **Transport:** S1 private taxi 14:00 to 18:30 (4,500 INR) and S2 state bus 15:15 to 21:00 (450 INR, seat not reserved), both CONFIRMED; S3 helicopter (95,000 INR) ADVERTISED ONLY and BLOCKED BY CAP.
- **Hotel:** release one room and take one person off the meal count from tonight's dinner, no charge if told by 18:00 (CONFIRMED).
- **Itinerary:** the plan for the other 19 is unchanged.
- **Room rule 2:** sending t07 back splits the group. The proposal must say so and ask Ragul to approve the split explicitly; nothing proceeds without it.
- **Proposal:** one plan, S1 taxi, 4,500 of 25,000 INR, split flagged for approval.
- **Organizer's change:** "use the 14:00 taxi, and I approve the split".
- **Travelers told:** one traveler is returning; everyone else's plan is unchanged. No name, no health details.

## Check it

- The coordinator answers in the trip room with one plain sentence (no scenario name, room id or tool name).
- A private channel **Parvati Traveler Disruption** appears; a traveler account cannot see it.
- The proposal calls out the split and asks you to approve it explicitly.
- Options over 25,000 INR are marked BLOCKED BY CAP and left out of the proposal (here: S3).
- coordinator-agent posts a handover note and releases `ops-desk`; support-agent assumes it and sends one proposal without being asked.
- After your final approval there is a line starting `Approval recorded:`, and the trip room gets the approved times only (no options, names or health details).
- On close: one note in the trip room, one summary in #pinewood-hq, and the room shows as archived in Switch Console.

Optional developer check (reads the local Switch database; assumes Switch Console's Windows layout, see `scripts/run_scenario.py`):

```text
python scripts/run_scenario.py --verify
```
