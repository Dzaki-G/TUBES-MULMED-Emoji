import cv2
import numpy as np
import time
from PIL import Image, ImageDraw, ImageFont
from audio_utils import play_sfx

# ===========================================================
#   Mouse Global State (variabel global untuk klik mouse)
# ===========================================================
mouse_clicked = False
mouse_x, mouse_y = 0, 0


def mouse_callback(event, x, y, flags, param):
    """
    Callback function untuk menangkap event klik mouse.

    Parameters:
        event (int): Jenis event dari OpenCV (misal EVENT_LBUTTONDOWN).
        x (int): Posisi X kursor ketika event terjadi.
        y (int): Posisi Y kursor ketika event terjadi.
        flags (int): Flag tambahan OpenCV.
        param: Parameter tambahan (tidak digunakan).

    Returns:
        None
    """
    global mouse_clicked, mouse_x, mouse_y

    # Jika user klik tombol kiri mouse → tandai posisi klik
    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_clicked = True
        mouse_x, mouse_y = x, y


# ===========================================================
#   RENDER TEXT DENGAN FONT CUSTOM (TrueType)
# ===========================================================
def draw_text_custom(frame, text, pos, size=80, color=(255, 255, 255),
                     font_path="assets/fonts/Montserrat-Bold.ttf",
                     center=False):
    """
    Menggambar teks menggunakan font custom (TTF) ke dalam frame OpenCV.

    Parameters:
        frame (numpy.ndarray): Frame gambar OpenCV.
        text (str): Teks yang ingin ditampilkan.
        pos (tuple): Posisi (x, y) text ditampilkan.
        size (int): Ukuran font.
        color (tuple): Warna teks dalam format BGR.
        font_path (str): Path ke file font .ttf.
        center (bool): Jika True, posisi akan di-center-kan.

    Returns:
        numpy.ndarray: Frame yang sudah berisi teks.
    """
    # Convert frame ke PIL image agar bisa memakai custom font
    img_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(font_path, size)

    # Hitung ukuran bounding untuk center alignment
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    # Jika center=True → geser posisi agar teks berada tepat di tengah
    if center:
        pos = (pos[0] - w // 2, pos[1] - h // 2)

    draw.text(pos, text, font=font, fill=color)

    return np.array(img_pil)


# ===========================================================
#   MENGGABUNGKAN PNG TRANSPARAN KE DALAM FRAME
# ===========================================================
def overlay_png(base, img_png, x, y):
    """
    Menempelkan gambar PNG transparan ke frame OpenCV.

    Parameters:
        base (numpy.ndarray): Frame dasar.
        img_png (numpy.ndarray): Gambar PNG (harus RGBA jika ada alpha).
        x (int): Posisi X tempat PNG ditempel.
        y (int): Posisi Y tempat PNG ditempel.

    Returns:
        numpy.ndarray: Frame hasil gabungan.
    """
    h, w = img_png.shape[:2]

    # Cegah keluar batas layar
    if y + h > base.shape[0] or x + w > base.shape[1]:
        return base

    # Jika PNG memiliki channel alpha
    if img_png.shape[2] == 4:
        b, g, r, a = cv2.split(img_png)
        overlay_color = cv2.merge((b, g, r))  # ignore alpha
        mask = a / 255.0  # normalisasi alpha (0–1)

        # Blending pixel-per-pixel
        for c in range(3):
            base[y:y+h, x:x+w, c] = (
                base[y:y+h, x:x+w, c] * (1 - mask) +
                overlay_color[:, :, c] * mask
            )

    return base


# ===========================================================
#   TAMPILKAN MAIN MENU
# ===========================================================
def show_main_menu(cap):
    """
    Menampilkan tampilan UI menu utama dan menunggu input klik user.

    Parameters:
        cap (cv2.VideoCapture): Kamera aktif untuk menampilkan background.

    Returns:
        bool:
            True  → User menekan tombol "Start"
            False → User menekan 'q' / keluar menu
    """
    global mouse_clicked, mouse_x, mouse_y

    window_name = "Emotion Match Game"

    # Aktifkan callback mouse untuk jendela OpenCV
    cv2.setMouseCallback(window_name, mouse_callback)

    # Load tombol start (PNG) satu kali
    start_btn = cv2.imread("assets/ui/startButton.png", cv2.IMREAD_UNCHANGED)

    if start_btn is None:
        print("ERROR: File startButton.png tidak ditemukan!")
        return False

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)  # mirror kamera
        blur = cv2.GaussianBlur(frame, (35, 35), 0)

        # Gelapkan background untuk fokus UI
        overlay_alpha = 0.5
        dark = np.zeros_like(blur)
        blur = cv2.addWeighted(blur, 1 - overlay_alpha, dark, overlay_alpha, 0)

        h, w = blur.shape[:2]

        # ---- Title ----
        blur = draw_text_custom(
            blur,
            "MIMIC THE EMOJI",
            (w // 2, int(h * 0.23)),
            size=int(w / 1600 * 120),
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

        # ---- Button PNG Size ----
        btn_h = int(h * 0.15)
        btn_w = int(btn_h * (start_btn.shape[1] / start_btn.shape[0]))

        # Resize tombol
        start_btn_resized = cv2.resize(start_btn, (btn_w, btn_h), interpolation=cv2.INTER_AREA)

        # Posisi tombol
        bx = (w - btn_w) // 2
        by = int(h * 0.55)

        blur = overlay_png(blur, start_btn_resized, bx, by)

        # ---- Deteksi klik user ----
        if mouse_clicked:
            # Jika klik berada dalam bounding box tombol
            if bx <= mouse_x <= bx + btn_w and by <= mouse_y <= by + btn_h:
                mouse_clicked = False
                return True
            mouse_clicked = False  # reset jika miss

        cv2.imshow(window_name, blur)

        # Tekan 'q' untuk keluar
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            return False


# ===========================================================
#   COUNTDOWN SEBELUM GAME DIMULAI
# ===========================================================
def show_countdown(cap, duration=3):
    """
    Menampilkan countdown animasi sebelum game dimulai.

    Parameters:
        cap (cv2.VideoCapture): Kamera aktif.
        duration (int): Lama hitungan mundur dalam detik.

    Returns:
        None
    """
    window_name = "Emotion Match Game"
    start_time = time.time()

    # Mainkan suara start
    play_sfx("assets/audio/mariostart.mp3")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        blur = cv2.GaussianBlur(frame, (35, 35), 0)

        # Gelapkan background
        overlay_alpha = 0.5
        dark = np.zeros_like(blur)
        blur = cv2.addWeighted(blur, 1 - overlay_alpha, dark, overlay_alpha, 0)

        # Hitung sisa waktu countdown
        elapsed = int(time.time() - start_time)
        number = duration - elapsed

        if number <= 0:
            break  # selesai countdown

        h, w = blur.shape[:2]

        # Tampilkan angka countdown
        blur = draw_text_custom(
            blur,
            str(number),
            (w // 2, h // 2),
            size=int(w / 1600 * 180),
            center=True
        )

        cv2.imshow(window_name, blur)
        cv2.waitKey(1)

    time.sleep(0.2)  # jeda sebentar sebelum game mulai
