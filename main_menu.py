
# main_menu.py
import cv2
import numpy as np
import time
from PIL import Image, ImageDraw, ImageFont
from audio_utils import play_sfx

# ============================
#   Mouse Global State
# ============================
mouse_clicked = False
mouse_x, mouse_y = 0, 0

def mouse_callback(event, x, y, flags, param):
    global mouse_clicked, mouse_x, mouse_y
    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_clicked = True
        mouse_x, mouse_y = x, y


# ============================
#   TEXT WITH CUSTOM FONT
# ============================
def draw_text_custom(frame, text, pos, size=80, color=(255,255,255),
                     font_path="assets/fonts/Montserrat-Bold.ttf",
                     center=False):

    img_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(font_path, size)

    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    if center:
        pos = (pos[0] - w//2, pos[1] - h//2)

    draw.text(pos, text, font=font, fill=color)
    return np.array(img_pil)


# ============================
#   OVERLAY PNG TRANSPARAN
# ============================
def overlay_png(base, img_png, x, y):
    h, w = img_png.shape[:2]

    if y + h > base.shape[0] or x + w > base.shape[1]:
        return base

    if img_png.shape[2] == 4:
        b, g, r, a = cv2.split(img_png)
        overlay_color = cv2.merge((b, g, r))
        mask = a / 255.0

        for c in range(3):
            base[y:y+h, x:x+w, c] = (
                base[y:y+h, x:x+w, c] * (1 - mask) +
                overlay_color[:, :, c] * mask
            )

    return base


# ============================
#      MAIN MENU
# ============================
def show_main_menu(cap):
    global mouse_clicked, mouse_x, mouse_y

    window_name = "Emotion Match Game"

    # Aktifkan mouse listener
    cv2.setMouseCallback(window_name, mouse_callback)

    # load PNG button sekali saja
    start_btn = cv2.imread("assets/ui/startButton.png", cv2.IMREAD_UNCHANGED)

    if start_btn is None:
        print("ERROR: File assets/ui/startButton.png tidak ditemukan!")
        return False

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        blur = cv2.GaussianBlur(frame, (35, 35), 0)

        # Dark overlay smooth
        overlay_alpha = 0.5   # ubah jadi 0.35–0.50 sesuai selera
        dark = np.zeros_like(blur)

        blur = cv2.addWeighted(blur, 1 - overlay_alpha, dark, overlay_alpha, 0)

        h, w = blur.shape[:2]

        # ---- Title ----
        blur = draw_text_custom(
            blur,
            "MIMIC THE EMOJI",
            (w // 2, int(h * 0.23)),
            size=int(w / 1600 * 120),
            color=(255, 255, 255),
            center=True
        )

        # ---- Subtitle ----
        blur = draw_text_custom(
            blur,
            "Match your expression with the emoji!",
            (w // 2, int(h * 0.32)),
            size=int(w / 1600 * 45),
            color=(240, 240, 240),
            font_path="assets/fonts/Montserrat-Regular.ttf",
            center=True
        )

        # ---- Button PNG ----
        btn_h = int(h * 0.15)
        btn_w = int(btn_h * (start_btn.shape[1] / start_btn.shape[0]))

        start_btn_resized = cv2.resize(start_btn, (btn_w, btn_h), interpolation=cv2.INTER_AREA)

        bx = (w - btn_w) // 2
        by = int(h * 0.55)

        blur = overlay_png(blur, start_btn_resized, bx, by)

        # ---- Deteksi klik mouse ----
        if mouse_clicked:
            if bx <= mouse_x <= bx + btn_w and by <= mouse_y <= by + btn_h:
                mouse_clicked = False  # reset state
                return True
            mouse_clicked = False  # reset klik jika miss

        cv2.imshow(window_name, blur)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            return False


# ============================
#      COUNTDOWN
# ============================
def show_countdown(cap, duration=3):
    window_name = "Emotion Match Game"
    start_time = time.time()
    play_sfx("assets/audio/mariostart.mp3")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        blur = cv2.GaussianBlur(frame, (35, 35), 0)

        # Dark overlay smooth
        overlay_alpha = 0.5   # ubah jadi 0.35–0.50 sesuai selera
        dark = np.zeros_like(blur)

        blur = cv2.addWeighted(blur, 1 - overlay_alpha, dark, overlay_alpha, 0)

        elapsed = int(time.time() - start_time)
        number = duration - elapsed

        if number <= 0:
            break

        h, w = blur.shape[:2]

        blur = draw_text_custom(
            blur,
            str(number),
            (w // 2, h // 2),
            size=int(w / 1600 * 180),
            center=True,
            color=(255, 255, 255)
        )

        cv2.imshow(window_name, blur)
        cv2.waitKey(1)

    time.sleep(0.2)

