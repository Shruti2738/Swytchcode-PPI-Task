# Friction diary

## 1. Example download failed
- Attempting: Step 3 of welcome wizard, 'Explore examples'
- Command: choose 'Weekly Reporting' while in C:\Windows\System32
- Expected: example project downloads
- Actual: error: extract demo: mkdir weekly-reporting: Access is denied.
- Tried next: moved to a user folder
- Resolved: yes (installer should warn or default to a writable dir)

## 2. Tooling configuration location
- Expected: tooling.json in project root
- Actual: .swytchcode/tooling.json
- Resolved: yes (located the generated file)

## 3. Integration listing
- Command: swytchcode list integrations
- Actual: no integration results displayed; PostHog shutdown timeout warnings appeared
- Status: needs further investigation

## 4. OpenF1 drivers API
- Attempted: drivers endpoint with literal <SESSION_KEY> placeholder
- Actual: No results found
- Next: use actual session_key 9472

## 5. Integration directory inspection
- Command: Get-ChildItem -Force -Recurse .swytchcode\integrations
- Actual: directory exists but contains no files

## 6. Integration listing output
- Command: swytchcode list integrations
- Actual: no integration entries displayed; PostHog shutdown timeout warning
- Status: unresolved

## 7. CLI command discovery
- Finding: list integrations is not a supported listing category.
- Supported categories: methods, workflows, providers, tooling.
- Important distinction: list scans local files; search searches providers and published workflows.
- Status: corrected approach.

## 8. Remote provider discovery
- OpenF1 search: []
- Formula search: []
- Natural-language discovery: no matching capabilities
- Search all: registry returned provider catalogue
- Finding: no OpenF1 provider discovered
- OpenF1 API baseline: sessions and drivers endpoints both working
- Driver test: session_key 9472 returned 2024 Bahrain GP drivers
- Next: investigate custom provider support and local execution

## 9. Creating a custom local OpenF1 provider

- OpenF1 was not available through Swytchcode's remote provider search.
- Created a local provider bundle at:
  `.swytchcode/integrations/OpenF1/openf1/1.0.0/`
- Created `methods.json` to register:
  - `openf1.sessions.list`
  - `openf1.drivers.list`
- Created `wrekenfile.yaml` defining both GET endpoints:
  - `/sessions`
  - `/drivers`
- `swytchcode list methods openf1` successfully discovered both methods.
- `swytchcode add method` successfully enabled both methods in `tooling.json`.

## 10. Configuring the OpenF1 manifest

- Added `OpenF1.openf1@1.0.0` to `.swytchcode/integrations/manifest.json`.
- Configured both sandbox and production endpoints as:
  `https://api.openf1.org/v1`
- OpenF1 public endpoints do not require API authentication.
- Important: this was a manually constructed local provider bundle, not a provider published to the Swytchcode registry.

## 11. Testing Swytchcode execution

- Dry-run of `openf1.sessions.list` successfully generated the correct GET URL.
- Live execution returned HTTP 200.
- Retrieved 24 race sessions from the 2024 season.
- Bahrain 2024 session key: `9472`.
- Live execution of `openf1.drivers.list` with session key `9472` returned 20 drivers.
- Both methods were successfully executed through Swytchcode itself.

## 12. Python integration

- Created `openf1_demo.py`.
- Used Python `subprocess` to execute Swytchcode CLI commands.
- Parsed JSON responses and displayed race sessions and driver information.
- Successfully tested with 2023 and 2024 seasons.
- Python initially raised `UnicodeDecodeError` because Windows used cp1252 to decode CLI output.
- Fixed by setting `encoding="utf-8"` and `errors="replace"` in `subprocess.run`.
- Final demo successfully displayed all 20 Bahrain 2024 drivers.

## 13. Remaining warnings

- PostHog telemetry repeatedly reports shutdown timeouts and dropped messages after CLI commands.
- These warnings did not prevent method discovery, registration, dry-runs, or live API execution.
