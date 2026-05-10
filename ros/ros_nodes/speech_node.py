#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from ros_nodes.speech_helpers import fast_verbalize_string


class SpeechNode(Node):
    def __init__(self):
        super().__init__("speech_node")
        self.speech_sub = self.create_subscription(
            String,
            "/speech_text",
            self.on_speech_text,
            10,
        )
        self.get_logger().info("SpeechNode ready on /speech_text")

    def on_speech_text(self, msg: String) -> None:
        print("speaking aloud message.")
        return
        phrase = msg.data.strip()
        if not phrase:
            self.get_logger().warn("Ignoring empty speech text.")
            return

        try:
            fast_verbalize_string(phrase)
        except Exception as exc:
            self.get_logger().error(f"Speech synthesis failed: {exc}")


def main(args=None):
    rclpy.init(args=args)
    node = SpeechNode()
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
