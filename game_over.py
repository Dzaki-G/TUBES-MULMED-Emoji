import cv2
import time
from audio_utils import play_sfx

def show_game_over(cap, score, highscore):
    window_name = "Emotion Match Game"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1600, 900)

    play_sfx("assets/audio/confeti.mp3")
    play_sfx("assets/audio/yay.mp3")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        blur = cv2.GaussianBlur(frame, (35, 35), 0)

        h, w = blur.shape[:2]

        # ----- Title -----
        title = "GAME OVER"
        title_scale = w / 1600 * 2.5
        title_thickness = int(w / 1600 * 6)

        cv2.putText(
            blur, title,
            (int(w * 0.30), int(h * 0.22)),
            cv2.FONT_HERSHEY_SIMPLEX,
            title_scale, (0, 200, 255), title_thickness
        )

        # ----- Score -----
        score_scale = w / 1600 * 1.7
        score_thick = int(w / 1600 * 4)

        cv2.putText(
            blur,
            f"Your Score: {score}",
            (int(w * 0.32), int(h * 0.42)),
            cv2.FONT_HERSHEY_SIMPLEX,
            score_scale, (255,255,255), score_thick
        )

        cv2.putText(
            blur,
            f"High Score: {highscore}",
            (int(w * 0.32), int(h * 0.52)),
            cv2.FONT_HERSHEY_SIMPLEX,
            score_scale, (255,255,255), score_thick
        )

        # ----- MENU BUTTON -----
        button_w = int(w * 0.25)
        button_h = int(h * 0.12)
        button_x = (w - button_w) // 2
        button_y = int(h * 0.67)

        overlay = blur.copy()
        alpha = 0.4

        cv2.rectangle(
            overlay,
            (button_x, button_y),
            (button_x + button_w, button_y + button_h),
            (0,255,0), -1
        )
        cv2.addWeighted(overlay, alpha, blur, 1 - alpha, 0, blur)

        # text
        btn_scale = w / 1600 * 2
        btn_thick = int(w / 1600 * 4)

        cv2.putText(
            blur,
            "MENU",
            (button_x + int(button_w * 0.22), button_y + int(button_h * 0.70)),
            cv2.FONT_HERSHEY_SIMPLEX,
            btn_scale, (0,0,0), btn_thick
        )

        cv2.imshow(window_name, blur)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('m'):     # back to main menu
            return "menu"
        if key == ord('q'):
            return "quit"
