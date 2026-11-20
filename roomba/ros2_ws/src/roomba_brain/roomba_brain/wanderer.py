import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

import math

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class Wanderer(Node):
    def __init__(self):
        super().__init__('wanderer')

        # params
        self.declare_parameter('stop_distance', 0.2)    # m
        self.declare_parameter('forward_speed', 0.2)    # m/s
        self.declare_parameter('turn_speed', 0.8)       # rad/s
        self.declare_parameter('front_half_angle', 0.5) # rad +/- ard straight ahead

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(LaserScan, '/scan', self.scan_cb, qos_profile_sensor_data)
        self.timer = self.create_timer(0.1, self.tick)

        # readings
        self.front_min = None
        self.left_min = None
        self.right_min = None
        self.turn_dir = 1.0  # +1 = left, -1 = right

        self.get_logger().info('Wanderer with basic collision avoidance Started!')

    def scan_cb(self, msg: LaserScan):
        half = self.get_parameter('front_half_angle').value
        front, left, right = [], [], []

        for i, r in enumerate(msg.ranges):
            if not math.isfinite(r) or r < msg.range_min or r > msg.range_max:
                continue # drop out of range readings
            angle = msg.angle_min + i * msg.angle_increment
            angle = math.atan2(math.sin(angle), math.cos(angle)) # normalize to [-pi, pi]

            if abs(angle) <= half:
                front.append(r)
            elif 0 < angle <= math.pi / 2:
                left.append(r)
            elif -math.pi / 2 <= angle < 0:
                right.append(r)

        # if nothing valid then treat as clear
        self.front_min = min(front) if front else msg.range_max
        self.left_min = min(left) if left else msg.range_max
        self.right_min = min(right) if right else msg.range_max

    def tick(self):
        if self.front_min is None:
            return # no readings yet
        
        stop = self.get_parameter('stop_distance').value
        cmd = Twist()

        if self.front_min < stop:
            # blocked, stop and turn towards side with more space
            self.turn_dir = 1.0 if self.left_min >= self.right_min else -1.0
            cmd.angular.z = self.turn_dir * self.get_parameter('turn_speed').value
        else:
            # clear go froward
            cmd.linear.x = self.get_parameter('forward_speed').value

        self.pub.publish(cmd)


def main():
    rclpy.init()
    node = Wanderer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()