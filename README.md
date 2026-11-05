# TripRescue

> Every disruption has another route.

**Work in progress.** Built for the Flip the Switch Hackathon (Nov 4 to 7, 2026). This README is filled in as each part is built and tested.

## The problem

A group trip runs on a chain of bookings. When one supplier cancels at 6:52 in the morning, the organizer has a few hours to find new transport, keep the hotel and guide in step, stay inside the budget and tell twenty travelers what happens next, usually by phoning around and juggling chat threads.

## What TripRescue does

A team of AI agents and people rescues the trip inside Switch rooms. When a coach is cancelled:

1. A disruption room opens, linked to the trip room and to the operator's HQ.
2. Transport, hotel and itinerary specialists work in parallel from one supplier sheet.
3. A room rule blocks any option over the contingency cap.
4. If the agent running the ops desk drops out, another agent takes the role and continues from the room history.
5. The organizer gets one proposal and approves it. No agent books or pays.
6. Travelers are told on Telegram, and the room is archived with a summary.

## How Switch is used

*To be completed once the flow runs end to end.*

| Switch feature | Where TripRescue uses it |
| --- | --- |
| Rooms | Pinewood HQ (Slack), Parvati Trek (Telegram), Parvati Disruption (Slack) |
| Room instructions | The four rules in [`rooms/`](rooms/) |
| Roles | ops-desk, transport, hotel, itinerary, budget ([`rooms/roles/`](rooms/roles/)) |
| Linked rooms | The disruption room links to the trip (parent) and HQ (escalation) |
| Human approval | The organizer approves the single proposal |

## Agents

*To be completed.* Planned: `switchboard-agent`, `support-agent`, `transport-agent`, `hotel-agent`, `itinerary-agent`, `budget-agent`, all Claude Code agents run through Switch Console.

## Setup

Requirements: Docker Desktop, [Switch Console](https://docs.switchagents.ai/switch-rooms/getting-started/install-switch-console), Claude Code (signed in), Python 3.10+, a Slack workspace where you can install a custom app, and a Telegram bot.

```bash
cp .env.example .env      # then fill in the values
python scripts/setup.py   # checks Python, seed data, Docker, Claude Code and .env
python -m unittest discover tests
```

On Windows, if agents answer in Switch Console but never in Mattermost, see [WINDOWS.md](WINDOWS.md).

*Channel setup and run steps to be completed.*

## Sample data

Everything in [`seed/`](seed/) is synthetic. Pinewood Holidays, the Parvati Valley Trek, the travelers, the suppliers and all prices are fictional. Emails use the reserved `example.com` domain. Option C stands in for a web search result and is labeled ADVERTISED ONLY.

## What is mocked

- Supplier availability and prices come from the seeded sheet, not live systems.
- Nothing is booked or paid. Any booking request is a draft for the organizer to send.

## Third-party components

- [Switch](https://github.com/sandbox-quantum/switch) and Switch Console run the rooms and agents; they are installed separately, not vendored here.
- Claude Code powers the agents.
- The scripts and tests use only the Python standard library.

## Licence

[MIT](LICENSE)
