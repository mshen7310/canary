#sounds/ferrari/5500.wav
#sounds/ferrari/7000.wav
from scipy.io import wavfile
import gen
import os
def readSample(filepath, T = 2, skip = 5):
    n, _ = os.path.splitext(os.path.basename(filepath))
    rate, audio = wavfile.read(filepath)
    skip = skip * rate
    T = T * rate    
    try:
        return int(n), rate, audio[skip : (skip  + T)]
    except ValueError:
        return n, rate, audio[skip : (skip  + T)]


def load(ratio):
    _, rate, s1 = readSample('sounds/ferrari/1100.wav')
    _, rate, s2 = readSample('sounds/ferrari/1200.wav')
    s = s1 * (1.0 - ratio) + s2 * ratio
    gen.play(s, rate)
