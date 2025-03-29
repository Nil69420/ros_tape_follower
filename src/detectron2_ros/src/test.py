#!/usr/bin/env python
import sys
import threading
import os

import cv2 as cv
import numpy as np
import rospy
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2.data.datasets.register_coco import register_coco_instances
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
import json

class TrackFollowerNode(object):
    def __init__(self):
        self._bridge = CvBridge()
        self._last_msg = None
        self._msg_lock = threading.Lock()

        self.cfg = get_cfg()
        # Add your Detectron2 configuration parameters here

        self._sub = rospy.Subscriber(rospy.get_param('~input'), Image, self._image_callback, queue_size=1)
        self._cmd_vel_pub = rospy.Publisher('~cmd_vel', Twist, queue_size=1)

        # Proportional control parameters
        self._kp_linear = 0.1  # Proportional gain for linear velocity
        self._kp_angular = 0.5  # Proportional gain for angular velocity

    def run(self):
        rate = rospy.Rate(10)  # adjust the rate based on your needs

        while not rospy.is_shutdown():
            if self._msg_lock.acquire(False):
                img_msg = self._last_msg
                self._last_msg = None
                self._msg_lock.release()
            else:
                rate.sleep()
                continue

            if img_msg is not None:
                np_image = self.convert_to_cv_image(img_msg)

                # Process the image using Detectron2 (replace with your detection logic)
                # Example: outputs = self.detect_objects(np_image)

                # Implement your logic to follow the track based on detection results
                # Example: cmd_vel = self.calculate_cmd_vel(outputs)
                cmd_vel = self.follow_track(np_image)

                # Publish the velocity command
                self._cmd_vel_pub.publish(cmd_vel)

            rate.sleep()

    def _image_callback(self, msg):
        rospy.logdebug("Get an image")
        if self._msg_lock.acquire(False):
            self._last_msg = msg
            self._msg_lock.release()

    def convert_to_cv_image(self, image_msg):
        try:
            cv_image = self._bridge.imgmsg_to_cv2(image_msg, desired_encoding="bgr8")
            return cv_image
        except CvBridgeError as e:
            rospy.logerr("CV Bridge Error: %s", str(e))
            return None

    def follow_track(self, image):
        # Convert image to grayscale for simplicity
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        # Apply edge detection (you may need to adjust parameters)
        edges = cv.Canny(gray, 50, 150)

        # Use HoughLines to detect lines in the image
        lines = cv.HoughLines(edges, 1, np.pi / 180, 100)

        cmd_vel = Twist()

        if lines is not None:
            for line in lines:
                rho, theta = line[0]
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))

                cv.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

                # Calculate the position error (difference between image center and line center)
                center_x = image.shape[1] // 2
                line_center_x = (x1 + x2) // 2
                error = center_x - line_center_x

                # Proportional control for linear and angular velocities
                cmd_vel.linear.x = self._kp_linear * error
                cmd_vel.angular.z = self._kp_angular * (theta - np.pi / 2)  # Adjust the angle as needed

        return cmd_vel

def main(argv):
    rospy.init_node('track_follower')
    node = TrackFollowerNode()
    node.run()

if __name__ == '__main__':
    main(sys.argv)