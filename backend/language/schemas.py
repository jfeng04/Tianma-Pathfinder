from typing import Literal
from pydantic import BaseModel, Field, model_validator

ObjectType = Literal["cylinder", "box", "gate"]

Color = Literal["red", "blue", "yellow", "green"]

SpatialHint = Literal["nearest", "farthest", "far_end", "left", "right"]
Constraint = Literal["avoid_obstacles", "remain_in_course", "do_not_enter_restricted_zone"]

# 目标体
class Target(BaseModel):
    object_type: ObjectType 
    color: Color | None = None
    spatial_hint: SpatialHint | None = None

# 任务
class Mission(BaseModel):
    action: Literal[
        "navigate",
        "inspect",
        "return_to_start",
        "stop",
        "unsupported",
    ] 
    target: Target | None = None # 目标体
    stop_distance_m: float = Field(default=1.5, ge=0.5, le=10.0) # 在距离 0.5-10.0 之间停止
    constraints: list[Constraint] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_action_target_relationship(self) -> "Mission":
        if self.action in {"navigate", "inspect"} and self.target is None:
            raise ValueError(
                f"Action '{self.action}' requires a target."
            )

        if self.action in {
            "stop",
            "return_to_start",
            "unsupported",
        } and self.target is not None:
            raise ValueError(
                f"Action '{self.action}' must not include a target."
            )

        return self