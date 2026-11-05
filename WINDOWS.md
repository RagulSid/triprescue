# Windows notes

Switch Console on Windows is early access. These notes cover one problem we hit with the local Switch server and how we fixed it.

## Mattermost messages never reach the agents

### Symptom

- An agent answers in Switch Console chat, and can post its greeting in Mattermost, but never answers anything typed in Mattermost.
- Even `!list-agents` and `!roles` get no reply.
- The Switch server log (`%APPDATA%\switchdash\local-switch-server\native\logs\switch-core.log`) repeats, every few seconds:

  ```
  WARNING [mattermostdriver.websocket] Failed to establish websocket connection: timed out during opening handshake
  ```

- `netstat -ano | findstr 61126` shows the Switch server's `python.exe` stuck in `SYN_SENT` to `[::1]:61126`, with no connection to `127.0.0.1:61126`. (61126 is the Mattermost port on our machine; Console picks ports per machine, so yours may differ.)

### Cause

WSL was set to mirrored networking (`networkingMode=mirrored` in `%USERPROFILE%\.wslconfig`). Docker Desktop runs inside WSL and publishes the bundled Mattermost on `127.0.0.1` only. In mirrored mode a connection to `[::1]` on that port is neither accepted nor refused; it hangs.

Switch connects to `http://localhost:61126`. On Windows, `localhost` resolves to `::1` first, so the websocket waits on `::1` until its handshake times out and never tries `127.0.0.1`. Posting uses a different client and still works, so only incoming messages are lost.

Changing the IPv6 prefix policy does not help: `localhost` still resolves to `::1` first.

### Fix

1. In `%USERPROFILE%\.wslconfig`, turn off mirrored networking by commenting out the line:

   ```ini
   [wsl2]
   # networkingMode=mirrored
   ```

2. Stop Docker Desktop, run `wsl --shutdown`, then start Docker Desktop.
3. If the Mattermost container (`switchdash-local-mattermost-mattermost-1`) is not running, start it again with `docker start switchdash-local-mattermost-mattermost-1`, or restart the server from its page in Switch Console.

A connection to `[::1]` is now refused in about two seconds, and Switch falls back to `127.0.0.1`. The Switch server does not need a restart; it retries the websocket on its own.

### Check it worked

- `netstat -ano | findstr 61126` shows the server's `python.exe` with `ESTABLISHED` connections to `127.0.0.1:61126`.
- `switch-core.log` shows `Websocket authentification OK` and the handshake warnings stop.
- `!roles` in a Mattermost room gets a reply.

### Undo

Remove the `#` before `networkingMode=mirrored`, then run `wsl --shutdown` and restart Docker Desktop. Mattermost messages will stop reaching Switch again.
