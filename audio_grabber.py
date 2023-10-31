#!/usr/bin/env python
# -*- charset utf8 -*-


from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pyaudio
import numpy
from pprint import pprint
import json
import matplotlib.pyplot as plt
import matplotlib.animation

RATE = 44100
BUFFER = 882

p = pyaudio.PyAudio()

stream = p.open(
    format = pyaudio.paFloat32,
    channels = 1,
    rate = RATE,
    input = True,
    frames_per_buffer = BUFFER
)


fig = plt.figure()
line1 = plt.plot([],[])[0]

r = range(0,int(RATE/2+1),int(RATE/BUFFER))
l = len(r)

threshold = []
new_data = []

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
ampl = volume.GetMasterVolumeLevel()*(-1)

def init_line():
    line1.set_data(r, [-1000] * l)
    return (line1,)

def update_line(i):
    try:
        data = numpy.fft.rfft(numpy.fromstring(
            stream.read(BUFFER), dtype=numpy.float32)
        )

    except IOError:
        pass
    data = numpy.log10(numpy.sqrt(
        numpy.real(data)**2) / BUFFER)*10

    with open('threshold.json') as f:
        threshold = json.load(f)
    threshold = numpy.array(threshold)
    new_data = numpy.clip(data-threshold, 0, 255)*ampl
    print(len(new_data))
    line1.set_data(r, new_data)
    return (line1,)

plt.xlim(0, RATE/2+1)
plt.ylim(0 , 255)
plt.xlabel('Frequency')
plt.ylabel('dB')
plt.title('Spectrometer')
plt.grid()

line_ani = matplotlib.animation.FuncAnimation(
    fig, update_line, init_func=init_line, interval=0, blit=True
)

plt.show()
