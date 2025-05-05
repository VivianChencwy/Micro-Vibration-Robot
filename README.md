# Vision-Controlled Vibrating Robot

This project develops a **micro vibrating robot** controlled via computer vision, designed to explore motion and communication in swarm robotics. The robot uses vibration motors for movement, an ESP8285 for WiFi communication, and ArUco markers for precise positioning. The system enables single-robot path planning and aims to extend to multi-robot swarm control.

## Features

- **Vision-Based Control**: Tracks robot position using ArUco markers and OpenCV for real-time path planning.
- **Vibration-Driven Movement**: Dual motors enable planar motion and steering via differential vibration.
- **WiFi Communication**: ESP8285 module connects the robot to a PC for command execution.
- **Hardware Design**: Custom PCB with ESP01F, CH340C USB-to-serial, TP4059 charging circuit, and 3.3V LDO.
- **Scalable Swarm Control**: Foundation for dynamic path planning of multiple robots.

## Why It Matters

Swarm robotics leverages coordinated robot groups for tasks like exploration or surveillance. This project focuses on a single micro-robot's motion control using vision-based feedback, laying the groundwork for scalable swarm behaviors.

## Implementation

### Hardware
- **Motion Principle**: Two vibration motors (top/bottom) generate periodic thrust via eccentric masses. Differential motor speeds control direction and speed.
- **Main Components**:
  - **ESP8285 (ESP01F)**: WiFi module for PC-robot communication and motor control.
  - **CH340C**: USB-to-serial module for wired communication and programming.
  - **TP4059**: Charging circuit for battery management.
  - **3.3V LDO**: Regulates power for stable operation.
  - **Vibration Motors**: Drive planar motion.
- **PCB Design**: Custom board integrates components (note: GND routing issue fixed in design).

### Software
- **Upper Computer (PC)**:
  - Uses Python with OpenCV for ArUco marker detection and path visualization.
  - Calculates robot angles and distances to waypoints, sending motor commands via UDP.
  - Sample code draws paths on video feed and adjusts motor speeds based on position errors.
- **Lower Computer (Robot)**:
  - Runs on ESP8285 using Arduino framework.
  - Handles WiFi connection and UDP packet parsing for motor control.
  - Code snippet:
    ```cpp
    void loop() {
      maintainWiFiConnection();
      int packetSize = Udp.parsePacket();
      if (packetSize) {
        int n = Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
        packetBuffer[n] = 0;
        sscanf(packetBuffer, "M1:%d, M2:%d", &power1, &power2);
        if (power1 < 0) {
          analogWrite(M1, -power1);
          analogWrite(M2, -power2);
          delay(100);
          analogWrite(M1, 0);
          analogWrite(M2, 0);
        } else {
          analogWrite(M1, power1);
          analogWrite(M2, power2);
        }
      }
    }
    ```

### Tech Stack
- **Python**: OpenCV for vision processing, UDP for communication.
- **C++ (Arduino)**: ESP8266WiFi and WiFiUDP libraries for robot firmware.
- **Hardware**: ESP8285, CH340C, TP4059, vibration motors.

## Getting Started

### Prerequisites
- Hardware: ESP01F module, CH340C USB-to-serial, TP4059 charging circuit, vibration motors, custom PCB.
- Software: Python 3.x, OpenCV, Arduino IDE, ESP8266 board support.
- Camera: For ArUco marker detection.

### Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/vision-controlled-robot.git


Install Python Dependencies:pip install opencv-python numpy


Configure Arduino:
Install ESP8266 board support in Arduino IDE.
Upload the lower computer code (firmware.ino) to the ESP01F.


Prepare Hardware:
Assemble the PCB with components.
Attach ArUco markers to the robot.


Run the System:
Launch the Python script (vision_control.py) on the PC.
Connect the robot via WiFi or USB.
Define waypoints in the UI to control robot movement.




