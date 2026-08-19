from pydantic import BaseModel

from backend.language.schemas import (
    Color,
    ObjectType,
)


class Detection(BaseModel):
    label: str
    confidence: float
    bbox: list[float]


class CameraPoint(BaseModel):
    x_m: float
    y_m: float
    z_m: float


class PerceivedObject(BaseModel):
    object_type: ObjectType
    color: Color | None = None

    detection: Detection
    camera_point: CameraPoint