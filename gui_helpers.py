# gui_helpers.py
import time
import numpy as np
import cv2
from emotion_utils import emoji_map

def draw_text_lines(img, lines, start=(10,30), line_height=40, scale=0.9, color=(255,255,255)):
    x, y = start
    for i, line in enumerate(lines):
        cv2.putText(img, line, (x, y + i*line_height), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2)

def draw_simple_hud(frame, round_num, score, remaining):
    text = f"Round: {round_num}   Time: {remaining}s   Score: {score}"

    h, w = frame.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    thickness = 2

    # ---- Ukur teks ----
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

    # posisi teks
    x = (w - text_width) // 2
    y = 50  # sedikit di bawah

    # ---- Auto-scale jika terlalu panjang ----
    if text_width > w - 40:
        font_scale = (w - 40) / text_width * 0.8
        thickness = 1
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        x = (w - text_width) // 2

    # ---- Background Box ----
    padding_x = 20
    padding_y = 12

    box_x1 = x - padding_x
    box_y1 = y - text_height - padding_y
    box_x2 = x + text_width + padding_x
    box_y2 = y + padding_y // 2

    # clamp biar tidak keluar batas
    box_x1 = max(0, box_x1)
    box_y1 = max(0, box_y1)
    box_x2 = min(w, box_x2)
    box_y2 = min(h, box_y2)

    # warna background (hitam semi-transparan)
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (box_x1, box_y1),
        (box_x2, box_y2),
        (0, 0, 0),  # hitam
        -1
    )

    # apply transparency
    alpha = 0.45  # 0.30 lebih cerah, 0.50 lebih gelap
    frame[:] = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    # ---- Draw Text ----
    cv2.putText(
        frame,
        text,
        (x, y),
        font,
        font_scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA
    )


def calculate_emoji_positions(face_box, num=3, spacing=120, above_offset=140):
    """Return list of (x,y) top-left positions for num emojis relative to face_box."""
    if face_box is None:
        # top-center fallback
        positions = [(100 + i*spacing, 50) for i in range(num)]
        return positions

    x, y, w, h = face_box
    positions = []
    for i in range(num):
        x_offset = int(x + (i - (num-1)/2) * spacing + 45)
        y_offset = int(y - above_offset)
        positions.append((x_offset, y_offset))
    return positions


def draw_floating_emojis(frame, emoji_keys, emoji_images, face_box=None, size=100, matched_emojis=None, current_index=0):

    """Place emoji images on frame. emoji_keys are glyphs from emoji_map."""
    if matched_emojis is None:
        matched_emojis = set()

    positions = calculate_emoji_positions(face_box, num=len(emoji_keys))

    for i, key in enumerate(emoji_keys):
        emotion = emoji_map[key]
        img = emoji_images.get(emotion)
        if img is None:
            continue

        resized = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
        x, y = positions[i]
        x = max(0, x); y = max(0, y)

        # draw the emoji
        if resized.shape[2] == 4:
            alpha = resized[:, :, 3]
            overlay = resized[:, :, :3]
            from emoji_overlay import overlay_image_alpha
            overlay_image_alpha(frame, overlay, (x, y), alpha)
        else:
            h, w = resized.shape[:2]
            if y + h <= frame.shape[0] and x + w <= frame.shape[1]:
                frame[y:y+h, x:x+w] = resized
        
        # highlight current target with YELLOW
        if i == current_index and key not in matched_emojis:
            cv2.rectangle(frame,
                        (x, y),
                        (x + size, y + size),
                        (0, 255, 255),    
                        3)


        # green highlight if matched
        if key in matched_emojis:
            cv2.rectangle(frame,
                          (x, y),
                          (x + size, y + size),
                          (0, 255, 0), 3)

def draw_current_emotion(frame, detected_emotion, emoji_images, size=60):
    """Draw bottom-left box showing current emotion (text above emoji)."""
    if detected_emotion is None:
        return

    img = emoji_images.get(detected_emotion)
    if img is None:
        return

    h, w = frame.shape[:2]

    # Resize emoji
    resized = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)

    # Position bottom-left
    x = 20
    y = h - size - 90   # same height, slightly lifted for text

    # Box size
    box_w = 100
    box_h = size + 55   # space for text + emoji

    # Semi-transparent box
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (x - 10, y - 10),
        (x - 10 + box_w, y - 10 + box_h),
        (0, 0, 0),
        -1
    )
    cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)

    # ---- Text  ----
    cv2.putText(
        frame,
        "Current Emotion:",
        (x, y + 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.3,                 
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )

    # ---- Emoji below text ----
    emoji_x = x + 10
    emoji_y = y + 25

    if resized.shape[2] == 4:
        alpha = resized[:, :, 3]
        overlay_emoji = resized[:, :, :3]
        from emoji_overlay import overlay_image_alpha
        overlay_image_alpha(frame, overlay_emoji, (emoji_x, emoji_y), alpha)
    else:
        frame[emoji_y:emoji_y+size, emoji_x:emoji_x+size] = resized
