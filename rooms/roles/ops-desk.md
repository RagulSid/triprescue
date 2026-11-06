# Role: ops-desk

**Holders:** one agent at a time (exclusive). `coordinator-agent` takes it when it opens the room and collects the specialists' answers; then it hands the desk to `support-agent`, which writes the proposal and tells the travelers.
**Room:** any Parvati disruption room (named by the scenario)

## Job

- Kick off the specialists (transport, hotel, itinerary) and collect their answers.
- Check the total cost against the room's 25,000 INR cap (there is no budget agent).
- When every specialist has answered, the setting-up holder hands over (see below); the new holder assembles one proposal that fits the room rules and sends it to the organizer.
- Handle the organizer's changes, ask the affected specialist to re-check, and resend.
- Record the organizer's approval in the room.

## Handing over

The holder posts a handover note (done, open, next step), calls `release_role`, and tells the next holder the role is free. Switch does not reassign a role on its own; the hand-over is always these explicit steps.

## When you take over

Call `list_roles`, then `assume_role("ops-desk")`. Read the room history from the handover note back. Continue from the last open step; do not restart work that is already done.
