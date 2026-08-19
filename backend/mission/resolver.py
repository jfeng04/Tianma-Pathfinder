import math

from backend.language.schemas import Mission
from backend.perception.models import PerceivedObject


class TargetResolutionError(Exception):
    pass


def distance_from_camera(
    obj: PerceivedObject,
) -> float:
    point = obj.camera_point

    return math.sqrt(
        point.x_m ** 2
        + point.y_m ** 2
        + point.z_m ** 2
    )


def resolve_target(
    mission: Mission,
    objects: list[PerceivedObject],
) -> PerceivedObject:

    if mission.action not in {
        "navigate",
        "inspect",
    }:
        raise TargetResolutionError(
            f"Action '{mission.action}' "
            "does not require target resolution."
        )

    if mission.target is None:
        raise TargetResolutionError(
            "Mission has no target."
        )

    target = mission.target

    # 匹配对象类型
    candidates = [
        obj
        for obj in objects
        if obj.object_type
        == target.object_type
    ]

    # 如果收到请求，配上颜色
    if target.color is not None:
        candidates = [obj for obj in candidates
            if obj.color == target.color
        ]

    if not candidates:
        raise TargetResolutionError(
            "No perceived object matches "
            f"target type={target.object_type}, "
            f"color={target.color}."
        )

    # 处理空间提示
    hint = target.spatial_hint

    if hint == "left":
        return min(
            candidates,
            key=lambda obj:
                obj.camera_point.x_m,
        )


    if hint == "right":
        return max(
            candidates,
            key=lambda obj:
                obj.camera_point.x_m,
        )


    if hint == "nearest":
        return min(
            candidates,
            key=distance_from_camera,
        )


    if hint == "farthest":
        return max(
            candidates,
            key=distance_from_camera,
        )


    if hint == "far_end":
        return max(
            candidates,
            key=lambda obj:
                obj.camera_point.z_m,
        )

    # 无空间提示
    if len(candidates) == 1:
        return candidates[0]


    raise TargetResolutionError(
        "Target is ambiguous: "
        f"{len(candidates)} objects match "
        "but no spatial hint was provided."
    )