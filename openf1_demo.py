import subprocess
import json
from collections import Counter

COMPOUNDS = {
    "SOFT": ("S", "31"), "MEDIUM": ("M", "33"), "HARD": ("H", "37"),
    "INTERMEDIATE": ("I", "32"), "WET": ("W", "34"),
}


def team_color(text, color):
    if not color or len(color) != 6:
        return text
    try:
        r, g, b = (int(color[i:i + 2], 16) for i in (0, 2, 4))
        return f"\033[38;2;{r};{g};{b}m{text}\033[0m"
    except ValueError:
        return text


def run_swytchcode(method, params):
    command = ["swytchcode", "exec", method]
    for key, value in params.items():
        command.extend(["--param", f"{key}={value}"])
    command.append("--json")

    result = subprocess.run(command, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print(f"Swytchcode execution failed for {method}:")
        print(result.stderr or result.stdout)
        return None

    for line in reversed(result.stdout.strip().splitlines()):
        try:
            response = json.loads(line.strip())
            if isinstance(response, dict) and "data" in response:
                return response
        except json.JSONDecodeError:
            continue

    print(f"Could not parse Swytchcode response for {method}.")
    return None


def get_records(response):
    if isinstance(response, list):
        return response
    if isinstance(response, str):
        try:
            return get_records(json.loads(response))
        except json.JSONDecodeError:
            return None
    if isinstance(response, dict):
        for key in ["data", "result", "response", "output"]:
            if key in response:
                records = get_records(response[key])
                if records is not None:
                    return records
    return None


def fetch(method, **params):
    response = run_swytchcode(method, params)
    return (get_records(response) if response else None) or []


def pick_race():
    year = input("\nSeason year (default 2024): ").strip() or "2024"
    sessions = fetch("openf1.sessions.list", year=year, session_name="Race")
    if not sessions:
        print("No race sessions found.")
        return None

    print(f"\nRACE SESSIONS - {year}")
    print("-" * 70)
    for i, s in enumerate(sessions, 1):
        print(f"{i:2}. {s.get('country_name', '?'):<22}"
              f"{s.get('circuit_short_name', '?'):<22}"
              f"{str(s.get('date_start', ''))[:10]}")
    try:
        choice = int(input("\nSelect a race number: "))
        return sessions[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None


def show_grid(session):
    drivers = fetch("openf1.drivers.list", session_key=session["session_key"])
    drivers.sort(key=lambda d: int(d.get("driver_number", 0)))
    print(f"\n{'NO.':<6}{'DRIVER':<25}TEAM")
    print("-" * 60)
    for d in drivers:
        c = d.get("team_colour", "FFFFFF")
        print(team_color(f"{d.get('driver_number', '?'):<6}"
                         f"{d.get('full_name', '?'):<25}"
                         f"{d.get('team_name', '?')}", c))


def show_strategy(session):
    key = session["session_key"]
    drivers = {d["driver_number"]: d
               for d in fetch("openf1.drivers.list", session_key=key)}
    stints = fetch("openf1.stints.list", session_key=key)
    if not stints:
        print("No stint data for this race.")
        return

    total_laps = max((s.get("lap_end") or 0) for s in stints)
    by_driver = {}
    for s in stints:
        by_driver.setdefault(s["driver_number"], []).append(s)

    print(f"\nTYRE STRATEGY  (S=soft M=medium H=hard I=inter W=wet, "
          f"{total_laps} laps)")
    print("-" * (14 + total_laps))

    strategies = Counter()
    for num in sorted(by_driver):
        d = drivers.get(num, {})
        code = d.get("name_acronym", str(num))
        ordered = sorted(by_driver[num], key=lambda s: s.get("stint_number", 0))
        bar, letters = "", []
        for s in ordered:
            letter, ansi = COMPOUNDS.get(
                str(s.get("compound", "")).upper(), ("?", "90"))
            start = s.get("lap_start") or 1
            end = s.get("lap_end") or total_laps
            bar += f"\033[{ansi}m{letter * max(end - start + 1, 0)}\033[0m"
            letters.append(letter)
        strategies["-".join(letters)] += 1
        print(f"{code:<5}{len(ordered) - 1} stop  {bar}")

    print("\nMost common strategies:")
    for strat, n in strategies.most_common(3):
        print(f"  {strat:<12}{n} drivers")


def show_pit_stops(session):
    key = session["session_key"]
    drivers = {d["driver_number"]: d.get("name_acronym", str(d["driver_number"]))
               for d in fetch("openf1.drivers.list", session_key=key)}
    pits = [p for p in fetch("openf1.pit.list", session_key=key)
            if isinstance(p.get("pit_duration"), (int, float))]
    if not pits:
        print("No pit stop data for this race.")
        return

    pits.sort(key=lambda p: p["pit_duration"])
    print("\nFASTEST PIT STOPS")
    print("-" * 40)
    for p in pits[:5]:
        print(f"{drivers.get(p['driver_number'], '?'):<6}"
              f"lap {p.get('lap_number', '?'):<4}"
              f"{p['pit_duration']:.1f}s")

    avg = sum(p["pit_duration"] for p in pits) / len(pits)
    print(f"\n{len(pits)} stops recorded, average {avg:.1f}s")


def main():
    print("\n===================================")
    print("   PITWALL x SWYTCHCODE EXPLORER")
    print("===================================")

    session = pick_race()
    if session is None:
        return
    country = session.get("country_name", "Unknown")

    views = {"1": show_grid, "2": show_strategy, "3": show_pit_stops}
    while True:
        print(f"\n{country.upper()} GRAND PRIX")
        print("1. Starting grid   2. Tyre strategy   3. Pit stops   q. Quit")
        choice = input("> ").strip().lower()
        if choice == "q":
            break
        view = views.get(choice)
        if view:
            view(session)
        else:
            print("Pick 1, 2, 3 or q.")


if __name__ == "__main__":
    main()