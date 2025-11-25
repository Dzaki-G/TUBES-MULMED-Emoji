from main_menu import show_main_menu, show_countdown
from game_over import show_game_over
import cv2
import time
from emotion_utils import get_emotion, get_random_emojis, emoji_map
from emoji_overlay import load_emoji_images
from gui_helpers import draw_floating_emojis, draw_text_lines, draw_simple_hud, draw_current_emotion
from audio_utils import init_audio, play_bgm, stop_bgm, play_sfx

def run_game(cap):
    # attributes
    score = 0
    round_num = 1
    round_emojis = get_random_emojis(3)
    matched = set()
    current_index = 0
    game_duration = 30
    start_time = time.time()

    # setup
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    emoji_images = load_emoji_images("assets")

    # loop game
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

        # draw emojis
        draw_floating_emojis(
            frame, round_emojis, emoji_images,
            face_box=face_box, size=100,
            matched_emojis=matched,
            current_index=current_index
        )

        draw_current_emotion(frame, detected, emoji_images)

        # logika untuk matching emoji dan detection
        if detected and current_index < len(round_emojis):
            key = round_emojis[current_index]
            if detected == emoji_map[key]:
                play_sfx("assets/audio/correct.mp3")
                matched.add(key)
                score += 1
                current_index += 1

                # next round
                if current_index == 3:
                    round_num += 1
                    matched.clear()
                    current_index = 0
                    round_emojis = get_random_emojis(3)

        # HUD
        remaining = max(0, int(game_duration - (time.time() - start_time)))
        draw_simple_hud(frame, round_num, score, remaining)

        cv2.imshow("Emotion Match Game", frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or remaining == 0:
            break

    return score


def main():
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Emotion Match Game", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Emotion Match Game", 1600, 900)
    init_audio()

    # Show main menu di awal
    while True:
        if not show_main_menu(cap):
            break

        show_countdown(cap)
        score = run_game(cap)

        # load high score
        try:
            highscore = int(open("highscore.txt").read())
        except:
            highscore = 0

        if score > highscore:
            highscore = score
            with open("highscore.txt", "w") as f:
                f.write(str(highscore))

        # Show game over screen
        action = show_game_over(cap, score, highscore)

        if action == "quit":
            break
        # if action == "menu": just loop again

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()