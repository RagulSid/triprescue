"""Run one TripRescue scenario: print what to post, check the start, verify the result.

Usage:
  python scripts/run_scenario.py --list
  python scripts/run_scenario.py <scenario>                    # print the messages to post (same as its README.md)
  python scripts/run_scenario.py --write-guides                # regenerate seed/scenarios/index.json and */README.md
  python scripts/run_scenario.py <scenario> --check            # clean-start check (local Switch database)
  python scripts/run_scenario.py [<scenario>] --verify         # verify the latest run (scenario inferred from the room if omitted)
  python scripts/run_scenario.py [<scenario>] --export DIR     # save the run's messages as evidence
  python scripts/run_scenario.py [<scenario>] --archive-channel  # archive the run's Mattermost channel

Optional developer tooling: --check, --verify, --export and --archive-channel. The demo and
scripts/setup.py never need them. They assume Switch Console's Windows layout (%APPDATA%\\switchdash).
--check, --verify and --export read the local Switch database (read-only) with the
credentials in Switch Console's switch-core.env, which are never printed. Run them
with the Python that ships with the local Switch server, because it has asyncpg:
  "%APPDATA%\\switchdash\\local-switch-server\\native\\switch-core\\<version>\\venv\\Scripts\\python.exe"
--archive-channel calls mmctl inside the bundled Mattermost container (docker).

This script posts nothing and books nothing. A person posts each message in Mattermost.
"""
import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ROOT / "seed" / "scenarios"
ENV = Path(os.path.expandvars(r"%APPDATA%\switchdash\local-switch-server\native\run\switch-core.env"))
ROLE_AGENT = {"transport": "transport-agent", "hotel": "hotel-agent", "itinerary": "itinerary-agent"}
COORDINATOR = "coordinator-agent"  # opens, hands over and closes disruption rooms
INDEX = SCENARIOS / "index.json"
TRIP_LABEL = "the trip room (#parvati-trek, or your Telegram group)"


def load_rooms(root=ROOT):
    """Exact Switch names of the trip and HQ rooms: rooms/rooms.json, overridden by the
    gitignored rooms/rooms.local.json when it exists (e.g. a Telegram trip room)."""
    rooms = json.loads((root / "rooms" / "rooms.json").read_text(encoding="utf-8"))
    local = root / "rooms" / "rooms.local.json"
    if local.is_file():
        rooms.update(json.loads(local.read_text(encoding="utf-8")))
    return rooms


ROOMS = load_rooms()
TRIP, HQ = ROOMS["trip_room"], ROOMS["hq_room"]
IST = timezone(timedelta(hours=5, minutes=30))


def load_scenario(name):
    path = SCENARIOS / name / "scenario.json"
    if not path.is_file():
        names = ", ".join(sorted(p.name for p in SCENARIOS.iterdir() if p.is_dir()))
        sys.exit(f"Unknown scenario '{name}'. Available: {names}")
    return json.loads(path.read_text(encoding="utf-8"))


def messages(s):
    """The exact messages a person posts, in order: (where, text, wait-for)."""
    return [
        (TRIP_LABEL,
         f"@{COORDINATOR} {s['trigger']['examples'][0]}",
         f"one plain sentence back in the trip room; the private channel '{s['room_name']}' opens; the specialists answer; "
         f"{COORDINATOR} posts a handover note and releases ops-desk; support-agent assumes it and sends you one proposal "
         "(no message from you needed)"),
        (f"'{s['room_name']}'",
         f"@ops-desk Approved with one change: {s['organizer_change'][0].lower()}{s['organizer_change'][1:]} Re-check it before I give final approval.",
         "the re-checked proposal"),
        (f"'{s['room_name']}'", "@ops-desk Final approval: approved as re-checked. Record it and tell the travelers.",
         "\"Approval recorded\" and support-agent's message to travelers in the trip room"),
        (TRIP_LABEL,
         f"@{COORDINATOR} The plan is approved and the travelers have been told. Please close the disruption room.",
         "one closing note in the trip room and one summary in #pinewood-hq"),
    ]


def build_index():
    """seed/scenarios/index.json: what the coordinator reads to match an organizer's own words to a scenario."""
    rows = []
    for p in sorted(SCENARIOS.iterdir()):
        if p.is_dir():
            s = load_scenario(p.name)
            rows.append({"name": s["name"], "title": s["title"], **s["trigger"]})
    return {"_note": "Generated from seed/scenarios/*/scenario.json by scripts/run_scenario.py --write-guides; do not edit. "
                     "Synthetic sample data.", "scenarios": rows}


def render_guide(s):
    """README.md for a scenario folder: copy-paste messages first, then the expected outcome."""
    out = [f"# Scenario: {s['title']} (`{s['name']}`)", "", f"_{s['_note']}_", "",
           f"{COORDINATOR} opens a private room **{s['room_name']}** with the roles "
           + ", ".join(f"`{r}`" for r in s["roles"]) + ".", "",
           "## Messages to post (copy each one exactly)", "",
           "Post one at a time and wait for the result before the next. "
           f"First run of the day only: send `!reset @{COORDINATOR}` and `!reset @support-agent` in the trip room.", ""]
    for i, (where, text, wait) in enumerate(messages(s), 1):
        out += [f"{i}. In **{where}**:", "", "   ```text", f"   {text}", "   ```", "", f"   Wait for: {wait}.", ""]
    out += ["## Other ways to say it", "",
            f"This scenario: {s['trigger']['description']} The coordinator matches your own words to it, so any of these work as message 1:", ""]
    out += [f"- `@{COORDINATOR} {e}`" for e in s["trigger"]["examples"][1:]]
    out += ["", "If it is unsure, it asks one short question; answer it in the same thread. "
            f"To force this scenario, add a line `Scenario: {s['name']}`.", ""]
    blocked = ", ".join(s["expected"]["blocked_by_cap"]) or "none"
    by_eye = [
        "The coordinator answers in the trip room with one plain sentence (no scenario name, room id or tool name).",
        f"A private channel **{s['room_name']}** appears; a traveler account cannot see it.",
        f"Options over 25,000 INR are marked BLOCKED BY CAP and left out of the proposal (here: {blocked}).",
        f"{COORDINATOR} posts a handover note and releases `ops-desk`; support-agent assumes it "
        "and sends one proposal without being asked.",
        "After your final approval there is a line starting `Approval recorded:`, and the trip room gets "
        "the approved times only (no options, names or health details).",
        "On close: one note in the trip room, one summary in #pinewood-hq, and the room shows as archived in Switch Console.",
    ]
    if s["expected"]["split_needs_approval"]:
        by_eye.insert(2, "The proposal calls out the split and asks you to approve it explicitly.")
    out += ["## Expected outcome", ""] + [f"- {n}" for n in s["expected"]["notes"]] + [
        "", "## Check it", ""] + [f"- {line}" for line in by_eye] + [
        "", "Optional developer check (reads the local Switch database; assumes Switch Console's Windows layout, "
        "see `scripts/run_scenario.py`):", "", "```text", "python scripts/run_scenario.py --verify", "```", ""]
    return "\n".join(out)


def write_guides():
    INDEX.write_text(json.dumps(build_index(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {INDEX.relative_to(ROOT).as_posix()}")
    for p in sorted(SCENARIOS.iterdir()):
        if p.is_dir():
            (p / "README.md").write_text(render_guide(load_scenario(p.name)), encoding="utf-8")
            print(f"wrote {(p / 'README.md').relative_to(ROOT).as_posix()}")


def print_steps(s):
    print(render_guide(s))


# ---------- database (read-only) ----------

def env():
    if not ENV.is_file():
        sys.exit(f"Switch Console's switch-core.env not found at {ENV}. Is the local Switch server installed?")
    cfg = {}
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            cfg[k] = v
    return cfg


async def query(fn):
    try:
        import asyncpg
    except ImportError:
        sys.exit("asyncpg is missing: run this with the Python inside the local Switch server (see the docstring).")
    c = env()
    conn = await asyncpg.connect(host=c["DB_HOST"], port=int(c["DB_PORT"]), user=c["DB_OWNER_USER"],
                                 password=c["DB_OWNER_PASSWORD"], database="switch")
    try:
        async with conn.transaction(readonly=True):
            return await fn(conn)
    finally:
        await conn.close()


async def named_rooms(conn, name):
    return await conn.fetch("select id, name from rooms where name=$1 and archived_at is null", name)


async def check(conn, s):
    ok = True
    for name in (TRIP, HQ):
        rows = await named_rooms(conn, name)
        good = len(rows) == 1
        ok &= good
        print(f"{'PASS' if good else 'FAIL'}  exactly one active room named {name!r} (found {len(rows)})")
    open_rooms = await named_rooms(conn, s["room_name"])
    good = not open_rooms
    ok &= good
    print(f"{'PASS' if good else 'FAIL'}  no open {s['room_name']!r} room (found {len(open_rooms)})")
    leases = await conn.fetch("select a.name from role_leases l join agents a on a.id=l.agent_id")
    good = not leases
    ok &= good
    print(f"{'PASS' if good else 'FAIL'}  no role held anywhere ({', '.join(r['name'] for r in leases) or 'none'})")
    agents = {r["name"] for r in await conn.fetch("select name from agents")}
    need = {COORDINATOR, "support-agent"} | {ROLE_AGENT[r] for r in s["roles"] if r in ROLE_AGENT}
    good = need <= agents
    ok &= good
    print(f"{'PASS' if good else 'FAIL'}  agents registered: {', '.join(sorted(need))}" + ("" if good else f" (missing {', '.join(sorted(need - agents))})"))
    members = {r["name"] for r in await conn.fetch(
        "select a.name from room_agents ra join agents a on a.id=ra.agent_id join rooms r on r.id=ra.room_id "
        "where r.name=$1 and r.archived_at is null", TRIP)}
    good = {COORDINATOR, "support-agent"} <= members
    ok &= good
    print(f"{'PASS' if good else 'FAIL'}  {COORDINATOR} and support-agent are in {TRIP}")
    return ok


async def latest_run(conn, s, since):
    room = await conn.fetchrow(
        "select * from rooms where name=$1 and created_at >= $2 order by created_at desc limit 1", s["room_name"], since)
    if room is None:
        sys.exit(f"No room named {s['room_name']!r} created since {since:%Y-%m-%d %H:%M} UTC.")
    trip = (await conn.fetchrow("select id from rooms where name=$1 and archived_at is null", TRIP))["id"]
    hq = (await conn.fetchrow("select id from rooms where name=$1 and archived_at is null", HQ))["id"]
    # The trigger is the organizer's own message to the coordinator in the trip room: the last one before the room
    # opened, or, if the coordinator asked a clarifying question first, the message that question answered. Only
    # messages after the previous disruption room closed (and at most 30 minutes before this one opened) count.
    previous = await conn.fetchval(
        "select max(archived_at) from rooms where name = any($1::text[]) and archived_at < $2",
        all_room_names(), room["created_at"])
    lower = max(previous or room["created_at"] - timedelta(minutes=30), room["created_at"] - timedelta(minutes=30))
    asks = await conn.fetch(
        "select sent_at, body from messages where room_id=$1 and sent_at > $2 and sent_at <= $3 "
        "and event_type='m.room.message' and sender_name not like '%-agent' and sender_name not in ('admin', 'switch-admin') "
        "and body ilike $4 order by sent_at desc", trip, lower, room["created_at"], f"%@{COORDINATOR}%")
    notice = asks[0] if asks else None
    for earlier in asks[1:]:
        question = await conn.fetchval(
            "select count(*) from messages where room_id=$1 and sender_name=$2 and body like '%?%' "
            "and sent_at > $3 and sent_at < $4", trip, COORDINATOR, earlier["sent_at"], notice["sent_at"])
        if not question:
            break
        notice = earlier
    return room, trip, hq, notice


def all_room_names():
    return [load_scenario(p.name)["room_name"] for p in sorted(SCENARIOS.iterdir()) if p.is_dir()]


async def infer_scenario(conn, since):
    """The scenario of the latest disruption room created since `since`, from its room name."""
    by_room = {load_scenario(p.name)["room_name"]: p.name for p in SCENARIOS.iterdir() if p.is_dir()}
    row = await conn.fetchrow("select name, created_at from rooms where name = any($1::text[]) and created_at >= $2 "
                              "order by created_at desc limit 1", list(by_room), since)
    if row is None:
        sys.exit(f"No disruption room created since {since:%Y-%m-%d %H:%M} UTC.")
    return by_room[row["name"]]


# Words travelers should never see in the trip room.
TECHNICAL = re.compile(r"\b(?=[0-9a-f]*\d)[0-9a-f]{8}\b|mcp__|ops-desk|`|\bScenario:|\b("
                       + "|".join(sorted(p.name for p in SCENARIOS.iterdir() if p.is_dir())) + r")\b", re.I)


async def verify(conn, s, since, named=False):
    room, trip, hq, notice = await latest_run(conn, s, since)
    rid = room["id"]
    end = (room["archived_at"] or datetime.now(timezone.utc)) + timedelta(minutes=5)
    results = []

    def res(ok, text):
        results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {text}")

    print(f"Room {rid} {room['name']!r}, created {room['created_at'].astimezone(IST):%H:%M:%S} IST")
    if named:
        latest = await infer_scenario(conn, since)
        res(latest == s["name"], f"latest disruption room is this scenario's ({latest})")
    res(notice is not None, f"organizer's message to {COORDINATOR} found in {TRIP}"
        + (f" at {notice['sent_at'].astimezone(IST):%H:%M:%S} IST: {notice['body'][:70]!r}" if notice else ""))
    res(room["channel_type"] == "channel_private", f"private channel ({room['channel_type']})")
    instructions_ok = (room["instructions"] or "").startswith((ROOT / "rooms" / "parvati-disruption.md").read_text(encoding="utf-8").strip()[:200])
    res(instructions_ok and s["title"] in (room["instructions"] or ""), "instructions = room file + this scenario's section")
    agents = {r["name"] for r in await conn.fetch(
        "select a.name from room_agents ra join agents a on a.id=ra.agent_id where ra.room_id=$1", rid)}
    need = {COORDINATOR, "support-agent"} | {ROLE_AGENT[r] for r in s["roles"] if r in ROLE_AGENT}
    res(need <= agents, f"agents: {', '.join(sorted(agents))}")
    roles = {r["name"]: r["exclusive"] for r in await conn.fetch("select name, exclusive from room_roles where room_id=$1", rid)}
    res(set(roles) == set(s["roles"]) and roles.get("ops-desk") is True and not any(v for k, v in roles.items() if k != "ops-desk"),
        f"roles: {', '.join(k + ('*' if v else '') for k, v in sorted(roles.items()))} (* = exclusive)")
    links = {(r["target_room_id"], r["label"]) for r in await conn.fetch(
        "select target_room_id, label from room_links where source_room_id=$1", rid)}
    res(links == {(trip, "parent trip"), (hq, "escalation")}, f"links: {', '.join(sorted(l for _, l in links))}")
    refs = await conn.fetchval("select count(*) from room_references where room_id=$1", rid)
    res(refs >= 1, f"supplier sheet reference attached ({refs})")
    approval = await conn.fetchrow(
        "select sent_at, sender_name from messages where room_id=$1 and body ilike '%approval recorded%' order by sent_at limit 1", rid)
    res(approval is not None, "approval recorded in the room" + (f" by {approval['sender_name']}" if approval else ""))
    told = await conn.fetch(
        "select sent_at, body from messages where room_id=$1 and sender_name='support-agent' and sent_at >= $2 and sent_at <= $3",
        trip, approval["sent_at"] if approval else end, end)
    res(len(told) >= 1, f"travelers told in {TRIP} by support-agent ({len(told)} message)")
    res(room["archived_at"] is not None, "room archived" + (f" at {room['archived_at'].astimezone(IST):%H:%M:%S} IST" if room["archived_at"] else ""))
    leases = await conn.fetchval("select count(*) from role_leases where room_id=$1", rid)
    res(leases == 0, f"no role still held in the room ({leases})")
    start = room["created_at"]
    closed = room["archived_at"] or end
    hq_sql = (f"select body from messages where room_id=$1 and sender_name='{COORDINATOR}' and sent_at between $2 and $3 "
              "and body not ilike 'Starting a session%' and body not ilike 'Already closed%'")
    # The open report comes before the organizer's approval; a later post (e.g. a close-out on hold) is not it.
    hq_open = await conn.fetch(hq_sql, hq, start, approval["sent_at"] if approval else closed)
    hq_posts = await conn.fetch(hq_sql, hq, closed, end)
    trip_notes = await conn.fetch(
        f"select body from messages where room_id=$1 and sender_name='{COORDINATOR}' and sent_at between $2 and $3 "
        "and body not ilike 'Starting a session%' and body not ilike 'Already closed%' and body ilike '%closed%'",
        trip, approval["sent_at"] if approval else start, end)
    res(len(hq_open) == 1, f"room details posted once in {HQ} when the room opened ({len(hq_open)})")
    res(len(hq_posts) == 1, f"close-out posted once in {HQ} after the archive ({len(hq_posts)})")
    res(len(trip_notes) == 1, f"close-out note posted once in {TRIP} ({len(trip_notes)})")
    agent_posts = await conn.fetch(
        "select body from messages where room_id=$1 and sender_name like '%-agent' and event_type='m.room.message' "
        "and sent_at between $2 and $3", trip, notice["sent_at"] if notice else start, end)
    leaks = [m.group(0) for r in agent_posts for m in [TECHNICAL.search(r["body"] or "")] if m]
    res(not leaks, f"trip room posts in plain words, no ids, scenario names or tool names ({len(agent_posts)} posts"
        + (f"; found {leaks}" if leaks else "") + ")")
    questions = await conn.fetchval(
        "select count(*) from messages where room_id=$1 and sender_name=$2 and body like '%?%' and sent_at between $3 and $4",
        trip, COORDINATOR, notice["sent_at"] if notice else start, start)
    print(f"INFO  clarifying questions from {COORDINATOR} before the room opened: {questions}")
    first = notice["sent_at"] if notice else start
    sessions = await conn.fetch(
        "select sender_name, count(*) from messages where body ilike 'Starting a session%' and sent_at between $1 and $2 group by 1",
        first, end)
    if room["archived_at"]:
        print(f"INFO  elapsed, notice to archive: {room['archived_at'] - first}")
    print(f"INFO  agent sessions started: {sum(r['count'] for r in sessions)} "
          f"({', '.join(f'{r[0]} {r[1]}' for r in sessions)})")
    print_models(first, end)
    print(f"\n{sum(results)}/{len(results)} checks passed")
    return all(results)


def print_models(start, end):
    """Which model each agent's Claude Code sessions used in the window (from local transcripts)."""
    base = Path.home() / ".claude" / "projects"
    found = {}
    for d in base.glob("*agents-*-agent"):
        agent = re.search(r"agents-(.+-agent)$", d.name).group(1)
        for f in d.glob("*.jsonl"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime, timezone.utc)
            if not (start <= mtime <= end + timedelta(minutes=30)):
                continue
            found.setdefault(agent, set()).update(re.findall(r'"model":"(claude[^"]+)"', f.read_text(encoding="utf-8", errors="ignore")))
    if found:
        print("INFO  models: " + "; ".join(f"{a} {','.join(sorted(m))}" for a, m in sorted(found.items())))


async def export(conn, s, since, out):
    room, trip, hq, notice = await latest_run(conn, s, since)
    start = (notice["sent_at"] if notice else room["created_at"]) - timedelta(minutes=1)
    end = (room["archived_at"] or datetime.now(timezone.utc)) + timedelta(minutes=5)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for rid, label in ((room["id"], s["room_name"]), (trip, TRIP), (hq, HQ)):
        rows = await conn.fetch("select sent_at, sender_name, body from messages where room_id=$1 and body <> '' "
                                "and sent_at between $2 and $3 order by sent_at", rid, start, end)
        path = out / f"{s['name']}-{re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')}.md"
        with path.open("w", encoding="utf-8") as f:
            f.write(f"# {label} ({rid})\n\n")
            for r in rows:
                f.write(f"### {r['sent_at'].astimezone(IST):%H:%M:%S} IST · {r['sender_name']}\n\n{r['body']}\n\n")
        print(f"wrote {path} ({len(rows)} messages)")


# ---------- Mattermost channel ----------

def archive_channel(s, since):
    async def channel(conn):
        room, *_ = await latest_run(conn, s, since)
        return room["external_channel_id"], room["archived_at"]
    channel_id, archived = asyncio.run(query(channel))
    if archived is None:
        sys.exit("The Switch room is not archived yet; close it first.")
    ps = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True)
    names = [n for n in ps.stdout.split() if n.endswith("mattermost-mattermost-1")]
    if len(names) != 1:
        sys.exit(f"Expected one Mattermost container, found: {names}")
    team = subprocess.run(["docker", "exec", names[0], "mmctl", "--local", "team", "list"], capture_output=True, text=True).stdout.split()
    if len(team) != 1:
        sys.exit(f"Expected one Mattermost team, found: {team}")
    r = subprocess.run(["docker", "exec", names[0], "mmctl", "--local", "channel", "archive", f"{team[0]}:{channel_id}"],
                       capture_output=True, text=True)
    print((r.stdout + r.stderr).strip() or f"archived Mattermost channel {channel_id}")
    sys.exit(r.returncode)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenario", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--write-guides", action="store_true", help="regenerate seed/scenarios/*/README.md from scenario.json")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--export", metavar="DIR")
    ap.add_argument("--archive-channel", action="store_true")
    ap.add_argument("--since", default=None, help="only consider runs since this ISO time (default: last 24 hours)")
    a = ap.parse_args()
    if a.list:
        for p in sorted(SCENARIOS.iterdir()):
            if p.is_dir():
                print(f"{p.name:20} {load_scenario(p.name)['title']}")
        return 0
    if a.write_guides:
        write_guides()
        return 0
    since = datetime.fromisoformat(a.since.replace("Z", "+00:00")) if a.since else datetime.now(timezone.utc) - timedelta(days=1)
    uses_db = a.verify or a.export or a.archive_channel
    if not a.scenario:
        if not uses_db:
            ap.error("name a scenario, or use --list")
        a_name = asyncio.run(query(lambda c: infer_scenario(c, since)))
        print(f"Latest run: {a_name} (inferred from the disruption room)")
    s = load_scenario(a.scenario or a_name)
    if a.check:
        return 0 if asyncio.run(query(lambda c: check(c, s))) else 1
    if a.verify:
        return 0 if asyncio.run(query(lambda c: verify(c, s, since, named=bool(a.scenario)))) else 1
    if a.export:
        asyncio.run(query(lambda c: export(c, s, since, a.export)))
        return 0
    if a.archive_channel:
        archive_channel(s, since)
    print_steps(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
