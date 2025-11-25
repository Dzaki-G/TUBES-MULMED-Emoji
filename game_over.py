# game_over.py
import cv2
import time
import numpy as np
from audio_utils import play_sfx
from PIL import Image, ImageDraw, ImageFont

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
#   TEXT USING CUSTOM FONT
# ============================
def draw_text_custom(frame, text, pos, size=80, color=(255, 255, 255),
                     font_path="assets/fonts/Montserrat-Bold.ttf",
                     center=False):

    img_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(font_path, size)

    # pillow getbbox
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    if center:
        pos = (pos[0] - w // 2, pos[1] - h // 2)

    draw.text(pos, text, font=font, fill=color)
    return np.array(img_pil)


# ============================
#   OVERLAY PNG TRANSPARAN
# ============================
def overlay_png(base, img_png, x, y):
    h, w = img_png.shape[:2]

    # Pastikan tidak keluar batas layar
    if y + h > base.shape[0] or x + w > base.shape[1]:
        return base

    if img_png.shape[2] == 4:
        b, g, r, a = cv2.split(img_png)
        overlay_color = cv2.merge((b, g, r))
        mask = a / 255.0

        # Perbaikan BUG: x:x+w (bukan x:y+h)
        for c in range(3):
            base[y:y+h, x:x+w, c] = (
                base[y:y+h, x:x+w, c] * (1 - mask) +
                overlay_color[:, :, c] * mask
            )

    else:
        base[y:y+h, x:x+w] = img_png

    return base



# ============================
#      GAME OVER SCREEN
# ============================
def show_game_over(cap, score, highscore):
    global mouse_clicked, mouse_x, mouse_y

    window_name = "Emotion Match Game"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1600, 900)

    # aktifkan mouse callback
    cv2.setMouseCallback(window_name, mouse_callback)

    # Load tombol PNG
    menu_btn = cv2.imread("assets/ui/mainmenuButton.png", cv2.IMREAD_UNCHANGED)

    if menu_btn is None:
        print("ERROR: File assets/ui/mainmenuButton.png tidak ditemukan!")
        return "quit"

    play_sfx("assets/audio/confeti.mp3")
    play_sfx("assets/audio/yay.mp3")

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

        # ----- GAME OVER Title -----
        blur = draw_text_custom(
            blur,
            "GAME OVER",
            (w // 2, int(h * 0.22)),
            size=int(w / 1600 * 140),
            color=(0, 0, 255),
            center=True
        )

        # ----- Score -----
        blur = draw_text_custom(
            blur,
            f"Your Score: {score}",
            (w // 2, int(h * 0.42)),
            size=int(w / 1600 * 80),
            color=(255, 255, 255),
            font_path="assets/fonts/Montserrat-Regular.ttf",
            center=True
        )

        blur = draw_text_custom(
            blur,
            f"High Score: {highscore}",
            (w // 2, int(h * 0.52)),
            size=int(w / 1600 * 80),
            color=(255, 255, 255),
            font_path="assets/fonts/Montserrat-Regular.ttf",
            center=True
        )

        # ----- MENU BUTTON (PNG) -----
        btn_h = int(h * 0.15)
        btn_w = int(btn_h * (menu_btn.shape[1] / menu_btn.shape[0]))

        menu_btn_resized = cv2.resize(menu_btn, (btn_w, btn_h), interpolation=cv2.INTER_AREA)

        bx = (w - btn_w) // 2
        by = int(h * 0.67)

        blur = overlay_png(blur, menu_btn_resized, bx, by)

        # ----- MOUSE CLICK DETECTION -----
        if mouse_clicked:
            if bx <= mouse_x <= bx + btn_w and by <= mouse_y <= by + btn_h:
                mouse_clicked = False
                return "menu"
            mouse_clicked = False

        cv2.imshow(window_name, blur)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            return "quit"
