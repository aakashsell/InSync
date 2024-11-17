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
from pynput import keyboard

import numpy as np # Sspecific float data type
import aubio # Audio processing
import pyaudio # Audio recording
import os # Run aubio command line tools

import sys # Get arguments

# Constants for audio stream
BUFFER_SIZE = 1024  # Standard Buffer Size
SAMPLE_RATE = 44100  # Common sample rate for audio
PITCH_TOLERANCE = 0.8 # Required confidence of pitch value
DEFAULT_BPM = 120 # Number of quarter-notes per minute
AUDIO_FORMAT = pyaudio.paFloat32 # Float format of audio data

# Global Semaphore 
VERBOSE_MODE = False # If enabled, print information while recording
RECORDING = -1 # Set to 1 if a piece is being recorded

def key_press_handler(key):
    if key == 's':  # Interrupt on 's' key press
        RECORDING = 0

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

def process_file(audio_source:str):
    # audio_source = "Test_Recordings/simple_scale.wav"
    destination = "temp.out"
    
    os.system("aubio notes " + audio_source + " > " + destination)

    f = open(destination,'r') #read data from destination file  
    data = []
    for line in f:
        cols = line.strip().split('\t')
        data.append(cols)
    
    # first line is the start time
    start_time = data[0]
    # second line is the end time
    stop_time = data[-1][0]
    data = data[1:-1] #trim

    # want to change last element of each output to be duration
    for note in data:
        try:
            if (note[0] < 100):
                note[2] = float(note[2]) - float(note[1])
                print(note)
        except: 
            pass
    
def record_audio(filename:str, audio_interface_index:int, num_channels:int=1):
    # initialise pyaudio
    audio_data = pyaudio.PyAudio()
    audio_interface_index = find_device()

    # open stream
    stream = audio_data.open(format=AUDIO_FORMAT,
                    channels=num_channels,
                    rate=SAMPLE_RATE,
                    input=True,
                    output=True,
                    frames_per_buffer=BUFFER_SIZE,
                    input_device_index=audio_interface_index)

    #TO-DO: Have multiple channel inputs
    #TO-DO: Stop recording on interupt or timeout
    outputsink = aubio.sink(filename, SAMPLE_RATE) 

    # setup pitch
    win_s = 4096 # fft size
    hop_s = BUFFER_SIZE # hop size

    # Create Aubio objects for detection
    aub_pitch = aubio.pitch("default", win_s, hop_s, SAMPLE_RATE)
    aub_onset = aubio.onset("default", win_s, hop_s, SAMPLE_RATE)

    #TO-DO Duration functionality

    aub_pitch.set_unit("midi")
    aub_pitch.set_tolerance(PITCH_TOLERANCE)

    #use "phase" Method for polyphonic onset

    # Create a thread for monitoring keyboard input
    # listener = keyboard.Listener(on_press=key_press_handler)
    # listener.start()

    print("*** Starting Recording ***")
    if VERBOSE_MODE:
        print("Recording to \"Recordings/" + filename)
    
    while RECORDING:
        try:
            audiobuffer = stream.read(BUFFER_SIZE)
            signal = np.frombuffer(audiobuffer, dtype=np.float32)

            pitch = aub_pitch(signal)[0]
            confidence = aub_pitch.get_confidence()

            onset = aub_onset(signal)[0]

            if VERBOSE_MODE:
                if onset != 0: 
                    print(f"onset {onset}")
                    print("{} / {}".format(pitch,confidence))
            
            #write to output file if one is given
            if outputsink: 
                outputsink(signal, len(signal))

        # Make this a generic keyboard input
        except KeyboardInterrupt:
            print("*** Ctrl-C Pressed, Exiting ***")
            break

    print("*** Done Recording ***")
    stream.stop_stream()
    stream.close()
    audio_data.terminate()



import argparse

parser = argparse.ArgumentParser(description="Initializing InSync...")
parser.add_argument("-f","--filename", help="Path of file to process. Does not record audio")
parser.add_argument("-b","--bpm", help="The bpm of the piece")
parser.add_argument("-p","--piece", help="Name of the piece used to label recordings")
parser.add_argument("-v","--verbose", help="Provides verbose output during recording")

args = parser.parse_args()

FILENAME_TO_PROCESS = "" # Filename of audiofile to process
RECORDING_PREFIX = "" # Name of music piece to add into recording filename

if len(sys.argv) < 1:
    print("Please provide the name of the music piece (-p) to record or a \
    filename (-f) to process.")
    sys.exit(1)

for arg in sys.argv[1:]:
    if arg == '-f':
        if RECORDING != -1:
            print("Cannot process a file and record at the same time")
            sys.exit()
        RECORDING = 0
        FILENAME_TO_PROCESS = args.filename
    elif arg == '-b':
        DEFAULT_BPM = int(args.bpm)
    elif arg == "-p":
        if RECORDING != -1:
            print("Cannot record and process a file at the same time")
            sys.exit()
        RECORDING = 1
        RECORDING_PREFIX = args.piece
    elif arg == "-v":
        VERBOSE_MODE = True

if RECORDING:
    device_index = find_device()
    record_audio(RECORDING_PREFIX,device_index)
    
process_file(FILENAME_TO_PROCESS)

# Set up single input scarlett input for singer microphone
# Set up stereo input scarlett input for piano microphones
# Record both seperately into two files
    # Files need to have a naming convention
# From each file run Aubio notes to generate output
    # Filter out noise
    # Check for articulations
    # Attampt chord handling
    # Clean up and save in data folder
