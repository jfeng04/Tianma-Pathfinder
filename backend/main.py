from executor import execute_mission
from parser import MissionParseError, parse_command

def main() -> None:

    # 命令
    command = input("Rover command: ")

    try:
        mission = parse_command(command)
        print("\nValidated mission:")
        print(mission.model_dump_json(indent=2))

        print("\nExecutor")
        execute_mission(mission)

    except MissionParseError as exc:
        print(f"Command rejected: {exc}")

    except Exception as exc:
        print(f"Unexpected error: {exc}")

if __name__ == "__main__":
    main()