from main_menu import show_main_menu, show_countdown
from game_over import show_game_over
import cv2
import time
from emotion_utils import get_emotion, get_random_emojis, emoji_map
from emoji_overlay import load_emoji_images
from gui_helpers import draw_floating_emojis, draw_text_lines, draw_simple_hud, draw_current_emotion
from audio_utils import init_audio, play_bgm, stop_bgm, play_sfx

def run_game(cap):
    """
    Fungsi utama loop permainan Emotion Match Game.

    Game akan:
    - Mengambil ekspresi wajah user melalui kamera.
    - Membandingkan hasil deteksi emosi dengan urutan target emoji.
    - Memberikan poin jika sesuai.
    - Menampilkan HUD (score, round, timer).
    - Mengakhiri game setelah waktu habis atau user keluar.

    Parameters:
        cap (cv2.VideoCapture): Kamera aktif.

    Returns:
        int: Score akhir pemain.
    """

    # ---------------------------
    # Variabel utama game
    # ---------------------------
    score = 0
    round_num = 1                  # ronde ke berapa
    round_emojis = get_random_emojis(3)   # 3 emoji target tiap ronde
    matched = set()                # emoji yang sudah berhasil dicocokkan
    current_index = 0              # pointer emoji target saat ini
    game_duration = 30             # total waktu game
    start_time = time.time()       # timestamp mulai

    # Mainkan background music
    play_bgm("assets/audio/bgm.mp3")

    # ---------------------------
    # Setup deteksi wajah & emoji
    # ---------------------------
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    emoji_images = load_emoji_images("assets")  # load semua emoji PNG

    # ---------------------------
    # MAIN GAME LOOP
    # ---------------------------
    while True:

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # mirror kamera
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Deteksi wajah (untuk meletakkan floating emojis)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        face_box = tuple(faces[0]) if len(faces) else None

        # Deteksi emosi dari kamera
        detected = get_emotion(frame, enforce_detection=False)

        # ---------------------------
        # Gambar emoji target mengitari wajah
        # ---------------------------
        draw_floating_emojis(
            frame,
            round_emojis,
            emoji_images,
            face_box=face_box,
            size=100,
            matched_emojis=matched,
            current_index=current_index
        )

        # Tampilkan emosi user saat ini (ikon kecil di HUD)
        draw_current_emotion(frame, detected, emoji_images)

        # ---------------------------
        # LOGIKA PENC0C0KAN EMOJI
        # ---------------------------
        if detected and current_index < len(round_emojis):

            key = round_emojis[current_index]       # emoji target saat ini
            target_emotion = emoji_map[key]         # konversi emoji → nama emosi

            # Jika emosi user sama dengan target:
            if detected == target_emotion:
                play_sfx("assets/audio/correct.mp3")

                matched.add(key)
                score += 1
                current_index += 1

                # Jika 3 emoji sudah berhasil → lanjut ronde berikutnya
                if current_index == 3:
                    round_num += 1
                    matched.clear()
                    current_index = 0
                    round_emojis = get_random_emojis(3)

        # ---------------------------
        # HUD: score, round, time
        # ---------------------------
        remaining = max(0, int(game_duration - (time.time() - start_time)))
        draw_simple_hud(frame, round_num, score, remaining)

        # Tampilkan frame
        cv2.imshow("Emotion Match Game", frame)

        # Game berhenti jika:
        # 1) user menekan 'q'
        # 2) waktu habis
        if cv2.waitKey(1) & 0xFF == ord('q') or remaining == 0:
            break

    # Stop background music ketika game selesai
    stop_bgm()

    return score


def main():
    """
    Fungsi utama untuk menjalankan keseluruhan alur program:

    1. Mengaktifkan kamera & window.
    2. Menampilkan main menu.
    3. Menampilkan countdown.
    4. Menjalankan game loop.
    5. Menyimpan highscore.
    6. Menampilkan layar Game Over.
    7. Mengulang jika user ingin kembali ke menu.

    Parameters:
        None

    Returns:
        None
    """

    # Inisialisasi kamera
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Emotion Match Game", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Emotion Match Game", 1600, 900)

    # Inisialisasi audio pygame
    init_audio()

    # ---------------------------
    # LOOP UTAMA PROGRAM
    # ---------------------------
    while True:

        # Tampilkan Main Menu (return False jika user keluar)
        if not show_main_menu(cap):
            break

        # Hitung mundur sebelum game dimulai
        show_countdown(cap)

        # Jalankan game → dapatkan score
        score = run_game(cap)

        # ---------------------------
        # Load & update highscore file
        # ---------------------------
        try:
            highscore = int(open("highscore.txt").read())
        except:
            highscore = 0

        if score > highscore:
            highscore = score
            with open("highscore.txt", "w") as f:
                f.write(str(highscore))

        # ---------------------------
        # Layar Game Over
        # ---------------------------
        action = show_game_over(cap, score, highscore)

        # Jika user memilih quit
        if action == "quit":
            break

        # Jika user memilih menu → ulangi loop

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
