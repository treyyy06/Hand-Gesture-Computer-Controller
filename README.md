# AirControl Ultimate – Hand Gesture Computer Controller

AirControl Ultimate is a computer vision-based Human-Computer Interaction (HCI) project that enables users to control their computer using hand gestures. The system uses a webcam, MediaPipe Hand Landmarker, OpenCV, and Python to track hand movements and translate them into mouse and system control actions.

## Features

### Mouse Control
- Move cursor using index finger movement
- Smooth cursor tracking
- Adjustable sensitivity

### Click Actions
- Left Click: Thumb + Index finger pinch
- Right Click: Index + Middle finger pinch

### Scrolling
- Scroll Up and Down using two-finger gesture movement

### Volume Control
- Control system volume using hand gestures
- Real-time volume adjustment

### Real-Time Visual Feedback
- Hand landmark visualization
- Gesture recognition indicators
- Distance measurements
- Active tracking region display

---

## Technologies Used

- Python
- OpenCV
- MediaPipe Tasks API
- PyAutoGUI
- Pycaw (Windows Audio Control)
- NumPy

---

## Project Architecture

1. Webcam captures live video feed.
2. MediaPipe detects and tracks hand landmarks.
3. Gesture recognition module identifies specific hand gestures.
4. Actions are mapped to system controls:
   - Mouse movement
   - Clicking
   - Scrolling
   - Volume control
5. Visual feedback is displayed on screen.

---

## Hand Gestures

| Gesture | Action |
|----------|----------|
| Index Finger Movement | Cursor Movement |
| Thumb + Index Pinch | Left Click |
| Index + Middle Pinch | Right Click |
| Two Fingers Up | Scroll Mode |
| Thumb + Pinky Distance | Volume Control |

---

## Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/AirControlUltimate.git
cd AirControlUltimate
