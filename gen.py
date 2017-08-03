import numpy as np
import matplotlib.pyplot as plt
import pyaudio
import scipy.fftpack as fp

def sined(rate, duration, *freqs):
    x = np.linspace(0.0, duration, duration * rate)
    y = np.zeros(len(x))
    for f in freqs:
        y += np.sin(f * 2.0 * np.pi * x)
    return (x, y, rate)

def sinel(rate, length, *freqs):
    x = np.linspace(0.0, 1.0 / freq * length, 1.0 / freq * length * rate)
    y = np.zeros(len(x))
    for f in freqs:
        y += np.sin(f * 2.0 * np.pi * x)
    return (x, y, rate)

def cosined(rate, duration, *freqs):
    x = np.linspace(0.0, duration, duration * rate)
    y = np.zeros(len(x))
    for f in freqs:
        y += np.cos(f * 2.0 * np.pi * x)
    return (x, y, rate)

def cosinel(rate, length, *freqs):
    x = np.linspace(0.0, 1.0 / freq * length, 1.0 / freq * length * rate)
    y = np.zeros(len(x))
    for f in freqs:
        y += np.cos(f * 2.0 * np.pi * x)
    return (x, y, rate)



def dfreq(y, rate):
    xf = fp.fftfreq(y.size, 1.0 / rate)
    yf = fp.fft(y)
    return (xf, yf, rate)

def dtime(xf, yf, rate):
    def highestFreq():
        for index in reversed(xrange(len(yf))):
            if (yf[index] != 0.0 + 0.j) and (xf[index] >= 0.0+0.j):
                return xf[index]
    y = fp.ifft(yf)
    length = len(y)
    freq = highestFreq()
    x = np.linspace(0.0, 1.0 / freq * length, 1.0 / freq * length * rate)
    return (x, y, rate)
    
def blend(y1, y2, r2 = 0.5):
    return (y1 * (1 - r2)) + (y2 * r2)


def draw(x, y, style='-', last=True):
    plt.plot(x.real, y.real, style)
    if last:
        plt.grid(True)
        plt.show()    

def play(data, rate):
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format = pyaudio.paInt16, 
        channels = 1, 
        rate = rate, 
        output=True)
    stream.write(data.real.astype('int16'))
    stream.stop_stream()
    stream.close()
    pa.terminate()

def drawFreq(rate, duration, *freqs):
    x, y, r = sined(rate, duration, *freqs)
    xf, yf, rate = dfreq(y, r)
    xf = xf[: len(xf)//2]
    yf = yf[: len(yf)//2]
    yf = yf / len(yf)
    draw(xf, np.abs(yf), 'bo-')    
    

def drawTime(rate, duration, *freqs):
    x, y, r = sined(rate, duration, *freqs)
    draw(x, y, 'bo-')

def playTime(rate, duration, *freqs):
    x, y, r = sined(rate, duration, *freqs)
    y = y * (2** 15)
    play(y, rate)

def playFreq(rate, duration, *freqs):
    x, y, r = sined(rate, duration, *freqs)
    xf, yf, rate = dfreq(y, r)
    y = fp.ifft(yf)
    y = y * (2**15)
    play(y.real, rate)
    