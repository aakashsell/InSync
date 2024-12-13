#! /usr/bin/env python

# Some portions of code modified from:
#    $ ./python/demos/demo_pyaudio.py
#    $ ./python/demos/demo_pyaudio.py /tmp/recording.wav

'''
    InSync Project, audio processing file. Performs the following operations

    Recording:
        Selects specified audio interface and records sound to a .wav file based
        on command line input. Will pipe recorded data into the Audio Processing
        methods automatically.
    
    Audio Processing:
        Processes a .wav file into a tuple of data in the form:
        {Midi Note, Start Time (seconds), Duration (seconds)}

        Uses the Aubio library to perform pitch estimation, note onset timing, and
        (less accurately) note duration. Note duration is calculated using the 
        produced start and end timing values from the aubio notes process. pitch
        estimation is performed using a FFT which finds the moving average between
        note onsets based on Aubio's fundamental frequency detection algorithm.
'''
import numpy as np # Sspecific float data type
import aubio # Audio processing
import pyaudio # Audio recording
import os # Run aubio command line tools
import wave

import sys # Get arguments
from utils.util_Conversions import *
from utils.util_Constants import * 

# Index Constants for data tuple
MIDI_INDEX = 0
ONSET_INDEX = 1
DURATION_INDEX = 2
STOP_INDEX = 2
MAX_MIDI = 200

# Global Semaphore 
VERBOSE_MODE = False # If enabled, print information while recording
RECORDING = -1 # Set to 1 if a piece is being recorded
AUDIO_FORMAT = pyaudio.paFloat32

def data_to_line(midi:float, onset:float, duration:float):
    """
        Converts note data into a line of formatted output data. Rounds float 
        values to 3 decimal places.

        Args:
            midi (float): midi value of the note
            onset (float): onset time of the note
            duration (float): duration of the note
        Returns:
            string (str): string containing args sequentially seperated by a tab
    """
    return format(f"{midi:.0f}\t{onset:.4f}\t{duration:.4f}")

def line_to_data(line:str):
    """
        Converts a unprocessed string of float data and seperates it into a tuple of
        floats using the tab (\t) delimiter

        Args:
            line (str): line in file to process
        Returns:
            tuple ([float]): tuple of float values
    """
    l = line.strip().split('\t')
    for i in range(len(l)):
        l[i] = round(float(l[i]), 4)
    return l

def find_device(name='Scarlett'):
    """
    Searches for a Scarlett Audio Interface and returns its device index. Returns
    default audio device of the system (typically built-in microphone) if none found.
    The device index is used by pyaudio to select I/O

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
    """
        Converts a wav file given as the audio source into a data stream of tuples
        containing the detected pitch (midi value), its time of onset, and its approximate duration.
        Periods of silence are marked by a midi value of 0. 

        Args:
            audio_source (str): A string containing the file path of a .wav file to process
        Returns:
            None
    """
    destination = "temp.out"
    os.system("aubio notes " + audio_source + " -s -55 " +" > " + destination)
    f = open(destination,'r') #read data from destination file  
    
    unprocessed_data = []
    for line in f: unprocessed_data.append(line_to_data(line))
    # unprocessed_data is now an 2D array where each line contains
    # [midi val, start time, duration]
        
    processed_note_data = []
    for line in range(len(unprocessed_data)):
        line_data = unprocessed_data[line]
        
        # Silence detected, if at end (no next), ignore
        if(len(line_data) == 1):
            curr_midi = 0
            curr_start = line_data[0]
            
            #last line of the output, ignore silence
            if(line == len(unprocessed_data)-1): 
                break
            else:
                # find previous ending
                prev_end = 0
                if(line != 0): #not the first entry
                    prev_data = unprocessed_data[line-1]
                    if(len(prev_data) == 3):
                        prev_end = prev_data[STOP_INDEX]
                    else:
                        # in theory should never execute
                        prev_line = line - 2
                        while(prev_line > 0):
                            prev_data = unprocessed_data[line-1]
                            if(len(prev_data) == 3):
                                prev_end = prev_data[STOP_INDEX]

                # Find next start, if none exists ignore
                next_line_data = unprocessed_data[line+1]
                if(len(next_line_data) == 3):
                    next_midi, next_start, next_end = next_line_data
                    duration = next_start - prev_end
                    if(duration == 0): 
                        continue
                    else:
                        temp_data = [curr_midi, prev_end, duration]
                        processed_note_data.append(temp_data)
                else:
                    #multiple silence values
                    next_line = line+2
                    while(next_line < len(unprocessed_data)-1):
                        #try to find non silent processed_note_data
                        next_line_data = line_to_data(f[next_line])
                        if(len(next_line_data) == 3):
                            next_start = next_line_data[STOP_INDEX]
                            temp_data = [curr_midi, curr_start, next_start-curr_start]
                            duration = next_start - prev_end
                            if(duration == 0): 
                                continue
                            else:
                                temp_data = [curr_midi, curr_start, duration]
                                processed_note_data.append(temp_data)
        elif(len(line_data) == 3):
            curr_midi, curr_start, curr_end = line_data
            temp_data = [curr_midi, curr_start, curr_end-curr_start]

            # Value outside threshold, attempt to append to next note
            if(curr_midi > MAX_MIDI and line != len(unprocessed_data)-1):
                next_line_data = unprocessed_data[line+1]

                if(len(next_line_data) == 3):
                    next_midi, next_start, next_end = next_line_data
                    temp_data = [next_midi, curr_start, next_end-curr_start]
                else: #Next value is silence
                    pass

            processed_note_data.append(temp_data)
    f.close()

    # normalize starting time
    start_time_ofset = 0
    if(processed_note_data[0][MIDI_INDEX] == 0):
        start_time_ofset = processed_note_data[0][DURATION_INDEX]
        processed_note_data = processed_note_data[1:]
    
    processed_data_out = open("modfied.out", 'w')
    for note in processed_note_data:
        note[ONSET_INDEX] = note[ONSET_INDEX] - start_time_ofset
        line = data_to_line(note[MIDI_INDEX], note[ONSET_INDEX], note[DURATION_INDEX])
        processed_data_out.write(line + "\n")
        if VERBOSE_MODE:
            pitch, start, duration = line_to_data(line)
            pitch = aubio.midi2note(int(float(pitch)))
            print(f"({pitch},{start},{duration})")
    processed_data_out.close()
                   
def record_audio(filename:str, audio_interface_index:int, num_channels:int=1):
    """
        Records an audio stream into a .wav file created from the file name given.
        Then processes the audio file into an output file.

        Args:
            filename (str): Name of the produced .wav file -> filename.wav
            audio_interface_index (int): Audio interface to record from
            num_channels (int): Number of input channels to record from the audio interface
    """
    
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

    outputsink = aubio.sink(filename, SAMPLE_RATE) 

    # setup pitch
    win_s = 4096 # fft size
    hop_s = BUFFER_SIZE # hop size

    # Create Aubio objects for detection
    aub_pitch = aubio.pitch("default", win_s, hop_s, SAMPLE_RATE)
    aub_onset = aubio.onset("default", win_s, hop_s, SAMPLE_RATE)

    aub_pitch.set_unit("midi")
    aub_pitch.set_tolerance(PITCH_TOLERANCE)

    #use "phase" Method for polyphonic onset

    print("*** Starting Recording ***")
    if VERBOSE_MODE:
        print("Recording to \"Recordings/" + filename)
    
    wav_data = []
    
    while RECORDING:
        try:
            audiobuffer = stream.read(BUFFER_SIZE)
            signal = np.frombuffer(audiobuffer, dtype=np.float32)
            wav_data.append(signal)

            pitch = aub_pitch(signal)[0]
            confidence = aub_pitch.get_confidence()

            onset = aub_onset(signal)[0]

            if VERBOSE_MODE:
                if onset != 0: 
                    print(f"onset {onset}")
                    print("{} / {}".format(pitch,confidence))

        except KeyboardInterrupt:
            print("*** Ctrl-C Pressed, Exiting ***")
            break

    print("*** Done Recording ***")

    # Clean up PyAudio
    stream.stop_stream()
    stream.close()
    audio_data.terminate()

    # Create WAV file
    output_file_name = RECORDING_PREFIX + ".wav"
    wav_file = wave.open(output_file_name, 'wb')
    wav_file.setnchannels(num_channels)
    wav_file.setsampwidth(audio_data.get_sample_size(AUDIO_FORMAT))
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(b''.join(wav_data))
    wav_file.close()

    # Run Audio Processing
    process_file(output_file_name)

import argparse

parser = argparse.ArgumentParser(description="Initializing InSync...")
parser.add_argument("-f","--filename", help="Path of file to process. Does not record audio")
parser.add_argument("-b","--bpm", help="The bpm of the piece")
parser.add_argument("-p","--piece", help="Name of the piece used to label recordings")
parser.add_argument("-v","--verbose", help="Provides verbose output during recording", action='store_false')

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
    record_audio(RECORDING_PREFIX, device_index)   
else:
    process_file(FILENAME_TO_PROCESS)

# TODO:
# Set up stereo input scarlett input for piano microphones
# Record both seperately into two files
    # Files need to have a naming convention
    # Have multiple channel inputs
# From each file run Aubio notes to generate output
    # Check for articulations
    # Attempt chord handling
