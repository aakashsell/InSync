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
from os.path import join
from threading import *
import wave

from queue import Queue
from sounddevice import InputStream
from soundfile import SoundFile

import sys # Get arguments
from Utils.util_Conversions import *
from Utils.util_Constants import *

# Index Constants for data tuple
MIDI_INDEX = 0
ONSET_INDEX = 1
DURATION_INDEX = 2
STOP_INDEX = 2

# Global Semaphore 
VERBOSE_MODE = False # If enabled, print information while recording
RECORDING = -1 # Set to 1 if a piece is being recorded

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

def process_file(audio_source:str, silence_threshold:int=-55, suffix:str="_voice", ):
    """
        Converts a wav file given as the audio source into a data stream of tuples
        containing the detected pitch (midi value), its time of onset, and its approximate duration.
        Periods of silence are marked by a midi value of 0. 

        Args:
            audio_source (str): A string containing the file path of a .wav file to process
        Returns:
            None
    """
    destination = "../DSP/Outputs/temp" + suffix + ".out"

    source = "aubio notes " + audio_source
    silence = f" -s {silence_threshold}"
    onset = "" #" -o " + onset_type # Change for polyphonic onsets
    dest = " > " + destination

    print(source + silence + onset + dest)
    os.system(source + silence + onset + dest)
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
                        pass
                        '''prev_line = line - 2
                        while(prev_line > 0):
                            prev_data = unprocessed_data[line-1]
                            if(len(prev_data) == 3):
                                prev_end = prev_data[STOP_INDEX]'''

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
                        next_line_data = unprocessed_data[next_line]
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
    start_time_opiano_streamet = 0
    if(processed_note_data[0][MIDI_INDEX] == 0):
        start_time_opiano_streamet = processed_note_data[0][DURATION_INDEX]
        processed_note_data = processed_note_data[1:]
    
    processed_data_out = open("../DSP/Outputs/modfied" + suffix + ".out", 'w')
    for note in processed_note_data:
        note[ONSET_INDEX] = note[ONSET_INDEX] - start_time_opiano_streamet
        line = data_to_line(note[MIDI_INDEX], note[ONSET_INDEX], note[DURATION_INDEX])
        processed_data_out.write(line + "\n")
        if VERBOSE_MODE:
            pitch, start, duration = line_to_data(line)
            pitch = aubio.midi2note(int(float(pitch)))
            print(f"({pitch},{start},{duration})")
    processed_data_out.close()

def find_device(name:str):
    """
    Searches for a Scarlett Audio Interface and returns its device index. Returns
    default audio device of the system (typically built-in microphone) if none found.
    The device index is used by pyaudio to select I/O

    Args:
        name (str): Name of audio device to be found. Returns first index if
        multiple found.

    Returns:
        int: Index used to access the audio device with pyaudio. Returns -1 if
        not found.
    """
    p = pyaudio.PyAudio()
    # Iterate through all available devices
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        device_name = device_info.get('name')

        # Check if the device name contains name provided
        if name in device_name:
            print("Found Device: ", device_name)
            p.terminate()
            return i
    p.terminate()
    return -1

def file_writing_thread(*, q, **soundfile_args):
    # Write data from queue to file until *None* is received
    with SoundFile(**soundfile_args) as f:
        while True:
            data = q.get()
            if data is None:
                break
            f.write(data)

def record_devices(voice_id:int, piano_id:int, piece:str):
    def create_callback(q):
        def callback(data, frames, time, status):
            if status:
                print(status)
            q.put(data.copy())

        return callback

    voice_queue = Queue()
    piano_queue = Queue()

    voice_stream = InputStream(
        device=voice_id,
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=create_callback(voice_queue),
    )
    piano_stream = InputStream(
        device=piano_id,
        samplerate=SAMPLE_RATE,
        channels=2,
        callback=create_callback(piano_queue),
    )

    voice_file = SoundFile(
        file=f"{piece}_voice.wav",
        mode="w",
        samplerate=int(voice_stream.samplerate),
        channels=voice_stream.channels,
    )
    piano_file = SoundFile(
        file=f"{piece}_piano.wav",
        mode="w",
        samplerate=int(piano_stream.samplerate),
        channels=piano_stream.channels,
    )

    with voice_file, piano_file:
        with voice_stream, piano_stream:
            print("press Ctrl+C to stop the recording")
            try:
                while True:
                    voice_file.write(voice_queue.get())
                    piano_file.write(piano_queue.get())
            except KeyboardInterrupt:
                print("\nDone Recording")
    piano_file_name = piece + "_piano.wav"
    voice_file_name = piece + "_voice.wav"

    process_file(audio_source=piano_file_name ,suffix="_piano")
    process_file(audio_source=voice_file_name, suffix="_voice")

def record_device(device_id:int, channels:int, piece:str):
    def audio_callback(data, frames, time, status):
        # Called for each audio block per thread
        if status:
            print(status, file=sys.stderr)
        audio_q.put(data.copy())

    file_name = piece + ".wav"

    stream = InputStream(
        samplerate=SAMPLE_RATE, 
        device=device_id, 
        channels=channels, 
        callback=audio_callback
    )
    stream.start()
    print(f"started stream {stream} ...")

    audio_q = Queue()
    print(f"generated queue {audio_q} ...")

    thread = Thread(
        target=file_writing_thread,
        kwargs=dict(
            file=file_name,
            mode="w",
            samplerate=int(stream.samplerate),
            channels=stream.channels,
            q=audio_q,
        ),
    )
    thread.start()
    # if VERBOSE_MODE:
    #     print(f"started thread {thread} ...")
    #     print(f'recording file "{file_name}" ...')
    #     print("#" * 40)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initializing InSync...")
    parser.add_argument("-f","--filename", help="Path of file to process. Does not record audio")
    parser.add_argument("-b","--bpm", help="The bpm of the piece")
    parser.add_argument("-p","--piece", help="Name of the piece used to label recordings")
    parser.add_argument("-v","--verbose", help="Provides verbose output during recording", action='store_false')

    args = parser.parse_args()

    FILENAME_TO_PROCESS = "" # Filename of audiofile to process
    NAME_OF_PIECE = "" # Name of music piece to add into recording filename

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
            NAME_OF_PIECE = args.piece
        elif arg == "-v":
            VERBOSE_MODE = True

    if RECORDING:
        rec_dir = join("../DSP/Recordings", NAME_OF_PIECE) # Pathname of .wav files
        piano_id = find_device("Scarlett 2i2")
        voice_id = find_device("Scarlett Solo")
        record_devices(voice_id, piano_id, rec_dir)
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
