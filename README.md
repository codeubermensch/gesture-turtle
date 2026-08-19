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

🔄 Complete Data Flow

For example, when the user shows an open palm:

1. Webcam
      ↓
2. OpenCV captures frame
      ↓
3. MediaPipe recognizes Open_Palm
      ↓
4. gesture_vision.py maps it to "forward"
      ↓
5. "forward" is printed to stdout
      ↓
6. gesture_bridge.py reads stdout
      ↓
7. Publishes "forward" on /gesture
      ↓
8. turtle_controller.py receives "forward"
      ↓
9. Creates a Twist message
      ↓
10. Publishes Twist on /turtle1/cmd_vel
      ↓
11. turtlesim moves forward
📁 Project Structure
gesture_turtle/
│
├── gesture_turtle/
│   ├── __init__.py
│   ├── gesture_vision.py
│   ├── gesture_bridge.py
│   └── turtle_controller.py
│
├── resource/
│   └── gesture_turtle
│
├── test/
│   ├── test_copyright.py
│   ├── test_flake8.py
│   └── test_pep257.py
│
├── .gitignore
├── demo.gif
├── package.xml
├── setup.cfg
├── setup.py
└── README.md
📄 Code Explanation
gesture_vision.py

This is the computer vision and gesture recognition layer.

It:

Opens the webcam using OpenCV.
Captures frames continuously.
Converts the OpenCV BGR frame to RGB.
Passes the frame to MediaPipe.
Runs the MediaPipe Gesture Recognizer.
Extracts the detected gesture.
Maps the gesture to a simple robot command.
Prints the command to standard output.

The mapping is:

Open_Palm    → forward
Closed_Fist  → stop
Thumb_Up     → left
Victory      → right

For example:

MediaPipe:
Open_Palm


gesture_vision.py:
forward

The script prints the command to stdout so that another process can consume it.

flush=True is used when printing commands so that the bridge receives the output immediately rather than waiting for Python's output buffer.

gesture_bridge.py

gesture_bridge.py is the ROS 2 interface between the computer vision system and the ROS system.

It is a ROS 2 node.

Instead of importing MediaPipe itself, it starts gesture_vision.py as a subprocess using the Python interpreter from the dedicated virtual environment.

Conceptually:

.venv Python
     │
     ▼
gesture_vision.py
     │
     │ stdout
     ▼
gesture_bridge.py
     │
     │ ROS topic
     ▼
/gesture

The bridge reads commands such as:

forward
stop
left
right

and publishes them using:

std_msgs/msg/String

on:

/gesture
turtle_controller.py

This is the robot control layer.

It subscribes to:

/gesture

using:

std_msgs/msg/String

It then translates the semantic command into a velocity command.

Velocity mapping
forward:
    linear.x  = 2.0
    angular.z = 0.0


left:
    linear.x  = 0.0
    angular.z = 2.0


right:
    linear.x  = 0.0
    angular.z = -2.0


stop:
    linear.x  = 0.0
    angular.z = 0.0

The resulting message is published to:

/turtle1/cmd_vel

using:

geometry_msgs/msg/Twist
📡 ROS 2 Communication

The project uses two main ROS topics.

/gesture
Publisher:
    gesture_bridge.py


Subscriber:
    turtle_controller.py


Message:
    std_msgs/msg/String

Example:

data: forward

This topic represents a semantic command.

It does not directly contain robot velocity information.

/turtle1/cmd_vel
Publisher:
    turtle_controller.py


Subscriber:
    turtlesim


Message:
    geometry_msgs/msg/Twist

This topic contains the actual velocity command.

❓ Why Use String for /gesture?

The perception system only needs to communicate high-level commands:

forward
stop
left
right

Therefore:

std_msgs/msg/String

is sufficient.

The controller converts the semantic command into a robot-specific velocity command.

This creates a clean separation:

Perception
    ↓
"forward"
    ↓
ROS interface
    ↓
Controller
    ↓
Twist
    ↓
Robot

The perception system therefore does not need to know how the robot is physically controlled.

❓ Why Use Twist for /turtle1/cmd_vel?

turtlesim expects velocity commands using:

geometry_msgs/msg/Twist

A Twist contains linear and angular velocity:

linear:
    x
    y
    z


angular:
    x
    y
    z

For this 2D project, the important fields are:

linear.x
angular.z

Therefore:

forward
    ↓
linear.x > 0

and:

left / right
    ↓
angular.z
🐍 Python Virtual Environment

One of the main technical challenges in this project was integrating MediaPipe with ROS 2 Jazzy's Python environment.

MediaPipe and OpenCV were installed inside:

~/ros2_ws/.venv/

while ROS 2 uses the system Python environment.

The final project intentionally keeps these environments separate.

Why was this necessary?

Initially, the idea was to make the ROS node directly import MediaPipe:

import mediapipe

However, when running the ROS executable, Python reported:

ModuleNotFoundError: No module named 'mediapipe'

Checking the Python interpreters showed the problem:

python
/home/maithresh/ros2_ws/.venv/bin/python


ros2
/opt/ros/jazzy/bin/ros2

The ROS-generated Python executable was using:

/usr/bin/python3

while MediaPipe was installed in:

~/ros2_ws/.venv/

Activating the virtual environment did not change the interpreter used by the already-installed ROS executable.

⚠️ Another Problem: System Python Package Installation

Ubuntu 24.04 protects the system Python environment using PEP 668.

Trying to install MediaPipe directly using:

python3 -m pip install mediapipe

resulted in:

error: externally-managed-environment

Using --break-system-packages was also undesirable because it could modify packages used by the system and ROS.

We also encountered a NumPy compatibility problem when MediaPipe was installed outside the isolated environment.

The error indicated that some installed modules had been compiled against NumPy 1.x while the environment contained NumPy 2.x.

Rather than modifying system packages and potentially breaking ROS dependencies, the computer vision stack was isolated.

✅ Final Solution: Separate Python Processes

The final architecture is:

┌─────────────────────────────────────┐
│       Python Virtual Environment    │
│                                     │
│  MediaPipe                          │
│  OpenCV                             │
│  NumPy                              │
│                                     │
│  gesture_vision.py                  │
└──────────────────┬──────────────────┘
                   │
                   │ stdout
                   ▼
┌─────────────────────────────────────┐
│          ROS 2 Environment          │
│                                     │
│  rclpy                              │
│  std_msgs                            │
│  geometry_msgs                       │
│                                     │
│  gesture_bridge.py                  │
│  turtle_controller.py               │
└─────────────────────────────────────┘

The two environments communicate through a simple process interface.

This avoids forcing MediaPipe dependencies into ROS 2's Python environment.

🧠 Why This Architecture Is Useful

The project separates:

Perception
Camera
 ↓
OpenCV
 ↓
MediaPipe
 ↓
Gesture
Communication
Gesture
 ↓
ROS topic
Control
ROS command
 ↓
Twist
 ↓
Robot

This means the controller does not care how the gesture was detected.

The perception layer could later be replaced with:

MediaPipe
    │
    ├── another vision model
    ├── YOLO
    ├── voice recognition
    ├── joystick
    └── another sensor
          ↓
       /gesture
          ↓
      Controller

This is the same general idea used in larger robotics systems: keep perception, communication, and control modular.

⚙️ Installation
Requirements
Ubuntu 24.04
ROS 2 Jazzy
Python 3.12
Webcam
OpenCV
MediaPipe
turtlesim
colcon
1. Create / use a ROS 2 workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

Clone the repository:

git clone <YOUR_REPOSITORY_URL>

The package should be located at:

~/ros2_ws/src/gesture_turtle
2. Create the Python Virtual Environment

From the ROS workspace:

cd ~/ros2_ws

Create the environment:

python3 -m venv .venv

Activate it:

source .venv/bin/activate

Install the computer vision dependencies:

python -m pip install mediapipe opencv-python

Verify MediaPipe:

python -c "import mediapipe; print(mediapipe.__version__)"

Verify OpenCV:

python -c "import cv2; print(cv2.__version__)"
3. MediaPipe Model

The project requires the MediaPipe Gesture Recognizer model:

gesture_recognizer.task

The model is intentionally not committed to this repository.

Place it locally at:

~/ros2_ws/models/gesture_recognizer.task

The resulting workspace should look like:

ros2_ws/
├── .venv/
├── models/
│   └── gesture_recognizer.task
└── src/
    └── gesture_turtle/

The .task files are excluded using .gitignore.

4. Build the ROS Package

Deactivate the virtual environment:

deactivate

Source ROS 2 Jazzy:

source /opt/ros/jazzy/setup.bash

Build the package:

cd ~/ros2_ws
colcon build --packages-select gesture_turtle

Source the workspace:

source ~/ros2_ws/install/setup.bash
▶️ Running the Project

The project currently uses three terminals.

Terminal 1 — Start turtlesim
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtlesim_node

This starts the simulated turtle.

Terminal 2 — Start the Controller
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash


ros2 run gesture_turtle turtle_controller

The controller subscribes to:

/gesture
Terminal 3 — Start the Gesture Bridge
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash


ros2 run gesture_turtle gesture_bridge

The webcam window should open.

Perform the gestures and observe the turtle.

🧪 Testing Individual Components
Test Gesture Recognition Without ROS

Activate the virtual environment:

cd ~/ros2_ws
source .venv/bin/activate

Run:

python src/gesture_turtle/gesture_turtle/gesture_vision.py

The webcam window should open and gesture commands should be detected.

Example:

forward
stop
left
right

Press q to close the camera.

🔍 Inspect ROS Topics

Check available topics:

ros2 topic list

You should see:

/gesture
/turtle1/cmd_vel
Monitor Gesture Commands
ros2 topic echo /gesture

Example:

data: forward
Inspect Gesture Topic
ros2 topic info /gesture
Monitor Robot Velocity
ros2 topic echo /turtle1/cmd_vel

Example:

linear:
  x: 2.0
angular:
  z: 0.0
🛠️ Common Problems and Solutions
ModuleNotFoundError: No module named 'mediapipe'

Make sure the vision environment is activated:

source ~/ros2_ws/.venv/bin/activate

Then verify:

python -c "import mediapipe"

Remember that the ROS nodes themselves do not import MediaPipe.

externally-managed-environment

Do not install MediaPipe directly into Ubuntu's system Python.

Instead:

python3 -m venv .venv
source .venv/bin/activate
python -m pip install mediapipe opencv-python
ROS package is not found

Source both ROS and the workspace:

source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash

Then:

ros2 pkg list | grep gesture_turtle
Python changes are not reflected

Rebuild:

cd ~/ros2_ws
colcon build --packages-select gesture_turtle
source install/setup.bash

Then run the node again.

Camera does not open

Check available video devices:

ls /dev/video*

Also verify that OpenCV can access the webcam from the virtual environment.

✏️ Customization
Change Gesture Mapping

Modify:

gesture_vision.py

For example:

Open_Palm → forward

can be changed to another command.

Change Turtle Speed

Modify the velocity values in:

turtle_controller.py

For example:

twist.linear.x = 2.0

can be changed to:

twist.linear.x = 1.0

for slower forward motion.

Similarly:

twist.angular.z = 2.0

controls rotational speed.

Change the /gesture Topic

The topic is created in:

gesture_bridge.py

and subscribed to in:

turtle_controller.py

If the topic name is changed, both sides must use the same name.

🧩 ROS 2 Concepts Demonstrated

This project provides hands-on experience with:

Nodes

Independent ROS 2 processes responsible for specific functions.

gesture_bridge
turtle_controller
Publishers

Publishing commands to:

/gesture
/turtle1/cmd_vel
Subscribers

turtle_controller subscribes to:

/gesture
Topics

ROS 2 topics provide asynchronous communication between components.

Message Types
/gesture
    ↓
std_msgs/msg/String


/turtle1/cmd_vel
    ↓
geometry_msgs/msg/Twist
Packages

The project is implemented as an ament_python ROS 2 package.

Workspace and Build System

The package is built using:

colcon
🧮 Why Not Send Twist Directly From MediaPipe?

A possible alternative would be:

MediaPipe
   ↓
Twist
   ↓
/cmd_vel

However, that would tightly couple the perception system to the robot's control interface.

Instead, this project uses:

Gesture
   ↓
/gesture
   ↓
Controller
   ↓
Twist
   ↓
/cmd_vel

This creates a semantic command layer.

For example:

"forward"

doesn't imply how a particular robot must move.

The controller decides how "forward" should be converted into motion.

This makes the system easier to adapt to another robot.

🔐 Repository Hygiene

The repository intentionally does not contain:

.venv/
build/
install/
log/
*.task

These are either:

generated build artifacts
local Python environments
machine-specific dependencies
large binary model files

The repository therefore contains the source code and configuration required to understand and reproduce the project, rather than the entire development environment.

🔮 Future Improvements

The current project is a working proof-of-concept. Possible extensions include:

1. Safety / Obstacle Detection

Add a safety layer between gesture commands and velocity commands:

Gesture
   ↓
Safety Check
   ↓
Allowed?
 ┌─┴───────┐
Yes       No
 ↓         ↓
Twist     Stop

This would prevent a forward gesture from commanding motion when an obstacle is detected.

2. Gesture Confidence Filtering

MediaPipe predictions could be filtered over multiple frames to prevent accidental movement caused by temporary misclassification.

3. More Gestures

Additional commands could include:

Backward
Speed Up
Speed Down
Emergency Stop
4. ROS Parameters

Move hard-coded values such as:

linear_speed
angular_speed

into ROS parameters.

5. Launch File

Create a ROS 2 launch file to start the complete ROS system with a single command.

6. Physical Robot

The turtlesim controller can eventually be replaced with a controller for a real mobile robot.

The high-level architecture could remain:

Camera
  ↓
Gesture Recognition
  ↓
/gesture
  ↓
Robot Controller
  ↓
/cmd_vel
  ↓
Physical Robot
7. Better ROS Interface

A custom ROS message could eventually replace the string-based interface:

GestureCommand.msg


gesture
confidence
timestamp

This would allow richer communication between perception and control.

📚 Key Learning Outcomes

Through this project, the following concepts were implemented and debugged in practice:

Robotics
ROS 2 architecture
Perception → communication → control pipeline
Velocity control
Linear and angular velocity
Modular robot control
ROS 2
rclpy
Nodes
Publishers
Subscribers
Topics
std_msgs/msg/String
geometry_msgs/msg/Twist
colcon
ament_python
ROS 2 CLI
Computer Vision
Webcam capture
OpenCV
BGR → RGB conversion
MediaPipe
Real-time gesture recognition
Gesture-to-command mapping
Python / Linux
Python virtual environments
PEP 668
Dependency isolation
subprocess communication
stdout pipes
Linux development workflow
Software Engineering
Modular architecture
Process isolation
Interface-based communication
Dependency management
Git/GitHub
Debugging environment and dependency conflicts
