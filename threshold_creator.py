#!/usr/bin/env python
# -*- charset utf8 -*-

import pyaudio
import numpy
from pprint import pprint
import json

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

new_data = []

def create():
    try:
        data = numpy.fft.rfft(numpy.fromstring(
            stream.read(BUFFER), dtype=numpy.float32)
        )
    except IOError:
        pass    
    data = numpy.log10(numpy.sqrt(
        numpy.real(data)**2+numpy.imag(data)**2) / BUFFER) * 10

    for el in data:
        new_data.append(int(el)+10)
    pprint (data)
    pprint (new_data)
    with open('threshold.json', 'w') as f:
        json.dump(new_data, f)

create()
