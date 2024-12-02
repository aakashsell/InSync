"""
Author: Ben Martinez
Last Updated: 11/5/24

Utility functions that help handle conversions between time and bpm, midi value 
and readable pitch object.
"""

import aubio
import math

def util_midi_to_note(midi:float):
    note = round(midi)
    return aubio.midi2note(note)

def midi_to_note(midi:int):
    """
    Converts a MIDI value (0-127) to a pitch descriptor (i.e C4)
    Ex. midi_to_note(60) -> C4
    Best used for debugging purposes

    Args:
        midi (int): A MIDI value 0-127 inclusive

    Returns:
        str: A char representing the note (A-G), accidental (b,#), octave number (-2,8)
    """
    notes = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
    NUM_SEMITONES = 12 # Number of notes in an octave
    MIN_OCTAVE = -2 # Lowest possible octave

    octave = (midi // NUM_SEMITONES) + MIN_OCTAVE
    pitch = notes[midi % NUM_SEMITONES]

    return pitch + str(octave)

def seconds_per_beat(bpm:int):
    """
    Converts Beats per Minute (BPM) to seconds per note
    Ex. seconds_per_beat(120) -> 0.5

    Args:
        bpm (int): Beats per minute

    Returns:
        float: Seconds per beat
    """
    return 60/bpm

def beats_from_duration(duration:float, bpm:int):
    """
    Finds the number of beats a note was

    Args:
        duration (float): Duration of note, in seconds
        bpm (int): beats per minute of piece

    Returns:
        float: Number of beats the note lasted
    """
    seconds_per_beat = seconds_per_beat(bpm)
    return duration/seconds_per_beat

def beat_to_samples(dur:float, bpm:int=60):
    60/bpm
    #ex. quater note 0.25 at 60bpm is 44100 samples
    
#def avg_pitch(values:List[float]):

#def seperate_notes():


