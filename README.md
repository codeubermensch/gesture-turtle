# ✋ Gesture-Controlled Turtle — ROS 2 + OpenCV + MediaPipe

A real-time computer-vision project that uses **hand gestures captured through a webcam to control a ROS 2 turtlesim robot**.

The project combines:

- **ROS 2 Jazzy** for robot communication and control
- **OpenCV** for webcam capture and image processing
- **MediaPipe Gesture Recognizer** for hand gesture detection
- **Python virtual environments** for isolating computer-vision dependencies
- **ROS 2 topics and messages** for communication between perception and control
- **turtlesim** as the simulated robot

![Gesture Controlled Turtle Demo](demo.gif)

---

## 📌 Project Overview

The goal of this project is to control a simulated robot without using a keyboard or joystick.

A webcam observes the user's hand, MediaPipe recognizes predefined gestures, and those gestures are converted into robot movement commands.

### Gesture → Robot Command

| Gesture | MediaPipe Label | Command | Turtle Action |
|:---:|---|---|---|
| ✋ | `Open_Palm` | `forward` | Move forward |
| ✊ | `Closed_Fist` | `stop` | Stop |
| 👍 | `Thumb_Up` | `left` | Rotate left |
| ✌️ | `Victory` | `right` | Rotate right |

---

# 🧠 System Architecture

The complete system is divided into two parts:

### Computer Vision

Runs inside a dedicated Python virtual environment because MediaPipe and OpenCV have their own Python dependencies.

### ROS 2

Runs using the normal ROS 2 Python environment and handles communication and robot control.

```text
                    ┌─────────────────────┐
                    │       Webcam        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       OpenCV        │
                    │   Frame Capture     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      MediaPipe      │
                    │  Gesture Recognizer │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  gesture_vision.py  │
                    │                     │
                    │ Gesture → Command   │
                    └──────────┬──────────┘
                               │
                         stdout / pipe
                               │
                               ▼
                    ┌─────────────────────┐
                    │  gesture_bridge.py  │
                    │       ROS 2 Node    │
                    └──────────┬──────────┘
                               │
                        /gesture
                     std_msgs/String
                               │
                               ▼
                    ┌─────────────────────┐
                    │ turtle_controller.py│
                    │       ROS 2 Node    │
                    └──────────┬──────────┘
                               │
                     /turtle1/cmd_vel
                   geometry_msgs/Twist
                               │
                               ▼
                    ┌─────────────────────┐
                    │      turtlesim      │
                    │         🐢          │
                    └─────────────────────┘
