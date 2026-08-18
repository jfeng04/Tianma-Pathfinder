from pathlib import Path

import numpy as np
import rclpy

from cv_bridge import CvBridge
from message_filters import (
    ApproximateTimeSynchronizer,
    Subscriber,
)
from PIL import Image as PILImage
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import (
    CameraInfo,
    Image,
)

from backend.perception.detector import (
    annotate_pil_image,
    detect_image,
)

from backend.perception.geometry import (
    get_depth_near_pixel,
    get_detection_center,
    pixel_to_camera_point,
)


RGB_TOPIC = "/tianma/front_rgbd/image"

DEPTH_TOPIC = "/tianma/front_rgbd/depth_image"

CAMERA_INFO_TOPIC = "/tianma/front_rgbd/camera_info"


LABELS = [
    "box",
    "cylinder",
]


class RgbdPerceptionNode(Node):

    def __init__(self):
        super().__init__(
            "tianma_rgbd_perception"
        )

        self.bridge = CvBridge()

        # 保存最新的镜头信息
        self.camera_info = None

        # 处理单一个帧
        self.processed = False


        # Camera calibration subscription
        self.camera_info_sub = (
            self.create_subscription(
                CameraInfo,
                CAMERA_INFO_TOPIC,
                self.camera_info_callback,
                qos_profile_sensor_data,
            )
        )


        # RGB 订阅
        self.rgb_sub = Subscriber(
            self,
            Image,
            RGB_TOPIC,
            qos_profile=qos_profile_sensor_data,
        )


        # 深度
        self.depth_sub = Subscriber(
            self,
            Image,
            DEPTH_TOPIC,
            qos_profile=qos_profile_sensor_data,
        )


        # 配对 RBG 和深度帧
        self.synchronizer = (
            ApproximateTimeSynchronizer(
                [
                    self.rgb_sub,
                    self.depth_sub,
                ],
                queue_size=5,
                slop=0.1,
            )
        )

        self.synchronizer.registerCallback(
            self.rgbd_callback
        )


        self.get_logger().info(
            "Tianma RGBD perception node started."
        )


    def camera_info_callback(
        self,
        msg: CameraInfo,
    ) -> None:

        self.camera_info = msg


    def rgbd_callback(
        self,
        rgb_msg: Image,
        depth_msg: Image,
    ) -> None:


        if self.processed:
            return

        if self.camera_info is None:
            self.get_logger().warning(
                "Waiting for camera info..."
            )
            return


        # ROS RGB -> NumPy

        rgb_array = (
            self.bridge.imgmsg_to_cv2(
                rgb_msg,
                desired_encoding="rgb8",
            )
        )

        # ROS 深度 -> NumPy

        depth_array = (
            self.bridge.imgmsg_to_cv2(
                depth_msg,
                desired_encoding="passthrough",
            )
        )

        # 正则化深度为米
        if depth_msg.encoding == "16UC1":

            depth_m = (
                depth_array.astype(
                    np.float32
                )
                / 1000.0
            )

        elif depth_msg.encoding == "32FC1":

            depth_m = depth_array.astype(
                np.float32
            )

        else:
            raise ValueError(
                "Unsupported depth encoding: "
                f"{depth_msg.encoding}"
            )


        # NumPy RGB -> PIL image

        pil_image = PILImage.fromarray(
            rgb_array
        )

        # 7. 运行 Grounding DINO
        detections = detect_image(
            image=pil_image,
            text_labels=LABELS,
        )


        if not detections:
            self.get_logger().warning(
                "No objects detected."
            )

            return

        # Detection -> pixel -> depth -> XYZ
        for detection in detections:

            # Find center of bounding box
            u, v = get_detection_center(
                detection
            )


            try:

                # 找到像素点边缘的深度
                depth = get_depth_near_pixel(
                    depth_image=depth_m,
                    u=u,
                    v=v,
                )


                # 转化:
                #
                # 像素点 + 深度 + 镜头调整
                #
                # 为:
                #
                # 镜头相对的 XYZ
                point = pixel_to_camera_point(
                    u=u,
                    v=v,
                    depth_m=depth,
                    camera_info=self.camera_info,
                )


            except ValueError as exc:

                self.get_logger().warning(
                    f"{detection.label}: {exc}"
                )

                continue


            self.get_logger().info(
                "\n"
                f"Detected: "
                f"{detection.label}\n"

                f"Confidence: "
                f"{detection.confidence:.3f}\n"

                f"Pixel: "
                f"({u}, {v})\n"

                f"Depth: "
                f"{depth:.3f} m\n"

                f"Camera point: "
                f"x={point.x_m:.3f}, "
                f"y={point.y_m:.3f}, "
                f"z={point.z_m:.3f}"
            )

        # 保存调试图例
        output_path = (
            Path(__file__)
            .resolve()
            .parent
            / "outputs"
            / "gazebo_rgbd_annotated.jpg"
        )

        annotate_pil_image(
            image=pil_image,
            detections=detections,
            output_path=str(output_path),
        )


        self.get_logger().info(
            "Annotated Gazebo frame saved to "
            f"{output_path}"
        )

        self.processed = True


def main() -> None:

    rclpy.init()

    node = RgbdPerceptionNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()