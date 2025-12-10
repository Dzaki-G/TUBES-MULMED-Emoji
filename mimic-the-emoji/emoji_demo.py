# emoji_demo.py
import cv2
from emoji_overlay import load_emoji_images
from gui_helpers import draw_floating_emojis
from emotion_utils import emoji_map

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
emoji_images = load_emoji_images("assets")
demo_emojis = list(emoji_map.keys())[:3]

print("Emoji demo — press Q to quit")
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # --- DETECT FACES ---
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # --- visualisasi haarcascades ---
    for (x, y, w, h) in faces:
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),     # green box
            2                # thickness
        )

    # Pick the first face for emoji "anchor"
    face_box = tuple(faces[0]) if len(faces) else None

    # --- DRAW EMOJIS ---
    draw_floating_emojis(frame, demo_emojis, emoji_images, face_box=face_box, size=100)

    # Scale display
    scale = 1.5
    resized_frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

    cv2.imshow("Emoji Demo", resized_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
