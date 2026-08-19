import os

import cv2
import mediapipe as mp


MODEL_PATH = os.path.expanduser("~/ros2_ws/models/gesture_recognizer.task")


BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
RunningMode = mp.tasks.vision.RunningMode


options = GestureRecognizerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=RunningMode.IMAGE
)

recognizer = GestureRecognizer.create_from_options(options)

cap = cv2.VideoCapture(0)

last_command = ""


def convert_gesture(gesture):

    if gesture == "Open_Palm":
        return "forward"

    if gesture == "Closed_Fist":
        return "stop"

    if gesture == "Thumb_Up":
        return "left"

    if gesture == "Victory":
        return "right"

    return "none"


while True:

    ret, frame = cap.read()

    if not ret:
        print("none", flush=True)
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    result = recognizer.recognize(mp_image)

    command = "none"

    if result.gestures:

        detected_gesture = result.gestures[0][0].category_name

        command = convert_gesture(detected_gesture)

    # Print only when command changes
    if command != last_command:

        print(command, flush=True)

        last_command = command

    cv2.putText(
        frame,
        command,
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (0, 255, 0),
        2
    )

    cv2.imshow("Gesture Vision", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()

cv2.destroyAllWindows()

recognizer.close()
