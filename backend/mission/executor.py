from schemas import Mission

def execute_mission(mission: Mission) -> None:

    """
    Mission 对象里的所有参数的控制命令
    """

    if mission.action == "stop":
        print("Stopping rover.")
        return

    if mission.action == "return_to_start":
        print("Returning to starting position.")
        return

    if mission.target is None:
        raise ValueError("This action requires a target.")

    print(
        f"Action: {mission.action}\n"
        f"Object: {mission.target.object_type}\n"
        f"Color: {mission.target.color}\n"
        f"Location hint: {mission.target.spatial_hint}\n"
        f"Stopping distance: {mission.stop_distance_m} meters"
    )