# Room instructions: Parvati Disruption

**Chat app:** Mattermost (created by `switchboard-agent` when a cancellation arrives)
Slack and Telegram are planned later; room rules do not depend on the chat app.
**Links:** Parvati Trek (parent trip), Pinewood HQ (escalation)
**Members:** the organizer (Anita), the ops-desk holder and the specialists (`transport-agent`, `hotel-agent`, `itinerary-agent`)
**Reference:** the supplier sheet (`seed/supplier_sheet.json`)

This room exists to fix one disruption. Specialists work from the supplier sheet, the ops desk assembles one proposal, and the organizer approves it. When the plan is approved and travelers are told, the room is archived and a summary is posted to Pinewood HQ and Parvati Trek.

## Room rules

1. Contingency cap: 25,000 INR per disruption. Every agent checks cost against the cap. An option that costs more is BLOCKED BY CAP: say so with the numbers, and never put it in a proposal.
2. Keep the group together unless the organizer approves a split.
3. Agents propose; the organizer approves. No agent books, pays or sends a booking request. A booking request is a draft for the organizer.
4. Label every transport or hotel option CONFIRMED (it is in the supplier sheet) or ADVERTISED ONLY (it came from search). Never present an advertised option as confirmed.

## Working agreement

- Answer from the supplier sheet and this room's history. If a fact is not there, say so; do not guess.
- Check knock-on effects (later bookings, guide time, next-day departures) before anything goes to the organizer.
- Ask another specialist with a targeted message, not a general post.
- The organizer sees one proposal, not a list of options.
- Hand the ops-desk role over with `release_role`, then `assume_role`. A new holder reads `list_roles` and this room's history before continuing.
