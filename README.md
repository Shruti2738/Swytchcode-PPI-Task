# PitWall x Swytchcode: OpenF1 Driver Explorer

A small CLI app that fetches Formula 1 race sessions and driver lineups from the [OpenF1](https://openf1.org) API **through Swytchcode** instead of making raw HTTP calls from Python.

It started as a test of Swytchcode for my F1 analytics project, PitWall Analytics, whose data pipeline also pulls from OpenF1.

**Demo video:** `<https://drive.google.com/file/d/1lCUBeNxoDCY5F6LBgOm58rivcSArKMhq/view?usp=sharing>`

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
Custom OpenF1 provider (Wrekenfile)
        |
        v
OpenF1 REST API
```

The Python code never calls OpenF1 directly. It only runs `swytchcode exec <canonical_id>` and parses the JSON response.

## API and integration explored

OpenF1 was **not available in the Swytchcode registry**, so I wrote a custom local provider with two methods.

| Canonical ID | Method | Endpoint | Parameters | Purpose |
|---|---|---|---|---|
| `openf1.sessions.list` | GET | `/sessions` | `year`, `session_name` | List race sessions for a season |
| `openf1.drivers.list` | GET | `/drivers` | `session_key` | List drivers for a session |

OpenF1 needs no API key for historical data, so no secrets are used in this repo.

## Project structure

```
.
├── openf1_demo.py            # Interactive demo app
├── FRICTION.md               # Friction diary
├── README.md
└── .swytchcode/
    ├── tooling.json          # Which methods the project may execute
    ├── workspace.json
    └── integrations/
        └── OpenF1/openf1/1.0.0/
            ├── wrekenfile.yaml   # Method definitions (HTTP, inputs, execution)
            └── methods.json      # Method list with canonical IDs
```

## Setup and commands

Requirements: Python 3, Node.js (for the CLI install), Windows PowerShell or any shell.

```powershell
# 1. Install the Swytchcode CLI (see https://docs.swytchcode.com)
# 2. Clone this repo and enter it
git clone <repo-url>
cd <repo-folder>

# 3. Confirm the OpenF1 methods are registered
swytchcode list methods openf1

# 4. Inspect a request without sending it
swytchcode exec openf1.sessions.list --param year=2024 --param session_name=Race --dry-run

# 5. Run the demo
python .\openf1_demo.py
```

When prompted, press Enter for the 2024 season, then pick a race number.

## What worked

- Writing a custom provider by hand (`wrekenfile.yaml` and `methods.json`).
- `swytchcode list methods` showing both methods.
- `swytchcode exec` returning JSON for sessions and drivers.
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

Full details are in [FRICTION.md](FRICTION.md). Main points:

1. **Example download failed from `C:\Windows\System32`.**
   `error: extract demo: mkdir weekly-reporting: Access is denied.`
   Fixed by working from a user folder.
2. **New methods listed but not executable.** I added `openf1.stints.list` and `openf1.pit.list` to the Wrekenfile and `methods.json`. `swytchcode list methods` showed them, but `swytchcode exec` failed with:
   `tool "openf1.stints.list" is not configured in this project's tooling.json. Run: swytchcode get openf1 && swytchcode add openf1.stints.list`
   Methods must also be registered in `tooling.json` with `swytchcode add`.
3. **Telemetry warnings on every command** (`posthog ... shutdown timeout exceeded`). Harmless, but they look like errors to a new user, and the demo script skips non-JSON lines to cope with them.

## Notes on the Wrekenfile

- Each method has `HTTP` (verb, endpoint), `INPUTS` (typed, with `LOCATION: query`), `EXECUTION` (`KIND: http`, `MODE: sync`) and a `CANONICAL_ID`.
- `SECURITY: - {}` marks the API as keyless.
- I wrote the file by hand, using the structure of the generated example as a template.
- The Wrekenfile and `methods.json` describe what a method is. `tooling.json` controls what the project may run. Editing the first two is not enough to make a method executable.

## How to reproduce

1. Install the CLI and run `swytchcode init` in an empty folder.
2. Create `.swytchcode/integrations/OpenF1/openf1/1.0.0/` and copy in `wrekenfile.yaml` and `methods.json` from this repo.
3. Run `swytchcode list methods openf1` and check both methods appear.
4. Run `python .\openf1_demo.py`.

## AI usage

I used Claude to help plan the project, draft the Wrekenfile structure and the Python demo, debug PowerShell and CLI errors, and draft this README. I ran every command myself and checked the outputs against the real CLI behaviour.

## Next steps

- Register `openf1.stints.list` and `openf1.pit.list` with `swytchcode add` and build a tyre strategy and pit stop view.
- Use the same provider as the data source for my PitWall Analytics ETL.
