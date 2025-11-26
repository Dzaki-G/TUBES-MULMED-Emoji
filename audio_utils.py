import pygame

def init_audio():
    """
    Menginisialisasi sistem audio pygame.mixer.

    Fungsi ini wajib dipanggil sebelum menggunakan fungsi audio lain
    seperti play_bgm() atau play_sfx().

    Parameters:
        None

    Returns:
        None
    """
    # Inisialisasi modul audio pygame
    pygame.mixer.init()


def play_bgm(path, volume=0.5):
    """
    Memutar background music (BGM) secara looping.

    Parameters:
        path (str): Path file audio (format umum: .mp3, .wav).
        volume (float): Volume audio antara 0.0–1.0.

    Returns:
        None
    """
    # Load file musik
    pygame.mixer.music.load(path)

    # Atur volume musik
    pygame.mixer.music.set_volume(volume)

    # Play musik secara loop tanpa henti (-1)
    pygame.mixer.music.play(-1)


def stop_bgm():
    """
    Menghentikan background music yang sedang diputar.

    Parameters:
        None

    Returns:
        None
    """
    # Stop playback musik
    pygame.mixer.music.stop()


def play_sfx(path, volume=1.0):
    """
    Memutar sound effect (SFX) sekali tanpa loop.

    Parameters:
        path (str): Path file audio SFX.
        volume (float): Volume efek suara (0.0–1.0).

    Returns:
        None
    """
    # Load sound effect ke objek Sound
    sound = pygame.mixer.Sound(path)

    # Set volume SFX
    sound.set_volume(volume)

    # Play sekali
    sound.play()