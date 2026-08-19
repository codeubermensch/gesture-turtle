import rclpy

from rclpy.node import Node

from std_msgs.msg import String

from geometry_msgs.msg import Twist


class TurtleController(Node):

    def __init__(self):

        super().__init__("turtle_controller")

        # Publisher: sends velocity commands to turtlesim
        self.publisher = self.create_publisher(
            Twist,
            "/turtle1/cmd_vel",
            10
        )

        # Subscriber: receives gestures
        self.subscription = self.create_subscription(
            String,
            "/gesture",
            self.gesture_callback,
            10
        )

        self.get_logger().info("Turtle controller started")

    def gesture_callback(self, msg):

        twist = Twist()

        if msg.data == "forward":

            twist.linear.x = 2.0
            twist.angular.z = 0.0

        elif msg.data == "left":

            twist.linear.x = 0.0
            twist.angular.z = 2.0

        elif msg.data == "right":

            twist.linear.x = 0.0
            twist.angular.z = -2.0

        elif msg.data == "stop":

            twist.linear.x = 0.0
            twist.angular.z = 0.0

        else:

            twist.linear.x = 0.0
            twist.angular.z = 0.0

        self.publisher.publish(twist)

        self.get_logger().info(
            f"Gesture: {msg.data}"
        )


def main():

    rclpy.init()

    node = TurtleController()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
