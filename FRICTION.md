# PitWall x Swytchcode: OpenF1 Driver Explorer

A small CLI app that fetches Formula 1 race sessions and driver lineups from the [OpenF1](https://openf1.org) API **through Swytchcode** instead of making raw HTTP calls from Python.

It started as a test of Swytchcode for my F1 analytics project, PitWall Analytics, whose data pipeline also pulls from OpenF1.

**Demo video:** `<link>`

## Problem and intended user

Scripts and AI agents that call APIs directly have to handle URLs, parameters and response parsing themselves. Swytchcode sits between the caller and the API: each operation is defined once in a Wrekenfile and executed by name. This project tests that idea on a public, keyless API.

**Intended user:** a developer or agent that needs structured, repeatable access to F1 data.

## Architecture

```
Python app (openf1_demo.py)
        |
        v
Swytchcode CLI (swytchcode exec)
        |
        v
Custom local OpenF1 provider (Wrekenfile)
        |
        v
OpenF1 REST API
```

The Python code never calls OpenF1 directly. It only runs `swytchcode exec <canonical_id>` and parses the JSON response.

## API and integration explored

OpenF1 was **not available in the Swytchcode registry**. I searched for `openf1` and `formula`, and a natural-language search for F1 data returned nothing. So I built a **custom local provider** by hand with two methods.

| Canonical ID | Method | Endpoint | Parameters | Purpose |
|---|---|---|---|---|
| `openf1.sessions.list` | GET | `/sessions` | `year`, `session_name` | List race sessions for a season |
| `openf1.drivers.list` | GET | `/drivers` | `session_key` | List drivers for a session |

OpenF1 needs no API key for historical data, so this repo contains no secrets.

## Project structure

```
.
├── openf1_demo.py                  # Interactive demo app
├── README.md
├── FRICTION.md                     # Friction diary
├── logs/                           # Saved demo output
└── .swytchcode/
    ├── tooling.json                # Which methods the project may execute
    ├── workspace.json
    └── integrations/
        ├── manifest.json           # Registers the OpenF1 provider and its endpoints
        └── OpenF1/openf1/1.0.0/
            ├── wrekenfile.yaml     # Method definitions (HTTP, inputs, execution)
            └── methods.json        # Method list with canonical IDs
```

The `Weaviate` folder under `integrations/` is not part of this project.

## How the provider works

Three pieces have to line up before a custom method runs:

1. **`wrekenfile.yaml`** defines what each method is: HTTP verb, endpoint, typed inputs and execution mode.
2. **`methods.json`** lists the methods and their canonical IDs, and **`manifest.json`** registers `OpenF1.openf1@1.0.0` with its base URL (`https://api.openf1.org/v1` for both sandbox and production).
3. **`tooling.json`** controls which methods the project may execute. It is filled in with `swytchcode add method <canonical_id>`.

## Setup and commands

Requirements: Python 3 and the Swytchcode CLI ([install instructions](https://docs.swytchcode.com)). Commands are shown for Windows PowerShell.

```powershell
# 1. Clone this repo and enter it
git clone <repo-url>
cd <repo-folder>

# 2. Confirm the OpenF1 methods are discovered
swytchcode list methods openf1

# 3. Inspect a request without sending it
swytchcode exec openf1.sessions.list --param year=2024 --param session_name=Race --dry-run

# 4. Run a live call
swytchcode exec openf1.sessions.list --param year=2024 --param session_name=Race --json

# 5. Run the demo
python .\openf1_demo.py
```

When prompted, press Enter for the 2024 season, then pick a race number.

## What worked

- Writing a custom provider by hand (`wrekenfile.yaml`, `methods.json`, `manifest.json`).
- `swytchcode list methods openf1` discovering both methods.
- `swytchcode add method` enabling both in `tooling.json`.
- A dry-run of `openf1.sessions.list` generating the correct GET URL.
- Live execution returning HTTP 200 with 24 race sessions for 2024 (Bahrain `session_key` is `9472`).
- `openf1.drivers.list` with `session_key=9472` returning all 20 drivers.
- Chaining the two methods in Python: the session key from the first call feeds the second.
- Coloured driver output using `team_colour` from the API.

### Sample output

```
RACE SESSIONS - 2024
 1. Bahrain               Sakhir                2024-03-02
 2. Saudi Arabia          Jeddah                2024-03-09
 ...

BAHRAIN GRAND PRIX
NO.   DRIVER                   TEAM
1     Max VERSTAPPEN           Red Bull Racing
4     Lando NORRIS             McLaren
16    Charles LECLERC          Ferrari
44    Lewis HAMILTON           Mercedes
...
Total drivers: 20
```

## What did not work

Full details, with exact errors, are in [FRICTION.md](FRICTION.md). Main points:

1. **Example download failed from `C:\Windows\System32`.**
   `error: extract demo: mkdir weekly-reporting: Access is denied.`
   Fixed by working from a user folder.
2. **No OpenF1 provider in the registry.** `search` returned `[]` for both `openf1` and `formula`. This led to the custom provider.
3. **New methods listed but not executable.** I tried to add `openf1.stints.list` and `openf1.pit.list` for tyre strategy and pit stop views. `swytchcode list methods` showed them, but `swytchcode exec` failed with:
   `tool "openf1.stints.list" is not configured in this project's tooling.json. Run: swytchcode get openf1 && swytchcode add openf1.stints.list`
   Editing the Wrekenfile and `methods.json` was not enough. See FRICTION.md #14 for the outcome.
4. **A Python encoding error.** `UnicodeDecodeError`, because Windows decoded CLI output as cp1252. Fixed with `encoding="utf-8", errors="replace"` in `subprocess.run`.
5. **Telemetry warnings on every command** (`posthog ... shutdown timeout exceeded`). Harmless, but they look like errors to a new user. The demo skips non-JSON output lines to cope with them.
6. **An AI-suggested command that did not exist.** `swytchcode list integrations` is not a supported category (supported: `methods`, `workflows`, `providers`, `tooling`).

## Notes on the Wrekenfile

- Each method has `HTTP` (verb, endpoint), `INPUTS` (typed, `LOCATION: query`), `EXECUTION` (`KIND: http`, `MODE: sync`) and a `CANONICAL_ID`.
- `SECURITY: - {}` marks the API as keyless.
- This is a **manually constructed local provider**, not one published to the Swytchcode registry.
- The Wrekenfile and `methods.json` describe what a method is. `tooling.json` decides what the project may run, so editing the first two is not enough to make a method executable.

## How to reproduce

1. Install the CLI and run `swytchcode init` in an empty folder.
2. Copy `.swytchcode/integrations/OpenF1/` from this repo into the same path.
3. Add the `OpenF1.openf1@1.0.0` entry to `.swytchcode/integrations/manifest.json` (copy it from this repo's version).
4. Register the methods:
   ```powershell
   swytchcode add method openf1.sessions.list
   swytchcode add method openf1.drivers.list
   ```
5. Run `swytchcode list methods openf1`, then `python .\openf1_demo.py`.

## AI usage

I used Claude to plan the project, draft the Wrekenfile structure and the Python demo, debug PowerShell and CLI errors, and draft this README. I ran every command myself and checked the outputs against real CLI behaviour. Not every AI answer worked: it suggested `swytchcode list integrations`, which does not exist, and the fix came from the CLI help and docs (FRICTION.md #7, #16).

## Next steps

- Finish registering `openf1.stints.list` and `openf1.pit.list` and build a tyre strategy and pit stop view.
- Use the same provider as the data source for my PitWall Analytics ETL.
