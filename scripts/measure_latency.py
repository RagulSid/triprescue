"""Measure agent reply latency in one Switch room (read-only).

For every message addressed to an agent in the room, report:
  ack    seconds until that agent's first post (often "Starting a session")
  answer seconds until its first substantive post (not the session or role notice)

Reads the local Switch database with the credentials in Switch Console's
switch-core.env. Nothing is written and no credential is printed.
Run it with the Python that ships with the local Switch server (it has asyncpg):

  "%APPDATA%\\switchdash\\local-switch-server\\native\\switch-core\\<version>\\venv\\Scripts\\python.exe" \
      scripts/measure_latency.py <room-id> [--since 2026-11-05T12:00:00Z]
"""
import argparse
import asyncio
import os
import statistics
from datetime import datetime

import asyncpg

ENV = os.path.expandvars(r"%APPDATA%\switchdash\local-switch-server\native\run\switch-core.env")
NOISE = ("Starting a session", "🎭")


def load_env():
    cfg = {}
    with open(ENV, encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.rstrip("\n").split("=", 1)
                cfg[k] = v
    return cfg


async def main(room_id, since):
    c = load_env()
    conn = await asyncpg.connect(host=c["DB_HOST"], port=int(c["DB_PORT"]), user=c["DB_OWNER_USER"],
                                 password=c["DB_OWNER_PASSWORD"], database="switch")
    try:
        async with conn.transaction(readonly=True):
            events = await conn.fetch(
                "select e.created_at, a.name as agent, e.payload->'payload'->>'sender_name' as sender, "
                "left(e.payload->'payload'->>'body', 40) as body from agent_events e "
                "join agents a on a.id=e.agent_id where e.room_id=$1 and e.type='message' "
                "and e.payload->'payload'->>'addressed'='true' and e.created_at >= $2 order by e.created_at",
                room_id, since)
            posts = await conn.fetch(
                "select sent_at, sender_name, body from messages where room_id=$1 and body <> '' "
                "and sent_at >= $2 order by sent_at", room_id, since)
    finally:
        await conn.close()

    per_agent = {}
    print(f"{'asked at (UTC)':<15}{'from':<19}{'to':<19}{'ack s':>7}{'answer s':>10}  asked")
    for i, e in enumerate(events):
        # The window ends at the next message addressed to the same agent.
        nxt = next((x["created_at"] for x in events[i + 1:] if x["agent"] == e["agent"]), None)
        mine = [p for p in posts if p["sender_name"] == e["agent"] and p["sent_at"] > e["created_at"]
                and (nxt is None or p["sent_at"] <= nxt)]
        ack = mine[0]["sent_at"] if mine else None
        ans = next((p["sent_at"] for p in mine if not p["body"].startswith(NOISE)), None)
        a_s = (ack - e["created_at"]).total_seconds() if ack else None
        n_s = (ans - e["created_at"]).total_seconds() if ans else None
        if n_s is not None:
            per_agent.setdefault(e["agent"], []).append(n_s)
        fmt = lambda v: f"{v:.0f}" if v is not None else "-"
        print(f"{e['created_at']:%H:%M:%S}       {str(e['sender'])[:18]:<19}{e['agent'][:18]:<19}"
              f"{fmt(a_s):>7}{fmt(n_s):>10}  {e['body']!r}")
    print("\nper agent: answers, median s, max s")
    for agent, xs in sorted(per_agent.items()):
        print(f"  {agent:<18} {len(xs):>3} {statistics.median(xs):>8.0f} {max(xs):>6.0f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("room_id")
    ap.add_argument("--since", default="2000-01-01T00:00:00+00:00")
    a = ap.parse_args()
    asyncio.run(main(a.room_id, datetime.fromisoformat(a.since.replace("Z", "+00:00"))))
