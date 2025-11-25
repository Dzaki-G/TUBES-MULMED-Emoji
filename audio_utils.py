# audio_utils.py
import pygame

def init_audio():
    pygame.mixer.init()

def play_bgm(path, volume=0.5):
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)  # loop forever

def stop_bgm():
    pygame.mixer.music.stop()

def play_sfx(path, volume=1.0):
    sound = pygame.mixer.Sound(path)
    sound.set_volume(volume)
    sound.play()
