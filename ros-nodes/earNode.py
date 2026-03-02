import rclpy, threading
from rclpy.node import Node
from std_msgs.msg import String


class EarNode(Node):
    def __init__(self):
        super().__init__('ear_node')
        self.user_command_pub = self.create_publisher(String, '/user_command', 10)
        self._running = True

        self.input_thread = threading.Thread(target=self._read_terminal_loop, daemon=True)
        self.input_thread.start()

        self.get_logger().info("EarNode initiated.")
        self.get_logger().info("Type commands and press Enter. Ctrl+C to quit.")

    def _read_terminal_loop(self):
        while self._running and rclpy.ok():
            try:
                text = input("Command for TIM: > ").strip()
            except EOFError:
                break

            if not text:
                continue

            msg = String()
            msg.data = text
            self.user_command_pub.publish(msg)
            self.get_logger().info(f"Published user_command_text: {text}")

    def destroy_node(self):
        self._running = False
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = EarNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()