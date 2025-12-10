import time
import numpy as np
import cv2
from emotion_utils import emoji_map

# ===========================================================
#   MENAMPILKAN BEBERAPA BARIS TEKS VERTIKAL
# ===========================================================
def draw_text_lines(img, lines, start=(10, 30), line_height=40, scale=0.9, color=(255, 255, 255)):
    """
    Menggambar beberapa baris teks secara vertikal di dalam frame.

    Parameters:
        img (numpy.ndarray): Frame OpenCV sebagai canvas.
        lines (list[str]): Daftar string yang akan ditampilkan per baris.
        start (tuple[int, int]): Posisi awal (x, y) baris pertama.
        line_height (int): Jarak vertikal antar baris teks.
        scale (float): Ukuran font.
        color (tuple): Warna teks (BGR).

    Returns:
        None
        (Modifies img directly)
    """
    x, y = start

    # Gambar tiap baris teks dengan offset line_height
    for i, line in enumerate(lines):
        cv2.putText(img, line, (x, y + i * line_height),
                    cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2)


# ===========================================================
#   HUD SEDERHANA (Ronde, Waktu, Score)
# ===========================================================
def draw_simple_hud(frame, round_num, score, remaining):
    """
    Menampilkan HUD di bagian atas layar berisi:
    - Round
    - Time
    - Score

    Teks diberi background semi-transparan agar mudah dibaca.

    Parameters:
        frame (numpy.ndarray): Frame OpenCV.
        round_num (int): Ronde permainan.
        score (int): Score pemain.
        remaining (int): Sisa waktu (detik).

    Returns:
        None
    """
    text = f"Round: {round_num}   Time: {remaining}s   Score: {score}"

    h, w = frame.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    thickness = 2

    # Hitung ukuran teks untuk centering
    (text_width, text_height), baseline = cv2.getTextSize(
        text, font, font_scale, thickness)

    x = (w - text_width) // 2
    y = 50

    # Auto-scale jika teks terlalu panjang
    if text_width > w - 40:
        font_scale = (w - 40) / text_width * 0.8
        thickness = 1
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, font_scale, thickness)
        x = (w - text_width) // 2

    # Background box semi-transparan
    padding_x = 20
    padding_y = 12

    box_x1 = max(0, x - padding_x)
    box_y1 = max(0, y - text_height - padding_y)
    box_x2 = min(w, x + text_width + padding_x)
    box_y2 = min(h, y + padding_y // 2)

    overlay = frame.copy()
    cv2.rectangle(overlay, (box_x1, box_y1),
                  (box_x2, box_y2), (0, 0, 0), -1)

    # Blend overlay → frame untuk transparansi
    frame[:] = cv2.addWeighted(overlay, 0.45, frame, 0.55, 0)

    # Gambar teks
    cv2.putText(frame, text, (x, y), font,
                font_scale, (255, 255, 255), thickness, cv2.LINE_AA)


# ===========================================================
#   HITUNG POSISI EMOJI DI ATAS KEPALA USER
# ===========================================================
def calculate_emoji_positions(face_box, num=3, spacing=120, above_offset=140):
    """
    Menghitung posisi top-left untuk emoji yang melayang di atas kepala pemain.

    Jika wajah tidak terdeteksi, emoji akan muncul di bagian atas layar.

    Parameters:
        face_box (tuple|None): (x, y, w, h) bounding box wajah.
        num (int): Jumlah emoji yang ingin ditempatkan.
        spacing (int): Jarak horizontal antar emoji.
        above_offset (int): Jarak vertikal di atas wajah.

    Returns:
        list[tuple[int, int]]: Daftar posisi (x, y) untuk tiap emoji.
    """
    if face_box is None:
        # fallback jika tidak ada wajah
        return [(100 + i * spacing, 50) for i in range(num)]

    x, y, w, h = face_box
    positions = []

    # Tempatkan emoji secara rata di atas kepala
    for i in range(num):
        x_offset = int(x + (i - (num - 1) / 2) * spacing + 45)
        y_offset = int(y - above_offset)
        positions.append((x_offset, y_offset))

    return positions


# ===========================================================
#   GAMBAR EMOJI TERBANG DI SEKITAR WAJAH
# ===========================================================
def draw_floating_emojis(frame, emoji_keys, emoji_images,
                         face_box=None, size=100,
                         matched_emojis=None, current_index=0):
    """
    Menggambar emoji target yang melayang di atas kepala pemain.
    Emoji memiliki highlight:
    - Kuning → target emoji yang harus dicocokkan sekarang
    - Hijau  → emoji yang sudah berhasil dicocokkan

    Parameters:
        frame (numpy.ndarray): Frame OpenCV.
        emoji_keys (list[str]): Daftar emoji (glyph).
        emoji_images (dict): Dict mapping nama emosi → gambar emoji.
        face_box (tuple|None): Posisi bounding box wajah.
        size (int): Ukuran emoji (px).
        matched_emojis (set): Emoji yang sudah benar.
        current_index (int): Indeks emoji target saat ini.

    Returns:
        None
    """
    if matched_emojis is None:
        matched_emojis = set()

    positions = calculate_emoji_positions(face_box, num=len(emoji_keys))

    for i, key in enumerate(emoji_keys):

        emotion = emoji_map[key]   # map emoji → nama emotion
        img = emoji_images.get(emotion)

        if img is None:
            continue

        # Resize emoji
        resized = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)

        x, y = positions[i]
        x, y = max(0, x), max(0, y)

        # ---------------------------
        # Gambar emoji (dengan alpha)
        # ---------------------------
        if resized.shape[2] == 4:
            alpha = resized[:, :, 3]
            overlay = resized[:, :, :3]
            from emoji_overlay import overlay_image_alpha
            overlay_image_alpha(frame, overlay, (x, y), alpha)
        else:
            h, w = resized.shape[:2]
            if y + h <= frame.shape[0] and x + w <= frame.shape[1]:
                frame[y:y+h, x:x+w] = resized

        # ---------------------------
        # Highlight kuning → target sekarang
        # ---------------------------
        if i == current_index and key not in matched_emojis:
            cv2.rectangle(frame, (x, y), (x + size, y + size),
                          (0, 255, 255), 3)

        # ---------------------------
        # Highlight hijau → berhasil dicocokkan
        # ---------------------------
        if key in matched_emojis:
            cv2.rectangle(frame, (x, y), (x + size, y + size),
                          (0, 255, 0), 3)


# ===========================================================
#   TAMPILKAN EMOSI SAAT INI (TEXT + EMOJI)
# ===========================================================
def draw_current_emotion(frame, detected_emotion, emoji_images, size=60):
    """
    Menampilkan kotak kecil di kiri bawah layar yang berisi:
    - Label "Current Emotion"
    - Emoji sesuai emosi yang dideteksi DeepFace

    Parameters:
        frame (numpy.ndarray): Frame kamera.
        detected_emotion (str|None): Nama emosi (happy, sad, angry, dll).
        emoji_images (dict): Mapping emosi → gambar PNG.
        size (int): Ukuran emoji.

    Returns:
        None
    """
    if detected_emotion is None:
        return

    img = emoji_images.get(detected_emotion)
    if img is None:
        return

    h, w = frame.shape[:2]

    resized = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)

    # Posisi panel
    x = 20
    y = h - size - 90
    box_w = 100
    box_h = size + 55

    # Background semi transparan
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (x - 10, y - 10),
        (x - 10 + box_w, y - 10 + box_h),
        (0, 0, 0),
        -1
    )
    cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)

    # Text label
    cv2.putText(frame, "Current Emotion:", (x, y + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.3,
                (255, 255, 255), 1, cv2.LINE_AA)

    # Gambar emoji
    emoji_x = x + 10
    emoji_y = y + 25

    if resized.shape[2] == 4:
        alpha = resized[:, :, 3]
        overlay_emoji = resized[:, :, :3]
        from emoji_overlay import overlay_image_alpha
        overlay_image_alpha(frame, overlay_emoji, (emoji_x, emoji_y), alpha)
    else:
        frame[emoji_y:emoji_y+size, emoji_x:emoji_x+size] = resized
