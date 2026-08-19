import os
import subprocess

import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class GestureBridge(Node):

    def __init__(self):
        super().__init__("gesture_bridge")

        self.publisher = self.create_publisher(
            String,
            "/gesture",
            10
        )

        vision_script = os.path.expanduser(
            "~/ros2_ws/src/gesture_turtle/gesture_turtle/gesture_vision.py"
        )

        venv_python = os.path.expanduser(
            "~/ros2_ws/.venv/bin/python"
        ) 
        self.process = subprocess.Popen(
            [
                venv_python,
                vision_script
            ],
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        self.timer = self.create_timer(
            0.01,
            self.read_gesture
        )

        self.get_logger().info("Gesture bridge started")

    def read_gesture(self):

        line = self.process.stdout.readline()

        if not line:
            return

        gesture = line.strip()

        if gesture == "":
            return

        msg = String()
        msg.data = gesture

        self.publisher.publish(msg)

        self.get_logger().info(
            f"Gesture: {gesture}"
        )

    def destroy_node(self):

        if self.process.poll() is None:
            self.process.terminate()

        super().destroy_node()


def main():

    rclpy.init()

    node = GestureBridge()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
