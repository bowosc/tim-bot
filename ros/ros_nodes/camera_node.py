#!/usr/bin/env python3
import base64
import subprocess

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger

from ros_nodes.gpt import transcribe_img

# try https://github.com/facebookresearch/scenescript

class CameraNode(Node):
    def __init__(self):
        super().__init__("camera_node")
        self.service = self.create_service(Trigger, "/check_camera", self.on_check_camera)
        self.get_logger().info("CameraNode ready on /check_camera")

    def capture_jpeg_bytes(self, quality: int) -> bytes:
        result = subprocess.run(
            [
                "rpicam-jpeg",
                "--nopreview",
                "--timeout",
                "1500",
                "-q",
                str(quality),
                "-o",
                "-",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return result.stdout

    def on_check_camera(self, request: Trigger.Request, response: Trigger.Response) -> Trigger.Response:
        return Trigger.Response(success=True, message="A sign that says TEST.")

        quality = 40

        try:
            jpeg_bytes = self.capture_jpeg_bytes(quality)
            if not jpeg_bytes:
                raise RuntimeError("Camera returned an empty frame.")

            img_b64 = base64.b64encode(jpeg_bytes).decode("ascii")
            description = transcribe_img(base64_img=img_b64)

            response.success = True
            response.message = description
            self.get_logger().info("Returned camera description.")
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode("utf-8", errors="ignore").strip()
            response.success = False
            response.message = f"camera capture failed: {stderr or exc}"
            self.get_logger().error(response.message)
        except Exception as exc:
            response.success = False
            response.message = f"camera service failed: {exc}"
            self.get_logger().error(response.message)

        return response


def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
