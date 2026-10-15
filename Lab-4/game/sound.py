import math
from array import array
import pygame

VOLUME = 0.3

def init_mixer():
    # Returns True if audio is usable; the game runs silently otherwise.
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(22050, -16, 1)
        return pygame.mixer.get_init()[1] == -16
    except pygame.error:
        return False

def make_tone(freqs, duration=0.15, freq_end=None):
    # Synthesize a sine tone (one frequency per segment, or a sweep from
    # freqs[0] to freq_end) as a pygame Sound built from 16-bit samples.
    rate, _, channels = pygame.mixer.get_init()
    total = int(rate * duration)
    samples = array("h")
    phase = 0.0
    for i in range(total):
        t = i / total
        if freq_end is not None:
            freq = freqs[0] + (freq_end - freqs[0]) * t
        else:
            freq = freqs[min(int(t * len(freqs)), len(freqs) - 1)]
        phase += 2 * math.pi * freq / rate
        value = int(32767 * VOLUME * (1 - t) * math.sin(phase))  # fade out
        samples.extend([value] * channels)
    return pygame.mixer.Sound(buffer=samples.tobytes())

class Sounds:
    def __init__(self):
        self.jump = self.goal = self.death = None
        try:
            if init_mixer():
                self.jump = make_tone([300], 0.15, freq_end=600)
                self.goal = make_tone([523, 659, 784], 0.3)
                self.death = make_tone([400], 0.5, freq_end=100)
        except (pygame.error, NotImplementedError):
            self.jump = self.goal = self.death = None

    def play(self, sound):
        if sound is not None:
            sound.play()
