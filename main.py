import os
import re
import string
import curses
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fftpack import fft, ifft
import gen
def ls(rootdir, pattern):
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            filepath = os.path.join(subdir, file)
            if re.match(pattern, filepath):
                yield filepath


def readSample(filepath):
    n, _ = os.path.splitext(os.path.basename(filepath))
    sampling_freq, audio = wavfile.read(filepath)
    try:
        return int(n), sampling_freq, audio
    except ValueError:
        return n, sampling_freq, audio

class Screen(object):
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)

    def close(self):
        self.stdscr.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
    
    def key(self):
        return self.stdscr.getch()

    def output(self, x, y, msg):
        self.stdscr.addstr(x,y,msg)
        

class AudioOut(object):
    def __init__(self, xformat=pyaudio.paInt16, xchannels = 1, xrate = 48000):
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.xformat = xformat
        self.xchannels = xchannels
        self.xrate = xrate

    def open(self, xsource):
        def on_data(in_data, frame_count, time_info, status):
            return xsource.get(frame_count)

        self.stream = self.pa.open(
            format = self.xformat, 
            channels = self.xchannels, 
            rate = self.xrate, 
            output=True, 
            stream_callback = on_data)
                
        self.stream.start_stream()

    def active(self):
        if self.stream is not None:
            return self.stream.is_active()
        return False

    def close(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.pa.terminate()

class FreqSamples(object):
    def __init__(self):
        self.samples = []
        self.current = None
        self.stopped = False

    def add(self, rpm, rate, data, T=5, S=3):
        if type(rpm).__name__ == 'int':
            S = S * rate
            T = T * rate
            s = data[S:(S + T)]
            self.samples.append((rpm, rate, s))

    def prepare(self):
        self.samples = sorted(self.samples, key=(lambda item: item[0]))
        self.current = self.samples[0][2]
        self.begin = 0
        self.stopped = False

    def stop(self):
        self.stopped = True
        
    def set(self, input):
        if input <= self.samples[0][0]:
            self.begin = 0
            self.current = self.samples[0][2]
            #print "i is %d; low is %d; input is %d; high is %d"%(0,self.samples[0][0],input,self.samples[0][0])
        elif input >= self.samples[len(self.samples)-1][0]:
            self.begin = 0
            self.current = self.samples[len(self.samples)-1][2]
            #print "i is %d; low is %d; input is %d; high is %d"%(len(self.samples)-1,self.samples[len(self.samples)-1][0],input,self.samples[len(self.samples)-1][0])
        else:
            for i in xrange(0, len(self.samples) - 1):
                low = self.samples[i]
                high = self.samples[i + 1]
                #print "i is %d; low is %d; input is %d; high is %d"%(i,low[0],input,high[0])
                if input == low[0]:
                    self.begin = 0
                    self.current = low[2]
                    break
                elif input == high[0]:
                    self.begin = 0
                    self.current = high[2]
                    break
                elif (input > low[0]) and (input < high[0]):
                    low_ratio = float(high[0] - input) / float(high[0] - low[0])
                    #print "hit", low_ratio, 1-low_ratio
                    self.begin = 0
                    self.current = (low[2] * low_ratio + high[2] * (1-low_ratio)).astype('int16')
                    break

    def get(self, frame_count):
        if self.current is not None:
            if (self.begin + frame_count) > len(self.current):
                self.begin = 0
            data = self.current[self.begin:self.begin + frame_count]
            self.begin = self.begin + frame_count
            if self.stopped:
                return (data, pyaudio.paComplete)
            else:
                return (data, pyaudio.paContinue)
        raise Exception("current frame is None %d"%frame_count)

    
def test(ao, fs):
    ao.open(fs)
    def getRPM():
        s = input("Please input RPM:\n")
        try:
            return int(s)
        except ValueError:
            return s
    while ao.active():
        r = getRPM()
        if type(r).__name__ == 'int':
            fs.set(r)
        else:
            fs.stop()

def loop(ao, fs):
    ao.open(fs)
    sc = Screen()
    try:
        rpm = 1100
        while ao.active():
            sc.output(0,0,"RPM:%d"%rpm)
            c = sc.key()
            if c == curses.KEY_UP:
                rpm += 50
                fs.set(rpm)
            elif c == curses.KEY_DOWN:
                rpm -= 50
                fs.set(rpm)
            else:
                fs.stop()
    finally:
        sc.close()


if __name__ == '__main__':
    fs = FreqSamples()
    ao = AudioOut()
    try:
        for f in ls('./sounds', '.+\\.wav$'):
            x, rate, au = readSample(f)
            fs.add(x, rate, au)
        fs.prepare()
        #test(ao, fs)
        loop(ao,fs)
    finally:       
        ao.close()