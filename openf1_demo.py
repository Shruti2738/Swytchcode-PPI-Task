
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
        print("\nSwytchcode execution failed:")
        print(result.stderr)
        print(result.stdout)
        return None

    output = result.stdout.strip()

    # Find the JSON response in CLI output
    decoder = json.JSONDecoder()
    response = None

    for i, char in enumerate(output):
        if char in "[{":
            try:
                response, _ = decoder.raw_decode(output[i:])
                break
            except json.JSONDecodeError:
                continue

    if response is None:
        print("\nCould not parse Swytchcode response.")
        print(output)
        return None

    return response


def get_records(response):
    """
    Extract a list of records from common Swytchcode
    response formats.
    """

    if isinstance(response, list):
        return response

    if isinstance(response, str):
        try:
            return get_records(json.loads(response))
        except json.JSONDecodeError:
            return None

    if isinstance(response, dict):

        # Check common response wrapper fields
        for key in ["data", "result", "response", "output"]:
            if key in response:
                records = get_records(response[key])

                if records is not None:
                    return records

        # A single API record
        if "session_key" in response or "driver_number" in response:
            return [response]

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

    if sessions_response is None:
        return

    sessions = get_records(sessions_response)

    if not sessions:
        print("\nNo valid session records found.")
        print("Actual response:")
        print(repr(sessions_response))
        return

    # Validate session records
    if not isinstance(sessions[0], dict):
        print("\nUnexpected session format:")
        print(repr(sessions_response))
        return

    print(f"\nRACE SESSIONS - {year}")
    print("-" * 75)

    for i, session in enumerate(sessions):
        print(
            f"{i + 1:2}. "
            f"{session.get('country_name', 'Unknown'):<22}"
            f"{session.get('circuit_short_name', 'Unknown'):<22}"
            f"{str(session.get('date_start', ''))[:10]}"
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
    session_key = selected_session.get("session_key")

    if session_key is None:
        print("Session key missing from selected session.")
        print(repr(selected_session))
        return

    country = selected_session.get("country_name", "Unknown")

    print(f"\nFetching drivers for {country} Grand Prix...")

    drivers_response = run_swytchcode(
        "openf1.drivers.list",
        {"session_key": session_key}
    )

    if drivers_response is None:
        return

    drivers = get_records(drivers_response)

    if not drivers:
        print("\nNo valid driver records found.")
        print("Actual response:")
        print(repr(drivers_response))
        return

    if not isinstance(drivers[0], dict):
        print("\nUnexpected driver format:")
        print(repr(drivers_response))
        return

    print("\n===================================")
    print(f"  {country.upper()} GRAND PRIX")
    print("===================================")

    print(f"\n{'NO.':<6}{'DRIVER':<25}{'TEAM'}")
    print("-" * 65)

    drivers.sort(
        key=lambda driver: int(driver.get("driver_number", 0))
    )

    for driver in drivers:
        color = driver.get("team_colour", "FFFFFF")

        number = team_color(
            f"{driver.get('driver_number', '?'):<6}", color
        )

        name = team_color(
            f"{driver.get('full_name', 'Unknown'):<25}", color
        )

        team = team_color(
            driver.get("team_name", "Unknown"), color
        )

        print(f"{number}{name}{team}")

    print(f"\nTotal drivers: {len(drivers)}")


if __name__ == "__main__":
    main()
