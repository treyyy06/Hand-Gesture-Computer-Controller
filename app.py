import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import math

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# =====================================
# AUDIO SETUP
# =====================================

devices = AudioUtilities.GetSpeakers()

interface = devices.Activate(
    IAudioEndpointVolume._iid_,
    CLSCTX_ALL,
    None
)

volume = cast(
    interface,
    POINTER(IAudioEndpointVolume)
)

vol_range = volume.GetVolumeRange()
min_vol = vol_range[0]
max_vol = vol_range[1]

# =====================================
# SETTINGS
# =====================================

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

screen_w, screen_h = pyautogui.size()

SMOOTHENING = 5
FRAME_REDUCTION = 70
SENSITIVITY = 1.0

LEFT_CLICK_THRESHOLD = 0.045
RIGHT_CLICK_THRESHOLD = 0.035

SCROLL_THRESHOLD = 15

# =====================================
# STATE VARIABLES
# =====================================

prev_x = 0
prev_y = 0

scroll_y_prev = 0

left_click_cooldown = 0
right_click_cooldown = 0

# =====================================
# MEDIAPIPE
# =====================================

BaseOptions = python.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="models/hand_landmarker.task"
    ),
    num_hands=1,
    running_mode=VisionRunningMode.VIDEO
)

landmarker = HandLandmarker.create_from_options(
    options
)

# =====================================
# CAMERA
# =====================================

cap = cv2.VideoCapture(
    0,
    cv2.CAP_DSHOW
)

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    640
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    480
)

frame_timestamp = 0

# =====================================
# MAIN LOOP
# =====================================

while True:

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)

    frame_h, frame_w, _ = frame.shape

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    results = landmarker.detect_for_video(
        mp_image,
        frame_timestamp
    )

    frame_timestamp += 1

    x1 = FRAME_REDUCTION
    y1 = FRAME_REDUCTION

    x2 = frame_w - FRAME_REDUCTION
    y2 = frame_h - FRAME_REDUCTION

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (255, 0, 255),
        2
    )

    if results.hand_landmarks:

        hand = results.hand_landmarks[0]

        for landmark in hand:

            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)

            cv2.circle(
                frame,
                (x, y),
                4,
                (0, 255, 0),
                -1
            )

        # ==========================
        # LANDMARKS
        # ==========================

        thumb_tip = hand[4]
        index_tip = hand[8]
        middle_tip = hand[12]
        pinky_tip = hand[20]

        ix = int(index_tip.x * frame_w)
        iy = int(index_tip.y * frame_h)

        tx = int(thumb_tip.x * frame_w)
        ty = int(thumb_tip.y * frame_h)

        mx = int(middle_tip.x * frame_w)
        my = int(middle_tip.y * frame_h)

        px = int(pinky_tip.x * frame_w)
        py = int(pinky_tip.y * frame_h)

        # ==========================
        # CURSOR CONTROL
        # ==========================

        mouse_x = (
                ((ix - x1) * screen_w / (x2 - x1))
                * SENSITIVITY
        )

        mouse_y = (
                ((iy - y1) * screen_h / (y2 - y1))
                * SENSITIVITY
        )

        mouse_x = max(
            0,
            min(screen_w, mouse_x)
        )

        mouse_y = max(
            0,
            min(screen_h, mouse_y)
        )

        curr_x = prev_x + (
                mouse_x - prev_x
        ) / SMOOTHENING

        curr_y = prev_y + (
                mouse_y - prev_y
        ) / SMOOTHENING

        pyautogui.moveTo(
            curr_x,
            curr_y
        )

        prev_x = curr_x
        prev_y = curr_y

        # ==========================
        # LEFT CLICK
        # ==========================

        left_distance = math.hypot(
            thumb_tip.x - index_tip.x,
            thumb_tip.y - index_tip.y
        )

        if left_distance < LEFT_CLICK_THRESHOLD:

            if left_click_cooldown == 0:

                pyautogui.click()

                left_click_cooldown = 15

        # ==========================
        # RIGHT CLICK
        # ==========================

        right_distance = math.hypot(
            middle_tip.x - index_tip.x,
            middle_tip.y - index_tip.y
        )

        if right_distance < RIGHT_CLICK_THRESHOLD:

            if right_click_cooldown == 0:

                pyautogui.rightClick()

                right_click_cooldown = 15

        # ==========================
        # SCROLL
        # ==========================

        index_up = hand[8].y < hand[6].y
        middle_up = hand[12].y < hand[10].y

        if index_up and middle_up:

            current_y = iy

            if scroll_y_prev != 0:

                diff = scroll_y_prev - current_y

                if abs(diff) > SCROLL_THRESHOLD:

                    pyautogui.scroll(
                        int(diff * 3)
                    )

            scroll_y_prev = current_y

        else:
            scroll_y_prev = 0

        # ==========================
        # VOLUME CONTROL
        # Thumb ↔ Pinky
        # ==========================

        volume_distance = math.hypot(
            thumb_tip.x - pinky_tip.x,
            thumb_tip.y - pinky_tip.y
        )

        volume_distance = max(
            0.05,
            min(0.35, volume_distance)
        )

        volume_level = (
                (volume_distance - 0.05)
                / (0.35 - 0.05)
        )

        current_volume = (
                min_vol
                + volume_level
                * (max_vol - min_vol)
        )

        volume.SetMasterVolumeLevel(
            current_volume,
            None
        )

        volume_percent = int(
            volume_level * 100
        )

        cv2.line(
            frame,
            (tx, ty),
            (px, py),
            (255, 255, 0),
            3
        )

        cv2.putText(
            frame,
            f"VOL: {volume_percent}%",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            2
        )

        # ==========================
        # VISUALS
        # ==========================

        cv2.circle(
            frame,
            (ix, iy),
            10,
            (0, 0, 255),
            -1
        )

    if left_click_cooldown > 0:
        left_click_cooldown -= 1

    if right_click_cooldown > 0:
        right_click_cooldown -= 1

    cv2.imshow(
        "AirControl Ultimate",
        frame
    )

    if cv2.waitKey(1) & 0xFF == 27:
        break

# =====================================
# CLEANUP
# =====================================

cap.release()
cv2.destroyAllWindows()