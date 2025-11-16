# emoji_overlay.py
import os
import cv2

def load_emoji_images(folder_path="assets"):
    """Load images named {emotion}.png into dict emotion->img (RGBA if available)."""
    images = {}
    for fname in os.listdir(folder_path):
        if not fname.lower().endswith((".png", ".webp")):
            continue
        name = os.path.splitext(fname)[0]  # e.g., happy.png -> "happy"
        path = os.path.join(folder_path, fname)
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)  # maybe 4 channels
        if img is None:
            continue
        images[name] = img
    return images

def overlay_image_alpha(img, img_overlay, pos, alpha_mask):
    """Overlay img_overlay (H x W x 3) onto img at pos (x,y) using alpha_mask (H x W)."""
    x, y = pos
    h, w = img_overlay.shape[:2]

    # Bounds check and trim if necessary
    if x >= img.shape[1] or y >= img.shape[0]:
        return
    if x + w > img.shape[1]:
        w = img.shape[1] - x
        img_overlay = img_overlay[:, :w]
        alpha_mask = alpha_mask[:, :w]
    if y + h > img.shape[0]:
        h = img.shape[0] - y
        img_overlay = img_overlay[:h]
        alpha_mask = alpha_mask[:h]

    roi = img[y:y+h, x:x+w].astype(float)
    overlay = img_overlay[..., :3].astype(float)
    alpha = (alpha_mask / 255.0)[..., None]

    # composite
    comp = (1.0 - alpha) * roi + alpha * overlay
    img[y:y+h, x:x+w] = comp.astype(img.dtype)
