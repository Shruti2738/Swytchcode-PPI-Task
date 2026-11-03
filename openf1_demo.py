
import subprocess
import json


def team_color(text, color):
    if not color or len(color) != 6:
        return text

    try:
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)

        return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

    except ValueError:
        return text


def run_swytchcode(method, params):
    command = ["swytchcode", "exec", method]

    for key, value in params.items():
        command.extend(["--param", f"{key}={value}"])

    command.append("--json")

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode != 0:
        print("Swytchcode execution failed:")
        print(result.stderr)
        print(result.stdout)
        return None

    output = result.stdout
    decoder = json.JSONDecoder()

    for i, char in enumerate(output):
        if char == "{":
            try:
                response, _ = decoder.raw_decode(output[i:])
                return response
            except json.JSONDecodeError:
                continue

    print("Could not parse Swytchcode response.")
    print(output)
    return None


def main():
    print("\n===================================")
    print("       OPENF1 DRIVER EXPLORER")
    print("===================================")

    year = input("\nEnter F1 season year (default 2024): ").strip()

    if not year:
        year = "2024"

    print("\nFetching race sessions through Swytchcode...")

    sessions_response = run_swytchcode(
        "openf1.sessions.list",
        {"year": year, "session_name": "Race"}
    )

    if not sessions_response:
        return

    sessions = sessions_response.get("data", [])

    if not sessions:
        print("No race sessions found.")
        return

    print(f"\nRACE SESSIONS - {year}")
    print("-" * 65)

    for i, session in enumerate(sessions):
        print(
            f"{i + 1:2}. {session['country_name']:<22}"
            f"{session['circuit_short_name']:<22}"
            f"{session['date_start'][:10]}"
        )

    try:
        choice = int(input("\nSelect a race number: "))

        if choice < 1 or choice > len(sessions):
            print("Invalid selection.")
            return

    except ValueError:
        print("Please enter a valid number.")
        return

    selected_session = sessions[choice - 1]
    session_key = selected_session["session_key"]

    print(
        f"\nFetching drivers for "
        f"{selected_session['country_name']} Grand Prix..."
    )

    drivers_response = run_swytchcode(
        "openf1.drivers.list",
        {"session_key": session_key}
    )

    if not drivers_response:
        return

    drivers = drivers_response.get("data", [])

    if not drivers:
        print("No drivers found.")
        return

    print("\n===================================")
    print(f"  {selected_session['country_name'].upper()} GRAND PRIX")
    print("===================================")

    print(f"\n{'NO.':<6}{'DRIVER':<25}{'TEAM'}")
    print("-" * 65)

    drivers.sort(key=lambda driver: driver["driver_number"])

    for driver in drivers:
        color = driver.get("team_colour", "FFFFFF")

        number = team_color(
            f"{driver['driver_number']:<6}", color
        )

        name = team_color(
            f"{driver['full_name']:<25}", color
        )

        team = team_color(
            driver["team_name"], color
        )

        print(f"{number}{name}{team}")

    print(f"\nTotal drivers: {len(drivers)}")


if __name__ == "__main__":
    main()
