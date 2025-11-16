# gui_helpers.py
import time
import numpy as np
import cv2
from emotion_utils import emoji_map

def draw_text_lines(img, lines, start=(10,30), line_height=40, scale=0.9, color=(255,255,255)):
    x, y = start
    for i, line in enumerate(lines):
        cv2.putText(img, line, (x, y + i*line_height), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2)

def calculate_emoji_positions(face_box, num=3, spacing=120, above_offset=140):
    """Return list of (x,y) top-left positions for num emojis relative to face_box."""
    if face_box is None:
        # top-center fallback
        positions = [(100 + i*spacing, 50) for i in range(num)]
        return positions

    x, y, w, h = face_box
    positions = []
    for i in range(num):
        x_offset = int(x + (i - (num-1)/2) * spacing)
        y_offset = int(y - above_offset)
        positions.append((x_offset, y_offset))
    return positions

def draw_floating_emojis(frame, emoji_keys, emoji_images, face_box=None, size=100, matched_emojis=None):
    """Place emoji images on frame. emoji_keys are glyphs from emoji_map."""
    if matched_emojis is None:
        matched_emojis = set()

    positions = calculate_emoji_positions(face_box, num=len(emoji_keys))
    float_offset = int(12 * np.sin(time.time() * 2.0))

    for i, key in enumerate(emoji_keys):
        emotion = emoji_map[key]
        img = emoji_images.get(emotion)
        if img is None:
            continue

        resized = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
        x, y = positions[i]
        y += float_offset
        x = max(0, x); y = max(0, y)

        # === DRAW THE EMOJI ===
        if resized.shape[2] == 4:
            alpha = resized[:, :, 3]
            overlay = resized[:, :, :3]
            from emoji_overlay import overlay_image_alpha
            overlay_image_alpha(frame, overlay, (x, y), alpha)
        else:
            h, w = resized.shape[:2]
            if y + h <= frame.shape[0] and x + w <= frame.shape[1]:
                frame[y:y+h, x:x+w] = resized

        # === GREEN HIGHLIGHT IF MATCHED ===
        if key in matched_emojis:
            cv2.rectangle(frame,
                          (x, y),
                          (x + size, y + size),
                          (0, 255, 0), 3)

