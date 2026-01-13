# 🚦 TRACE: Turtlebot for Reducing Adverse Congestion
**An Intelligent Transportation System (ITS) for Emergency Prioritization**

![Main Project Image](Pics/img%201.jpg)

[![ROS Noetic](https://img.shields.io/badge/ROS-Noetic-blue?logo=ros&logoColor=white)](http://wiki.ros.org/noetic)
[![Python 3.8](https://img.shields.io/badge/Python-3.8-yellow?logo=python&logoColor=white)](https://www.python.org/)
[![Ubuntu 20.04](https://img.shields.io/badge/OS-Ubuntu%2020.04-orange?logo=ubuntu&logoColor=white)](https://releases.ubuntu.com/20.04/)
[![IoT Enabled](https://img.shields.io/badge/IoT-Pushbullet-brightgreen)](https://www.pushbullet.com/)

## 📖 Overview
**TRACE** (Turtlebot for Reducing Adverse Congestion) is an advanced **Intelligent Transportation System** developed to address Egypt's "Grand Challenges" regarding urban congestion and environmental pollution. By leveraging **ICT, IoT, and Machine Learning**, the system manages a dynamic **"Green Corridor"**—an emergency lane that allows emergency vehicles (EVs) priority while opening to general traffic during peak congestion to optimize flow.

---

## 🚀 Key Features
* **Dynamic Lane Management:** Reallocates the emergency lane for general use based on real-time traffic density to reduce bottlenecks.
* **Emergency Vehicle Priority:** Instantly clears the "Green Corridor" upon detecting an emergency trigger, ensuring rapid transit for ambulances.
* **360° LiDAR Perception:** Utilizes a custom clustering algorithm to count vehicles and detect lane infractions with high precision.
* **IoT Notification System:** Sends real-time alerts to drivers via **Pushbullet** for congestion warnings and emergency lane clearing.
* **Remote Mission Control:** Features a web-based dashboard for long-distance monitoring and manual emergency overrides.

---

## 📊 Performance & Test Results
Project TRACE was evaluated against three measurable design requirements to ensure reliability and safety.

### **1. System Accuracy (Vehicle Counting)**
Using a depth discontinuity threshold ($\delta$) of 0.5m, the system identifies separate vehicles within a $0-90^{\circ}$ sector.
* **Standard Scenarios (1-5 cars):** 100% Accuracy.
* **Dense Scenarios (8+ cars):** 92% Accuracy.

![System Accuracy](Pics/par%201.gif)

### **2. Temporal Responsiveness (Latency)**
The system measures the interval between an emergency trigger and the output notification.
* **Average Response Time:** 0.425 seconds.
* **Safety Threshold:** < 3.0 seconds.

![Time Response](Pics/par%202.gif)

### **3. System Violation Test (Sensor Deviation)**
The system enforces a "2-meter" violation rule using LiDAR calibration to ensure enforcement integrity.
* **Average Deviation:** 3.4 cm (Well within the ±5cm requirement).

![System Violation Test](Pics/Par%203.gif)

---

## 🛠️ Tech Stack
### **Hardware**
| Component | Usage | Cost |
| :--- | :--- | :--- |
| **TurtleBot 3 Burger** | Primary mobile processing and enforcement unit. | Borrowed |
| **Raspberry Pi 4 (B)** | Cognitive layer hosting software and communication. | Included |
| **LiDAR Sensor** | 360° environment scanning and obstacle mapping. | Included |
| **Cars (5pcs)** | Simulate road traffic for the maquette environment. | 60 EGP/pc |

### **Software**
* **OS:** Ubuntu 20.04 (Focal Fossa).
* **Middleware:** ROS Noetic.
* **Language:** Python 3 (Logic) & JavaScript (Dashboard).
* **Communication:** Pushbullet API for IoT Notifications.

---

## 📜 Core Logic

### **Python: Traffic Marshall Node**
The main controller handles state management and executes robotic maneuvers based on LiDAR data.
```python
# snippet of emergency logic
def emergency_callback(self, msg):
    if msg.data == "START":
        self.mode = "EMERGENCY"
        self.emergency_start_time = time.time()
        self.set_lights("RED")
        # Send Notification
        self.send_notification("EMERGENCY CALL! Robot moving in 30s.")
