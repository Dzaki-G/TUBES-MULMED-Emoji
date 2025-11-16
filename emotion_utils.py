# emotion_utils.py
from deepface import DeepFace
import random

# map emoji glyph
emoji_map = {
    "😃": "happy",
    "😢": "sad",
    "😠": "angry",
    "😐": "neutral",
    "😮": 'surprise',
    "🤢": 'disgust',
    "😨": "fear"
}

def get_emotion(frame, enforce_detection=False):
    """Return dominant emotion name or None."""
    try:
        result = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=enforce_detection)
        return result[0]["dominant_emotion"]
    except Exception:
        return None

def get_random_emojis(n=3):
    """Return n random emoji keys from emoji_map."""
    return random.sample(list(emoji_map.keys()), n)
