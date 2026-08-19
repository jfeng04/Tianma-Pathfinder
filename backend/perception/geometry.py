import numpy as np

from pydantic import BaseModel
from backend.perception.models import (
    CameraPoint,
    Detection,
)
from sensor_msgs.msg import CameraInfo

from backend.perception.detector import Detection


def get_detection_center(
    detection: Detection,
) -> tuple[int, int]:

    x1, y1, x2, y2 = detection.bbox

    u = round((x1 + x2) / 2)
    v = round((y1 + y2) / 2)

    return u, v

def get_depth_near_pixel(
    depth_image: np.ndarray,
    u: int,
    v: int,
    radius: int = 2,
) -> float:

    height, width = depth_image.shape[:2]

    x_min = max(0, u - radius)
    x_max = min(width, u + radius + 1)

    y_min = max(0, v - radius)
    y_max = min(height, v + radius + 1)

    patch = depth_image[
        y_min:y_max,
        x_min:x_max,
    ]

    valid = patch[
        np.isfinite(patch)
        & (patch > 0)
    ]

    if valid.size == 0:
        raise ValueError(
            "No valid depth near target pixel."
        )

    return float(
        np.median(valid)
    )

def pixel_to_camera_point(
    u: int,
    v: int,
    depth_m: float,
    camera_info: CameraInfo,
) -> CameraPoint:

    fx = camera_info.k[0]
    fy = camera_info.k[4]

    cx = camera_info.k[2]
    cy = camera_info.k[5]

    if fx <= 0 or fy <= 0:
        raise ValueError(
            "Invalid camera intrinsics."
        )

    x = (
        (u - cx)
        * depth_m
        / fx
    )

    y = (
        (v - cy)
        * depth_m
        / fy
    )

    z = depth_m

    return CameraPoint(
        x_m=float(x),
        y_m=float(y),
        z_m=float(z),
    )