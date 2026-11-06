# Scenario: Ten VIP guests arriving today (`vip_guests`)

_Synthetic sample data. Pinewood Holidays, Switch Summit 2026, the venue, the delegation, people and suppliers are fictional. Guest needs are counts only, never names._

coordinator-agent opens a private room **Summit VIP Arrival** with the roles `ops-desk`, `seating`, `catering`, `itinerary`.

## Messages to post (copy each one exactly)

Post one at a time and wait for the result before the next. First run of the day only: send `!reset @coordinator-agent` and `!reset @support-agent` in the attendee room.

1. In **the attendee room (#switch-summit)**:

   ```text
   @coordinator-agent A partner delegation of 10 VIP guests is joining us today. They need good seats together, they prefer vegetarian food, and we want to give them a welcome speech.
   ```

   Wait for: one plain sentence back in the attendee room; the private channel 'Summit VIP Arrival' opens; the specialists answer; coordinator-agent posts a handover note and releases ops-desk; support-agent assumes it and sends you one proposal (no message from you needed).

2. In **'Summit VIP Arrival'**:

   ```text
   @ops-desk Approved with one change: one of the ten guests is vegan, not vegetarian. Re-check it before I give final approval.
   ```

   Wait for: the re-checked proposal.

3. In **'Summit VIP Arrival'**:

   ```text
   @ops-desk Final approval: approved as re-checked. Record it and tell the attendees.
   ```

   Wait for: "Approval recorded" and support-agent's message to attendees in the attendee room.

4. In **the attendee room (#switch-summit)**:

   ```text
   @coordinator-agent The plan is approved and the attendees have been told. Please close the disruption room.
   ```

   Wait for: one closing note in the attendee room and one summary in #pinewood-hq.

## Other ways to say it

This scenario: At the Switch Summit conference, a partner delegation of 10 VIP guests arrives today at 09:00: they need seats together at the front, vegetarian lunches (the kitchen must be told), and a short welcome speech. The coordinator matches your own words to it, so any of these work as message 1:

- `@coordinator-agent We have 10 extra VIPs arriving at 09:00. Can you sort their seating, let the kitchen know they're vegetarian, and fit in a welcome?`
- `@coordinator-agent Ten VIP guests from a partner delegation are coming to the summit today: plan their seats, a veg lunch and a short welcome speech.`

If it is unsure, it asks one short question; answer it in the same thread. To force this scenario, add a line `Scenario: vip_guests`.

## Expected outcome

- **Seating:** V1 reserved VIP row of 12 chairs in front of row 1 in Hall A, ready 09:15, 34 front seats for 26 people, 6,000 INR, CONFIRMED. V2 row 2 (0 INR, CONFIRMED) seats them together but not at the front. V3 lounge sofas (72,000 INR) ADVERTISED ONLY and BLOCKED BY CAP.
- **Catering:** K1 10 extra lunches from the in-house kitchen, 4,500 INR, CONFIRMED, tell the kitchen by 10:00; K2 outside lunch boxes (18,000 INR) ADVERTISED ONLY. Draft kitchen note with counts only.
- **Itinerary:** a 5-minute welcome in Hall A that fits without moving any other session (for example just before the 09:30 keynote; the stage is ready from 09:00). venue-agent confirms the stage is free and the VIP row is set before the welcome. If a session has to move, the agenda says exactly what moves. A speech draft of at most 5 sentences for Ragul.
- **Proposal:** one plan, V1 and K1, 10,500 of 60,000 INR, every attendee and guest seated.
- **Organizer's change:** one guest is vegan; catering-agent re-checks: 9 vegetarian and 1 vegan from the same kitchen, same 4,500 INR.
- **Attendees told:** the welcome's time and place, and that the other sessions are unchanged (or exactly what moves); no names, diets or individual needs.
- **Open items for a person:** send the kitchen note by 10:00; who meets the guests at 09:00; review the speech.

## Check it

- The coordinator answers in the attendee room with one plain sentence (no scenario name, room id or tool name).
- A private channel **Summit VIP Arrival** appears; an attendee account cannot see it.
- Options over 60,000 INR are marked BLOCKED BY CAP and left out of the proposal (here: V3).
- coordinator-agent posts a handover note and releases `ops-desk`; support-agent assumes it and sends one proposal without being asked.
- After your final approval there is a line starting `Approval recorded:`, and the attendee room gets the approved times only (no options, names or individual needs).
- On close: one note in the attendee room, one summary in #pinewood-hq, and the room shows as archived in Switch Console.

Optional developer check (reads the local Switch database; assumes Switch Console's Windows layout, see `scripts/run_scenario.py`):

```text
python scripts/run_scenario.py --verify
```
