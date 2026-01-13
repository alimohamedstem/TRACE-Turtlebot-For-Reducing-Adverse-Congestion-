#!/usr/bin/env python3
import rospy
import time
import math
import RPi.GPIO as GPIO
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from pushbullet import Pushbullet

# ================= CONFIGURATION =================
PUSHBULLET_API_KEY = "# ================= Your-API ================="

# GPIO PINS
RED_PIN = 17
YELLOW_PIN = 27
GREEN_PIN = 22

# TIMED MOVEMENT SETTINGS
MOVE_SPEED = 0.1
TURN_SPEED = 0.3
TIME_FOR_50CM = 5.0
TIME_FOR_90DEG = 5.2 

# TOY CAR DETECTION SETTINGS
MAX_VIEW_DIST = 1.5
GAP_THRESHOLD = 0.05
MIN_OBJ_WIDTH = 3
# =================================================

class TrafficMarshallBot:
    def __init__(self):
        rospy.init_node('traffic_marshall_bot')
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RED_PIN, GPIO.OUT)
        GPIO.setup(YELLOW_PIN, GPIO.OUT)
        GPIO.setup(GREEN_PIN, GPIO.OUT)
        
        self.set_lights("RED")

        # Connect Pushbullet (WITH ERROR PRINTING)
        self.pb = None
        print("DEBUG: Connecting to Pushbullet...")
        try:
            self.pb = Pushbullet(PUSHBULLET_API_KEY)
            print("DEBUG: Pushbullet Connected Successfully!")
            self.pb.push_note("System Online", "Traffic Bot Started.")
        except Exception as e:
            print(f"ERROR: Pushbullet Connection FAILED: {e}")
            self.pb = None

        # ROS Connections
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.scan_sub = rospy.Subscriber('/scan', LaserScan, self.scan_callback)
        self.emergency_sub = rospy.Subscriber('/emergency_trigger', String, self.emergency_callback)

        self.mode = "NORMAL" 
        self.emergency_start_time = None
        self.action_1_done = False 
        self.action_2_done = False 
        self.last_print_time = 0

        print("System Ready. Scanning FULL 360 DEGREES for Toy Cars.")

    def set_lights(self, color):
        GPIO.output(RED_PIN, GPIO.LOW)
        GPIO.output(YELLOW_PIN, GPIO.LOW)
        GPIO.output(GREEN_PIN, GPIO.LOW)
        if color == "RED": GPIO.output(RED_PIN, GPIO.HIGH)
        elif color == "GREEN": GPIO.output(GREEN_PIN, GPIO.HIGH)
        elif color == "YELLOW": GPIO.output(YELLOW_PIN, GPIO.HIGH)

    def emergency_callback(self, msg):
        if msg.data == "START":
            self.mode = "EMERGENCY"
            self.emergency_start_time = time.time()
            self.action_1_done = False
            self.action_2_done = False
            self.set_lights("RED")
            
            # Send Notification
            self.send_notification("EMERGENCY CALL! Robot moving in 30s.")
            print("!!! EMERGENCY MODE STARTED !!!")
            
        elif msg.data == "STOP":
            self.mode = "NORMAL"
            self.emergency_start_time = None
            self.set_lights("RED")
            print("--- Normal Mode Restored ---")

    def move_robot(self, linear, angular, duration):
        move = Twist()
        move.linear.x = linear
        move.angular.z = angular
        
        start = time.time()
        while time.time() - start < duration:
            self.cmd_vel_pub.publish(move)
            time.sleep(0.1)
        
        move.linear.x = 0.0
        move.angular.z = 0.0
        self.cmd_vel_pub.publish(move)

    def scan_callback(self, scan):
        ranges = [x if x > 0.02 else 10.0 for x in scan.ranges]
        
        # Count Objects (360)
        all_points = ranges
        car_count = 0
        current_obj_width = 0 
        prev_dist = all_points[0]
        
        for dist in all_points:
            if dist < MAX_VIEW_DIST:
                if abs(dist - prev_dist) > GAP_THRESHOLD:
                    if current_obj_width > MIN_OBJ_WIDTH:
                        car_count += 1
                    current_obj_width = 0
                current_obj_width += 1
                prev_dist = dist
            else:
                if current_obj_width > MIN_OBJ_WIDTH:
                    car_count += 1
                    current_obj_width = 0
                prev_dist = dist

        # Print Status
        if time.time() - self.last_print_time > 1.0:
            status = f"Mode: {self.mode}"
            if self.mode == "EMERGENCY":
                elapsed = int(time.time() - self.emergency_start_time)
                status += f" (Time: {elapsed}s)"
            
            print(f"🏎️ 360° Scan: Found {car_count} objects | {status}")
            self.last_print_time = time.time()

        # Traffic Logic
        if self.mode == "NORMAL":
            if car_count >= 4:
                self.mode = "CONGESTION"
                self.set_lights("GREEN")
                self.send_notification(f"Congestion! I see {car_count} objects.")
        elif self.mode == "CONGESTION":
            if car_count < 2:
                self.mode = "NORMAL"
                self.set_lights("RED")

        # Emergency Sequence
        if self.mode == "EMERGENCY" and self.emergency_start_time is not None:
            elapsed = time.time() - self.emergency_start_time
            
            if elapsed > 30 and not self.action_1_done:
                print("⚡ T+30s: Clearing Way...")
                self.set_lights("YELLOW")
                self.move_robot(-MOVE_SPEED, 0.0, TIME_FOR_50CM)
                self.move_robot(0.0, TURN_SPEED, TIME_FOR_90DEG)
                self.set_lights("RED")
                self.action_1_done = True

            if elapsed > 60 and not self.action_2_done:
                print("⚡ T+60s: Returning...")
                self.set_lights("YELLOW")
                self.move_robot(0.0, -TURN_SPEED, TIME_FOR_90DEG)
                self.move_robot(MOVE_SPEED, 0.0, TIME_FOR_50CM)
                self.set_lights("RED")
                self.action_2_done = True
                self.send_notification("Emergency Ended. Robot returned.")

    def send_notification(self, text):
        if self.pb:
            try:
                self.pb.push_note("Traffic Bot", text)
                print(f"DEBUG: SENT NOTIFICATION -> {text}")
            except Exception as e:
                print(f"ERROR: Failed to send notification: {e}")
        else:
            print("DEBUG: Pushbullet is NOT Connected. Cannot send message.")

if __name__ == '__main__':
    try:
        TrafficMarshallBot()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    finally:
        GPIO.cleanup()
