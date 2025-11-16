# game_emotion.py
import cv2
import time
from emotion_utils import get_emotion, get_random_emojis, emoji_map
from emoji_overlay import load_emoji_images
from gui_helpers import draw_floating_emojis, draw_text_lines

# setup
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
emoji_images = load_emoji_images("assets")

# for fullscreen window
cv2.namedWindow("Emotion Match Game", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Emotion Match Game", 1600, 900)   # or 1920x1080


# attributes
score = 0
round_num = 1
round_emojis = get_random_emojis(3)
matched = set()
game_duration = 30
start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    face_box = tuple(faces[0]) if len(faces) else None

    # emotion detection
    detected = get_emotion(frame, enforce_detection=False)
    if detected:
        cv2.putText(frame, f"Detected: {detected}", (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2)

    # draw emojis
    draw_floating_emojis(frame, round_emojis, emoji_images, face_box=face_box, size=100, matched_emojis=matched)

    # matching logic
    for key in round_emojis:
        if detected == emoji_map[key] and key not in matched:
            score += 1
            matched.add(key)

    # next round
    if len(matched) == len(round_emojis):
        round_num += 1
        round_emojis = get_random_emojis(3)
        matched.clear()

    # HUD
    remaining = max(0, int(game_duration - (time.time() - start_time)))
    draw_text_lines(frame, [f"Round: {round_num}", f"Score: {score}", f"Time: {remaining}s"], start=(10,40))

    cv2.imshow("Emotion Match Game", frame)

    if cv2.waitKey(1) & 0xFF == ord('q') or remaining == 0:
        break

cap.release()
cv2.destroyAllWindows()
print("Time's up!" if remaining == 0 else "Quit")
print(f"Final score: {score}")
print(f"Rounds: {round_num - 1}")
