import cv2
import time
import numpy as np
from audio_utils import play_sfx
from PIL import Image, ImageDraw, ImageFont

# ===========================================================
#   Mouse Global State — menyimpan status klik mouse
# ===========================================================
mouse_clicked = False
mouse_x, mouse_y = 0, 0


def mouse_callback(event, x, y, flags, param):
    """
    Callback untuk menangani input klik mouse.

    Parameters:
        event (int): Event dari OpenCV (misal EVENT_LBUTTONDOWN).
        x (int): Posisi X mouse saat event terjadi.
        y (int): Posisi Y mouse saat event terjadi.
        flags (int): Informasi tambahan event.
        param: Parameter tambahan (tidak digunakan).

    Returns:
        None
    """
    global mouse_clicked, mouse_x, mouse_y

    # Deteksi klik kiri mouse
    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_clicked = True
        mouse_x, mouse_y = x, y


# ===========================================================
#   TEXT USING CUSTOM FONT (TTF)
# ===========================================================
def draw_text_custom(frame, text, pos, size=80, color=(255, 255, 255),
                     font_path="assets/fonts/Montserrat-Bold.ttf",
                     center=False):
    """
    Menggambar teks pada frame menggunakan font .ttf custom.

    Parameters:
        frame (numpy.ndarray): Frame OpenCV.
        text (str): Teks yang ingin ditampilkan.
        pos (tuple): Posisi (x, y) text.
        size (int): Ukuran font.
        color (tuple): Warna teks BGR.
        font_path (str): Path font TTF.
        center (bool): Jika True, posisi akan dirata-tengah.

    Returns:
        numpy.ndarray: Frame dengan teks terpasang.
    """
    # Convert frame ke PIL karena PIL mendukung font TTF custom
    img_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(font_path, size)

    # Hitung ukuran bounding box untuk center alignment
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    # Jika center=True → geser posisi ke tengah
    if center:
        pos = (pos[0] - w // 2, pos[1] - h // 2)

    draw.text(pos, text, font=font, fill=color)

    return np.array(img_pil)


# ===========================================================
#   OVERLAY PNG TRANSPARAN DI ATAS FRAME OPENCV
# ===========================================================
def overlay_png(base, img_png, x, y):
    """
    Menempelkan file PNG dengan alpha channel ke frame OpenCV.

    Parameters:
        base (numpy.ndarray): Frame video sebagai background.
        img_png (numpy.ndarray): Gambar PNG (RGBA).
        x (int): Posisi X penempatan PNG.
        y (int): Posisi Y penempatan PNG.

    Returns:
        numpy.ndarray: Frame yang telah ditempeli PNG.
    """
    h, w = img_png.shape[:2]

    # Cegah keluar batas frame
    if y + h > base.shape[0] or x + w > base.shape[1]:
        return base

    # Jika PNG memiliki channel alpha → lakukan blending
    if img_png.shape[2] == 4:
        b, g, r, a = cv2.split(img_png)
        overlay_color = cv2.merge((b, g, r))
        mask = a / 255.0  # normalisasi alpha 0–1

        # Blending pixel-per-channel
        for c in range(3):
            base[y:y+h, x:x+w, c] = (
                base[y:y+h, x:x+w, c] * (1 - mask) +
                overlay_color[:, :, c] * mask
            )

    else:
        # Jika PNG tidak punya alpha, langsung tempel
        base[y:y+h, x:x+w] = img_png

    return base


# ===========================================================
#      GAME OVER SCREEN
# ===========================================================
def show_game_over(cap, score, highscore):
    """
    Menampilkan layar Game Over lengkap dengan score, high score,
    dan tombol kembali ke main menu.

    Parameters:
        cap (cv2.VideoCapture): Kamera aktif untuk background.
        score (int): Skor pemain.
        highscore (int): Highscore tersimpan.

    Returns:
        str:
            "menu"  → pengguna klik tombol 'Main Menu'
            "quit"  → pengguna menekan 'q' untuk keluar
    """
    global mouse_clicked, mouse_x, mouse_y

    window_name = "Mimic The Emoji"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1600, 900)

    # Aktifkan event listener mouse
    cv2.setMouseCallback(window_name, mouse_callback)

    # Load gambar tombol
    menu_btn = cv2.imread("assets/ui/mainmenuButton.png", cv2.IMREAD_UNCHANGED)

    if menu_btn is None:
        print("ERROR: File mainmenuButton.png tidak ditemukan!")
        return "quit"

    # Mainkan efek suara Game Over
    play_sfx("assets/audio/confeti.mp3")
    play_sfx("assets/audio/yay.mp3")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        blur = cv2.GaussianBlur(frame, (35, 35), 0)

        # Gelapkan background untuk fokus UI
        overlay_alpha = 0.5
        dark = np.zeros_like(blur)
        blur = cv2.addWeighted(blur, 1 - overlay_alpha, dark, overlay_alpha, 0)

        h, w = blur.shape[:2]

        # ----- TITLE GAME OVER -----
        blur = draw_text_custom(
            blur,
            "GAME OVER",
            (w // 2, int(h * 0.22)),
            size=int(w / 1600 * 140),
            color=(0, 0, 255),
            center=True
        )

        # ----- SCORE -----
        blur = draw_text_custom(
            blur,
            f"Your Score: {score}",
            (w // 2, int(h * 0.42)),
            size=int(w / 1600 * 80),
            color=(255, 255, 255),
            font_path="assets/fonts/Montserrat-Regular.ttf",
            center=True
        )

        # ----- HIGH SCORE -----
        blur = draw_text_custom(
            blur,
            f"High Score: {highscore}",
            (w // 2, int(h * 0.52)),
            size=int(w / 1600 * 80),
            color=(255, 255, 255),
            font_path="assets/fonts/Montserrat-Regular.ttf",
            center=True
        )

        # ----- BUTTON RESIZING -----
        btn_h = int(h * 0.15)
        btn_w = int(btn_h * (menu_btn.shape[1] / menu_btn.shape[0]))

        menu_btn_resized = cv2.resize(menu_btn, (btn_w, btn_h), interpolation=cv2.INTER_AREA)

        # Posisikan tombol
        bx = (w - btn_w) // 2
        by = int(h * 0.67)

        blur = overlay_png(blur, menu_btn_resized, bx, by)

        # ----- DETEKSI KLIK -----
        if mouse_clicked:
            if bx <= mouse_x <= bx + btn_w and by <= mouse_y <= by + btn_h:
                mouse_clicked = False
                return "menu"  # kembali ke main menu

            mouse_clicked = False  # reset jika klik tidak di tombol

        cv2.imshow(window_name, blur)

        # Tekan Q untuk quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            return "quit"
