#! /usr/bin/env python

# Use pyaudio to open the microphone and run aubio.pitch on the stream of
# incoming samples. If a filename is given as the first argument, it will
# record 5 seconds of audio to this location. Otherwise, the script will
# run until Ctrl+C is pressed.

# Some portions of code modified from:
#    $ ./python/demos/demo_pyaudio.py
#    $ ./python/demos/demo_pyaudio.py /tmp/recording.wav

'''
For MVP
1. Detect and connect to Scarlett USB Device
Method A:
a2. Record into file (to save for user listening)
a3. Run file through aubio
Method B:
b2. Pipe audio directly into aubio (lose ability to re-listen)
...
4. Provide output file to audio timing algorithm

Challenges:
Chord Handling; might need a fft and custom chord detection alg. 
'''

import pyaudio
import sys
import numpy as np
import aubio
import os

# Gloabals Table
# Constants for audio stream
BUFFER_SIZE = 1024  # Standard Buffer Size
SAMPLE_RATE = 44100  # Common sample rate for audio
PITCH_TOLERANCE = 0.8 # Required confidence of pitch value
DEFAULT_BPM = 120 # Number of quarter-notes per minute

# @param name is the name of the device to be searched for
# @return output is the index of the audio device, or the default if none found
# The device index is used by pyaudio to select I/O
def find_device(name='Scarlett'):
    """
    Searches for a Scarlett Audio Interface and returns its device index

    Args:
        name (str): Name of audio device to be found. Defaults to "Scarlett"

    Returns:
        int: Index used to access the audio device with pyaudio
    """
    p = pyaudio.PyAudio()
    # Iterate through all available devices
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        device_name = device_info.get('name')

        # Check if the device name contains name provided
        # In our case this defaults to 'Scarlett'
        if name in device_name:
            print("Found Device: ", device_name)
            p.terminate()
            return i
    p.terminate()
    return 0

def process_file():
    audio_source = "Recordings/simple_scale.wav"
    destination = "temp.out"
    
    os.system("aubio notes " + audio_source + "> " + destination)

    f = open(destination,'r') #read data from destination file  
    data = []
    for line in f:
        cols = line.strip().split('\t')
        data.append(cols)
    
    # first line is the start time
    start_time = data[0][0]
    # second line is the end time
    stop_time = data[-1][0]
    data = data[1:-1] #trim

    # want to change last element of each output to be duration
    for note in data:
        note[2] = float(note[2]) - float(note[1])
        print(note)
    

def process_audio():
    # initialise pyaudio
    p = pyaudio.PyAudio()
    audio_interface_index = find_device()

    # open stream
    pyaudio_format = pyaudio.paFloat32
    num_channels = 1 # This needs to change to 2 or 3
    stream = p.open(format=pyaudio_format,
                    channels=num_channels,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=BUFFER_SIZE,
                    input_device_index=audio_interface_index)

    #TO-DO: Have multiple channel inputs
    #TO-DO: Stop recording on interupt or timeout

    if len(sys.argv) > 1:
        output_filename = sys.argv[1] # file name to record to
        record_duration = None # number of seconds to record 
        outputsink = aubio.sink(sys.argv[1], SAMPLE_RATE) 
        total_frames = 0
    else:
        # run forever
        outputsink = None
        record_duration = None

    # setup pitch
    win_s = 4096 # fft size
    hop_s = BUFFER_SIZE # hop size

    # Create Aubio objects for detection
    aub_pitch = aubio.pitch("default", win_s, hop_s, SAMPLE_RATE)
    aub_onset = aubio.onset("default", win_s, hop_s, SAMPLE_RATE)
    # aub_notes = aubio.notes("default", win_s, hop_s, SAMPLE_RATE)

    #TO-DO Duration functionality

    aub_pitch.set_unit("midi")
    aub_pitch.set_tolerance(PITCH_TOLERANCE)

    #use "phase" Method for polyphonic onset

    print("*** Starting Recording ***")
    while True:
        try:
            audiobuffer = stream.read(BUFFER_SIZE)
            signal = np.frombuffer(audiobuffer, dtype=np.float32)

            pitch = aub_pitch(signal)[0]
            confidence = aub_pitch.get_confidence()

            onset = aub_onset(signal)[0]

            

            if onset != 0: 
                print(f"onset {onset}")
                #print("{} / {}".format(pitch,confidence))
            #write to output file if one is given
            if outputsink: 
                outputsink(signal, len(signal))

            if record_duration:
                total_frames += len(signal)
                if record_duration * SAMPLE_RATE < total_frames:
                    break
        except KeyboardInterrupt:
            print("*** Ctrl+C pressed, Exiting ***")
            break

    print("*** Done Recording ***")
    stream.stop_stream()
    stream.close()
    p.terminate()


process_file()