# Scenario: One traveler unwell and leaving the trip (`traveler_sick`)

_Synthetic sample data. Pinewood Holidays, the trip, people and suppliers are fictional. Logistics only: no medical details or advice._

The switchboard opens a private room **Parvati Traveler Disruption** with the roles `ops-desk`, `transport`, `hotel`, `itinerary`.

## Messages to post (copy each one exactly)

Post one at a time and wait for the result before the next. First run of the day only: send `!reset @switchboard-agent` and `!reset @support-agent` in #parvati-trek.

1. In **#parvati-trek (new message)**:

   ```text
   @switchboard-agent Scenario: traveler_sick. Message from guide Tenzin, Day 3, 11:20: traveler t07 is unwell and wants to stop the trip and go back to Manali today. They are resting at Riverbend Camp. No medical details are shared here; the organizer is in touch with them directly. Open the disruption room as your instructions describe.
   ```

   Wait for: the private channel 'Parvati Traveler Disruption' opens; the specialists answer; switchboard posts a handover note and releases ops-desk; support-agent assumes it and sends you one proposal (no message from you needed).

2. In **'Parvati Traveler Disruption'**:

   ```text
   @ops-desk Approved with one change: use the 14:00 taxi, and I approve the split: t07 returns to Manali, the other 19 continue. Re-check it before I give final approval.
   ```

   Wait for: the re-checked proposal.

3. In **'Parvati Traveler Disruption'**:

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

- **Transport:** S1 private taxi 14:00 to 18:30 (4,500 INR) and S2 state bus 15:15 to 21:00 (450 INR, seat not reserved), both CONFIRMED; S3 helicopter (95,000 INR) ADVERTISED ONLY and BLOCKED BY CAP.
- **Hotel:** release one room and take one person off the meal count from tonight's dinner, no charge if told by 18:00 (CONFIRMED).
- **Itinerary:** the plan for the other 19 is unchanged.
- **Room rule 2:** sending t07 back splits the group. The proposal must say so and ask Anita to approve the split explicitly; nothing proceeds without it.
- **Proposal:** one plan, S1 taxi, 4,500 of 25,000 INR, split flagged for approval.
- **Organizer's change:** "use the 14:00 taxi, and I approve the split".
- **Travelers told:** one traveler is returning; everyone else's plan is unchanged. No name, no health details.

## Check it

```text
python scripts/run_scenario.py traveler_sick --verify
```

Run it with the Python inside the local Switch server (see `scripts/run_scenario.py`).
