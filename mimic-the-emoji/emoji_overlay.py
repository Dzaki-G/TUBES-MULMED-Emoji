import os
import cv2

# ===========================================================
#   LOAD EMOJI PNG/WEBP KE DALAM DICTIONARY
# ===========================================================
def load_emoji_images(folder_path="assets"):
    """
    Memuat semua file gambar emoji dari folder ke dalam dictionary.

    File yang di-load hanya yang berekstensi .png atau .webp.
    Nama file dijadikan key dalam dictionary (tanpa ekstensi),
    misalnya: "happy.png" -> key "happy".

    Parameters:
        folder_path (str):
            Path folder tempat file emoji disimpan.

    Returns:
        dict[str, numpy.ndarray]:
            Dictionary berisi pasangan:
                { "emotion_name": image_array (RGBA atau BGR) }
    """
    images = {}
    
    # Loop semua file di folder target
    for fname in os.listdir(folder_path):

        # Lewati file yang bukan PNG/WEBP
        if not fname.lower().endswith((".png", ".webp")):
            continue

        # Ambil nama file tanpa ekstensi
        name = os.path.splitext(fname)[0]

        # Path lengkap file emoji
        path = os.path.join(folder_path, fname)

        # Load gambar (IMREAD_UNCHANGED untuk menjaga alpha channel)
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            continue

        images[name] = img

    return images


# ===========================================================
#   OVERLAY GAMBAR DENGAN ALPHA BLENDING MANUAL
# ===========================================================
def overlay_image_alpha(img, img_overlay, pos, alpha_mask):
    """
    Menempelkan gambar overlay (dengan alpha mask) ke frame utama.

    Proses ini menggunakan alpha blending manual:
        output = (1 - alpha) * background + alpha * overlay

    Parameters:
        img (numpy.ndarray):
            Frame utama (background) tempat gambar ditempel.
        img_overlay (numpy.ndarray):
            Gambar overlay (H x W x 3), tidak termasuk alpha.
        pos (tuple[int, int]):
            Posisi (x, y) tempat overlay ditempel pada frame utama.
        alpha_mask (numpy.ndarray):
            Mask alpha (H x W), nilai 0–255.

    Returns:
        None
        (Modifies img directly)
    """

    x, y = pos
    h, w = img_overlay.shape[:2]

    # Jika titik awal sudah di luar frame → tidak perlu overlay
    if x >= img.shape[1] or y >= img.shape[0]:
        return

    # Jika overlay melebihi batas kanan frame → potong lebar
    if x + w > img.shape[1]:
        w = img.shape[1] - x
        img_overlay = img_overlay[:, :w]
        alpha_mask = alpha_mask[:, :w]

    # Jika overlay melebihi batas bawah frame → potong tinggi
    if y + h > img.shape[0]:
        h = img.shape[0] - y
        img_overlay = img_overlay[:h]
        alpha_mask = alpha_mask[:h]

    # Region tempat overlay ditempel
    roi = img[y:y+h, x:x+w].astype(float)

    # Pisahkan pixel overlay
    overlay = img_overlay[..., :3].astype(float)

    # Normalisasi alpha mask ke 0–1 dan expand dims
    alpha = (alpha_mask / 255.0)[..., None]

    # Formula alpha blending:
    comp = (1.0 - alpha) * roi + alpha * overlay

    # Replace region dengan hasil blending
    img[y:y+h, x:x+w] = comp.astype(img.dtype)