# Switch Console setup: agents and rooms

Everything to type into Switch Console, field by field: seven agents and three base rooms. Disruption rooms are created by `coordinator-agent`, not by hand.

`<clone>` is the folder you cloned this repo into (for example `C:\Users\you\triprescue`).

## Agents

Switch Console: **Your Agents** → the **+** card. Fill in one form per agent, then **Add agent**. Leave the model alone in Console: it comes from each folder's `.claude/settings.json`.

### coordinator-agent

| Field | Value |
| --- | --- |
| Name | `coordinator-agent` |
| Description | Opens, links and archives disruption rooms for Pinewood Holidays. |
| Agent instructions | Follow CLAUDE.md in your directory. Act only on requests in a room; stop and post the exact error if a Switch tool fails. |
| Run location | This computer |
| Directory | `<clone>\agents\coordinator-agent` |
| Agent provider | Claude Code (model `claude-sonnet-5-5` from `.claude/settings.json`) |
| Who can talk to your agent | Default: you and your agents |

### support-agent

| Field | Value |
| --- | --- |
| Name | `support-agent` |
| Description | Answers Parvati Valley Trek travelers from the trip plan; never guesses. |
| Agent instructions | Follow CLAUDE.md in your directory. |
| Run location | This computer |
| Directory | `<clone>\agents\support-agent` |
| Agent provider | Claude Code (model `claude-sonnet-5-5` from `.claude/settings.json`) |
| Who can talk to your agent | Anyone (travelers and attendees must reach it) |

### transport-agent

| Field | Value |
| --- | --- |
| Name | `transport-agent` |
| Description | Finds replacement transport from the supplier sheet; labels CONFIRMED or ADVERTISED ONLY. |
| Agent instructions | Follow CLAUDE.md in your directory. Reply only when addressed; take facts only from the seed files and the room. |
| Run location | This computer |
| Directory | `<clone>\agents\transport-agent` |
| Agent provider | Claude Code (model `claude-haiku-5-5` from `.claude/settings.json`) |
| Who can talk to your agent | Default: you and your agents |

### hotel-agent

| Field | Value |
| --- | --- |
| Name | `hotel-agent` |
| Description | Checks late check-in and dinner holds from the supplier sheet. |
| Agent instructions | Follow CLAUDE.md in your directory. Reply only when addressed; take facts only from the seed files and the room. |
| Run location | This computer |
| Directory | `<clone>\agents\hotel-agent` |
| Agent provider | Claude Code (model `claude-haiku-5-5` from `.claude/settings.json`) |
| Who can talk to your agent | Default: you and your agents |

### itinerary-agent

| Field | Value |
| --- | --- |
| Name | `itinerary-agent` |
| Description | Rebuilds the day and checks knock-on effects with the transport agent. |
| Agent instructions | Follow CLAUDE.md in your directory. Reply only when addressed; take facts only from the seed files and the room. |
| Run location | This computer |
| Directory | `<clone>\agents\itinerary-agent` |
| Agent provider | Claude Code (model `claude-sonnet-5-5` from `.claude/settings.json`) |
| Who can talk to your agent | Default: you and your agents |

### venue-agent

| Field | Value |
| --- | --- |
| Name | `venue-agent` |
| Description | Finds seating for Switch Summit sessions from the venue sheet; labels CONFIRMED or ADVERTISED ONLY. |
| Agent instructions | Follow CLAUDE.md in your directory. Reply only when addressed; take facts only from the seed files and the room. |
| Run location | This computer |
| Directory | `<clone>\agents\venue-agent` |
| Agent provider | Claude Code (model `claude-haiku-5-5` from `.claude/settings.json`) |
| Who can talk to your agent | Default: you and your agents |

### catering-agent

| Field | Value |
| --- | --- |
| Name | `catering-agent` |
| Description | Finds meals for Switch Summit changes and drafts the kitchen note (counts only); labels CONFIRMED or ADVERTISED ONLY. |
| Agent instructions | Follow CLAUDE.md in your directory. Reply only when addressed; take facts only from the seed files and the room. |
| Run location | This computer |
| Directory | `<clone>\agents\catering-agent` |
| Agent provider | Claude Code (model `claude-haiku-5-5` from `.claude/settings.json`) |
| Who can talk to your agent | Default: you and your agents |

## Rooms

Switch Console: **Your Rooms** → **Create room**, messaging app **Mattermost**. The names must match exactly: `coordinator-agent` finds rooms by the names in `rooms/rooms.json`. For the instructions, paste the whole file.

### Pinewood HQ

| Field | Value |
| --- | --- |
| Name | `Pinewood HQ` |
| Messaging app | Mattermost |
| Description | Pinewood Holidays home base: disruption summaries and escalations. |
| Agents | `coordinator-agent` |
| Instructions | Paste the whole of [`rooms/pinewood-hq.md`](rooms/pinewood-hq.md) |
| Channel | Public |

### Parvati Trek

| Field | Value |
| --- | --- |
| Name | `Parvati Trek` |
| Messaging app | Mattermost |
| Description | Parvati Valley Trek: travelers and the support agent. |
| Agents | `support-agent`, `coordinator-agent` |
| Instructions | Paste the whole of [`rooms/parvati-trek.md`](rooms/parvati-trek.md) |
| Channel | Public |

### Switch Summit

| Field | Value |
| --- | --- |
| Name | `Switch Summit` |
| Messaging app | Mattermost |
| Description | Switch Summit 2026: conference attendees and the support agent. |
| Agents | `support-agent`, `coordinator-agent` |
| Instructions | Paste the whole of [`rooms/switch-summit.md`](rooms/switch-summit.md) |
| Channel | Public |

## Check

- In each room, `!list-agents` lists the agents above.
- In `#pinewood-hq`, `@coordinator-agent hello` gets a reply.
- A room made in Mattermost instead of Console gets the Switch name `Mattermost: <channel>`. Put that exact name in a gitignored `rooms/rooms.local.json`, for example `{"summit_room": "Mattermost: Switch Summit"}`.
