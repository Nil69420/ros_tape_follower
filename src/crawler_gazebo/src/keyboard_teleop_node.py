#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
import sys, select, termios, tty

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def teleop():
    rospy.init_node('keyboard_teleop_node')
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rate = rospy.Rate(10)  # 10 Hz
    twist = Twist()

    try:
        print("Use arrow keys to control the robot. Press 'q' to quit.")
        while not rospy.is_shutdown():
            key = getKey()
            if key == '\x03' or key == 'q':  # Ctrl-C or 'q' to exit
                break

            if key == 'w':
                twist.linear.x = 20.0
            elif key == 's':
                twist.linear.x = -20.0
            else:
                twist.linear.x = 0.0

            if key == 'a':
                twist.angular.z = 30.0
            elif key == 'd':
                twist.angular.z = -30.0
            else:
                twist.angular.z = 0.0

            pub.publish(twist)
            rate.sleep()

    except rospy.ROSInterruptException:
        pass

if __name__ == '__main__':
    settings = termios.tcgetattr(sys.stdin)
    try:
        teleop()
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)