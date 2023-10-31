
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
threshold_coef = 1

# init volume grabber
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)


def calculate():
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
    output_data = (np.repeat(avg,1)+threshold_coef).tolist()
    return (output_data)

def ampl_coef():
    if 0 < volume.GetMasterVolumeLevelScalar() < 1:
        val = np.log10(volume.GetMasterVolumeLevelScalar()) * (-4)
    elif volume.GetMasterVolumeLevelScalar() == 1:
        val = 0.0
    else:
        val = 1.0
    if bool(volume.GetMute()):
        val = 1.0
    return val

new_list = calculate()

with open ('threshold.json','w') as f:
    json.dump(new_list, f)
