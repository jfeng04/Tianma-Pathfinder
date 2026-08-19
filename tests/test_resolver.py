import pytest

from backend.language.schemas import (
    Mission,
    Target,
)
from backend.mission.resolver import (
    TargetResolutionError,
    resolve_target,
)
from backend.perception.models import (
    CameraPoint,
    Detection,
    PerceivedObject,
)


def make_object(
    object_type: str,
    x: float,
    y: float,
    z: float,
    color: str | None = None,
    confidence: float = 0.9,
) -> PerceivedObject:

    return PerceivedObject(
        object_type=object_type,
        color=color,

        detection=Detection(
            label=(
                f"{color} {object_type}"
                if color
                else object_type
            ),
            confidence=confidence,
            bbox=[
                100.0,
                100.0,
                200.0,
                200.0,
            ],
        ),

        camera_point=CameraPoint(
            x_m=x,
            y_m=y,
            z_m=z,
        ),
    )


def test_resolves_rightmost_cylinder():

    left = make_object(
        "cylinder",
        x=-0.8,
        y=0.0,
        z=3.0,
    )

    right = make_object(
        "cylinder",
        x=1.1,
        y=0.0,
        z=4.0,
    )

    mission = Mission(
        action="navigate",
        target=Target(
            object_type="cylinder",
            spatial_hint="right",
        ),
    )

    result = resolve_target(
        mission,
        [left, right],
    )

    assert result is right


def test_resolves_red_cylinder():

    red = make_object(
        "cylinder",
        color="red",
        x=0.4,
        y=0.0,
        z=4.0,
    )

    blue = make_object(
        "cylinder",
        color="blue",
        x=-0.4,
        y=0.0,
        z=3.0,
    )

    mission = Mission(
        action="navigate",
        target=Target(
            object_type="cylinder",
            color="red",
        ),
    )

    result = resolve_target(
        mission,
        [red, blue],
    )

    assert result is red


def test_resolves_nearest():

    near = make_object(
        "box",
        x=0.0,
        y=0.0,
        z=2.0,
    )

    far = make_object(
        "box",
        x=0.0,
        y=0.0,
        z=6.0,
    )

    mission = Mission(
        action="navigate",
        target=Target(
            object_type="box",
            spatial_hint="nearest",
        ),
    )

    result = resolve_target(
        mission,
        [near, far],
    )

    assert result is near


def test_ambiguous_target_is_rejected():

    first = make_object(
        "cylinder",
        x=-1.0,
        y=0.0,
        z=3.0,
    )

    second = make_object(
        "cylinder",
        x=1.0,
        y=0.0,
        z=3.0,
    )

    mission = Mission(
        action="navigate",
        target=Target(
            object_type="cylinder",
        ),
    )

    with pytest.raises(
        TargetResolutionError
    ):
        resolve_target(
            mission,
            [first, second],
        )