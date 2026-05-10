import os
import time

from dotenv import load_dotenv
from langchain.agents import tool
from langchain_openai import ChatOpenAI
from rosa import ROSA, RobotSystemPrompts
import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger


ROS_VERSION = 2
CAMERA_REQUEST_TIMEOUT_SEC = 8.0
_camera_client = None
_ros_node = None


@tool(description="Returns a description of what's in front of the robot.")
def check_camera() -> str:
    global _camera_client, _ros_node

    if _camera_client is None or _ros_node is None:
        print("Camera client not initialized.")
        return "Camera client not initialized."
    if not _camera_client.wait_for_service(timeout_sec=1.0):
        print("Camera service unavailable.")
        return "Camera service unavailable."

    req = Trigger.Request()
    future = _camera_client.call_async(req)
    deadline = time.monotonic() + CAMERA_REQUEST_TIMEOUT_SEC
    while not future.done() and time.monotonic() < deadline:
        time.sleep(0.05)

    if not future.done():
        print("Camera request timed out.")
        return "Camera request timed out."

    exc = future.exception()
    if exc is not None:
        err = f"Camera request failed: {exc}"
        print(err)
        return err

    res = future.result()
    if res is None:
        print("Camera request failed: empty response.")
        return "Camera request failed: empty response."

    print("Camera request sucessful!")
    return res.message if res.success else "Camera failed."


class BrainNode(Node):
    def __init__(self):
        global _camera_client, _ros_node

        super().__init__("brain_node")
        load_dotenv()

        _ros_node = self
        self._camera_client_group = ReentrantCallbackGroup()
        _camera_client = self.create_client(
            Trigger,
            "/check_camera",
            callback_group=self._camera_client_group,
        )

        llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.4,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

        prompts = RobotSystemPrompts(
            embodiment_and_persona="You are a robot named Tim.",
            critical_instructions=(
                "You try and keep your response short (1-2 sentences max) unless requested. "
            ),
            about_your_capabilities="Use tools as needed.",
        )

        self.agent = ROSA(
            ros_version=ROS_VERSION,
            llm=llm,
            tools=[check_camera],
            prompts=prompts,
        )

        self.movement_directive_pub = self.create_publisher(String, "/movement_directive", 10)
        self.speech_text_pub = self.create_publisher(String, "/speech_text", 10)
        self.user_command_sub = self.create_subscription(
            String,
            "/user_command",
            self.on_user_command,
            10,
        )

        self.get_logger().info("BrainNode initiated.")

    def on_user_command(self, msg: String) -> None:
        response = self.agent.invoke(msg.data)
        self.get_logger().info(f"ROSA response: {response}")

        speech_msg = String()
        speech_msg.data = response
        self.speech_text_pub.publish(speech_msg)
        self.get_logger().info("Published response to /speech_text")


def main(args=None):
    rclpy.init(args=args)
    node = BrainNode()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
