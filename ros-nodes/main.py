import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Talker(Node):
    def __init__(self):
        super().__init__('talker')
        self.pub = self.create_publisher(String, 'chatter', 10)
        self.timer = self.create_timer(1.0, self.tick)
        self.count = 0

    def tick(self):
        msg = String()
        msg.data = f'hello {self.count}'
        self.pub.publish(msg)
        self.get_logger().info(f'Published: {msg.data}')
        self.count += 1

class Listener(Node):
    def __init__(self):
        super().__init__('listener')
        self.sub = self.create_subscription(String, 'chatter', self.on_msg, 10)

    def on_msg(self, msg):
        self.get_logger().info(f'Heard: {msg.data}')

def main(args=None):
    rclpy.init(args=args)

    talker = Talker()
    listener = Listener()

    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(talker)
    executor.add_node(listener)

    try:
        executor.spin()
    finally:
        talker.destroy_node()
        listener.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()