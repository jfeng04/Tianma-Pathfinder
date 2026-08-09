import math
from schemas import Mission
from world import WorldObject, WorldState

class TargetResolutionError(Exception):
    pass

def distance_from_rover(
    obj: WorldObject,
    world: WorldState,
) -> float:
    dx = obj.position.x - world.rover_position.x
    dy = obj.position.y - world.rover_position.y

    return math.hypot(dx, dy)

def lateral_position(
    obj: WorldObject,
    world: WorldState,
) -> float:
    """
    正数代表左侧
    负数代表右侧
    """

    heading_rad = math.radians(world.rover_heading_deg)

    # 单位向量指向左侧
    left_x = -math.sin(heading_rad)
    left_y = math.cos(heading_rad)

    dx = obj.position.x - world.rover_position.x
    dy = obj.position.y - world.rover_position.y

    return dx * left_x + dy * left_y

def resolve_target(
    mission: Mission,
    world: WorldState,
) -> WorldObject:
    if mission.target is None:
        raise TargetResolutionError(
            f"Action '{mission.action}' has no target."
        )

    candidates = [
        obj
        for obj in world.objects
        if obj.object_type == mission.target.object_type
        and (
            mission.target.color is None
            or obj.color == mission.target.color
        )
    ]

    if not candidates:
        raise TargetResolutionError(
            "No object matches the requested type and color."
        )

    hint = mission.target.spatial_hint

    if hint == "nearest":
        return min(
            candidates,
            key=lambda obj: distance_from_rover(obj, world),
        )

    if hint == "farthest":
        return max(
            candidates,
            key=lambda obj: distance_from_rover(obj, world),
        )

    if hint == "left":
        return max(
            candidates,
            key=lambda obj: lateral_position(obj, world),
        )

    if hint == "right":
        return min(
            candidates,
            key=lambda obj: lateral_position(obj, world),
        )

    if len(candidates) == 1:
        return candidates[0]

    raise TargetResolutionError(
        f"Found {len(candidates)} matching objects, "
        "but the command does not specify which one."
    )
