#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from ros_nodes.serial_helpers import send_serial_command


class MotorNode(Node):
    def __init__(self):
        super().__init__("motor_node")
        self.directive_sub = self.create_subscription(
            String,
            "/movement_directive",
            self.on_movement_directive,
            10,
        )
        self.get_logger().info("MotorNode ready on /movement_directive")

    def on_movement_directive(self, msg: String) -> None:
        command = msg.data
        if not command:
            self.get_logger().warn("Ignoring empty movement directive.")
            return

        try:
            send_serial_command(command)
        except Exception as exc:
            self.get_logger().error(f"Motor command failed: {exc}")


def main(args=None):
    rclpy.init(args=args)
    node = MotorNode()
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
