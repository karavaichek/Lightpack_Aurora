import matplotlib.pyplot as plt
import matplotlib.animation

import pyaudio
import numpy as np
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from dht import idht
import json

# Counts the frames
# why the list? https://stackoverflow.com/questions/25040323/unable-to-reference-one-particular-variable-declared-outside-a-function
count = [0]

# ------------ Audio Setup ---------------
# constants
CHUNK = 1024 * 2  # samples per frame
FORMAT = pyaudio.paInt16  # audio format (bytes per sample?)
CHANNELS = 1  # single channel for microphone
RATE = 44100  # samples per second
# Signal range is -32k to 32k
# limiting amplitude to +/- 4k
AMPLITUDE_LIMIT = 4096

# pyaudio class instance
p = pyaudio.PyAudio()

# stream object to get data from microphone
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

fig = plt.figure()
line1 = plt.plot([],[])[0]
r = range(0,55)
l = len(r)
# init volume grabber
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

def get_const_values():
    with open('threshold.json') as thr:
        threshold = np.array(json.load(thr))
    with open('logarithmic_coefficients.json') as cf:
        log_cf = json.load(cf)
    return (threshold,log_cf)

def calculate(i):
    threshold, log_cf = get_const_values()
    ampl = ampl_coef()
    # binary data
    data = stream.read(CHUNK)
    # Open in numpy as a buffer
    data_np = np.frombuffer(data, dtype='h')
    # compute FFT and update line
    yf = np.abs(idht(data_np))
    # The fft will return complex numbers, so np.abs will return their magnitude
    sound_data = np.interp(yf*ampl, (yf.min(), yf.max()), (0, 255))
    avg = np.mean(np.take(sound_data,list(range(-1,439))).reshape(-1, 8), axis=1)
    raw_data = np.repeat(avg,1)
    after_threshold = raw_data-threshold
    after_threshold = np.clip(after_threshold, 0, 2048).tolist()
    output_data = []
    for i in range(0,len(after_threshold)):
        output_data.append(after_threshold[i]*log_cf[i])
    line1.set_data(r, output_data)
    return (line1,)

def ampl_coef():
    if 0 < volume.GetMasterVolumeLevelScalar() < 1:
        val = np.log10(volume.GetMasterVolumeLevelScalar()) * (-10)+1
    elif volume.GetMasterVolumeLevelScalar() == 1:
        val = 0.1
    else:
        val = 1.0
    if bool(volume.GetMute()):
        val = 1.0
    return val

plt.xlim(0, 55)
plt.ylim(0, 255)
plt.xlabel('Frequency')
plt.ylabel('dB')
plt.title('Spectrometer')
plt.grid()

line_ani = matplotlib.animation.FuncAnimation(
    fig, calculate, interval=0, blit=True
)
plt.show()
