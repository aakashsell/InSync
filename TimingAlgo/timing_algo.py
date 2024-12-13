# Aakash Sell (asell)

import math
import sys
import numpy as np
import matplotlib.pyplot as plt
from parse_musicxml import parse_musicxml_file
from processing import *
from music21 import note


# Plot Functions
def plot_music(sheet_data, audio_data, part): 
    plt.figure(figsize=(10, 6))

    # Plot sheet music
    for idx, (pitch, onset, duration) in enumerate(sheet_data):
        plt.plot([onset, onset + duration], [pitch, pitch], color='blue', marker='o', markersize=5, 
                 label="Singer" if idx == 0 else "")

    # Plot audio data
    for idx, (pitch, onset, duration) in enumerate(audio_data):
        plt.plot([onset, onset + duration], [pitch, pitch], color='red', marker='o', markersize=5, 
                 label="Piano" if idx == 0 else "")

    plt.xlabel('Onset Time (s)')
    plt.ylabel('Pitch (MIDI Number)')
    plt.title(f"Sheet Music vs. Audio Data ({part})")
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()


def plot_paths(sheet_data, audio_data, part, matching_paths):
    plt.figure(figsize=(10, 6))
    # Plot sheet music data
    for idx, (pitch, onset, duration) in enumerate(sheet_data):
        plt.plot([onset, onset + duration], [pitch, pitch], color='blue', marker='o', markersize=5, 
                 label="singer" if idx == 0 else "")

    # Plot audio data
    for idx, (pitch, onset, duration) in enumerate(audio_data):
        plt.plot([onset, onset + duration], [pitch, pitch], color='red', marker='o', markersize=5, 
                 label="piano" if idx == 0 else "")

    # Plot matching paths
    for i, j in matching_paths:
        plt.plot([sheet_data[i][1], audio_data[j][1]], [sheet_data[i][0], audio_data[j][0]], 
                 color='green', linestyle='--', label="Matching Path" if (i, j) == matching_paths[0] else "")

    plt.xlabel('Onset Time (s)')
    plt.ylabel('Pitch (MIDI Number)')
    plt.title(f"Corresponding Notes ({part})")
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()


# Utility Functions
def parse_audio(file_path):
    with open(file_path, mode='r') as file:
        lines = file.readlines()
   
    data = []

    for line in lines[0:]:
        line_data = line.split()
        if len(line_data) == 3:
            pitch = int(float(line_data[0]))
            onset = float(line_data[1]) 
            duration = float(line_data[2]) - float(line_data[1])
            data.append((pitch, onset, duration))
    
    return data


def seconds_to_beats(seconds, tempo):
    return math.floor(seconds * (tempo / 60))


def find_out_of_sync(shared_notes, singer_map, piano_map, singer_audio, piano_audio, tempo, thres=0.15):
    delays = []
    delay_path = []
    sev = 0

    for s_idx, p_idx in shared_notes:
        if s_idx in singer_map and p_idx in piano_map:
            singer_note = singer_audio[singer_map[s_idx]]
            piano_note = piano_audio[piano_map[p_idx]]
            diff = singer_note[1] - piano_note[1]

            if diff > thres:
                if diff > 3*thres:
                    sev
                first_beat = seconds_to_beats(singer_note[1], tempo)
                second_beat = first_beat + seconds_to_beats(diff, tempo)
                delays.append((first_beat, second_beat))
                delay_path.append((singer_map[s_idx], piano_map[p_idx]))

    return delays, delay_path, sev


def find_simultaneous_notes(notes1, notes2, time_tolerance=0.01):
    if not notes1 or not notes2:
        raise ValueError("Invalid inputs")

    simultaneous_notes = []
    i, j = 0, 0

    while i < len(notes1) and j < len(notes2):
        onset_diff = abs(notes1[i][1] - notes2[j][1])
        if onset_diff <= time_tolerance:
            simultaneous_notes.append((i, j))
            i += 1
            j += 1
        elif notes1[i][1] < notes2[j][1]:
            i += 1
        else:
            j += 1

    return simultaneous_notes


def remove_duplicate_paths(path):
    return [path[i] for i in range(len(path)) if i == 0 or path[i][0] != path[i - 1][0]]


# Main Algorithm
def timing_algo(sheet_music_path, audio_data_paths, bpm=110):
    parts_data = parse_musicxml_file(sheet_music_path, bpm)
    tempo = parts_data[1]

    # Extract and format sheet music data
    singer_sm = [(note.Note(n[0]).pitch.midi if n[0] != 'rest' else 0, n[1], n[2]) for n in parts_data[0].get('P1', [])]
    piano_sm = [(note.Note(n[0]).pitch.midi if n[0] != 'rest' else 0, n[1], n[2]) for n in parts_data[0].get('P2', [])]
    

    # Parse audio data
    singer_audio = parse_audio(audio_data_paths[0])
    piano_audio = parse_audio(audio_data_paths[1])


    tmp = []
    for val in singer_audio:
        tmp.append((val[0] - 12, val[1], val[2]))
    singer_audio = tmp

    # Process paths
    _, singer_path = process(singer_sm, singer_audio, [1,4,3])
    _, piano_path = process(piano_sm, piano_audio, [1,4,3])

    singer_path = remove_duplicate_paths(singer_path)
    piano_path = remove_duplicate_paths(piano_path)

    # Find out-of-sync notes
    shared_notes = find_simultaneous_notes(singer_sm, piano_sm)
    min_cost, best_weights = float('inf'), None

    '''from itertools import product
    for w1, w2, w3 in product(range(1, 5), range(1, 5), range(1, 5)):
        weights = [w1, w2, w3]


        _, singer_path = process(singer_sm, singer_audio, weights=weights)

        _, piano_path = process(piano_sm, piano_audio, weights=weights)
        delays, new_path = find_out_of_sync(shared_notes, dict(singer_path), dict(piano_path), singer_audio, piano_audio, tempo)


        if len(delays) < min_cost:
            min_cost, best_weights = len(delays), weights, 

    print(f"Best Weights: {best_weights}, Delays: {min_cost}")'''




    delays, new_path, sev = find_out_of_sync(shared_notes, dict(singer_path), dict(piano_path), singer_audio, piano_audio, tempo)



    delays = remove_duplicate_paths(delays)
    print(singer_sm[0])

    #plot_paths(singer_audio, piano_audio, "both", new_path)
    #plot_paths(singer_sm, singer_audio, "singer", singer_path)
    #plot_paths(piano_sm, piano_audio, "piano", piano_path)
    #plt.show()

    return delays

def test_script(sm, audio):
    parts_data = parse_musicxml_file(sm, 110)
    singer_sm = [(note.Note(n[0]).pitch.midi if n[0] != 'rest' else 0, n[1], n[2]) for n in parts_data[0].get('P1', [])]
    piano_sm = [(note.Note(n[0]).pitch.midi if n[0] != 'rest' else 0, n[1], n[2]) for n in parts_data[0].get('P2', [])]
    sm = piano_sm

    audio = parse_audio(audio)


    _, path = process(sm, audio, [0, 400, 0])

        
    
    for line in path:
        print(str(sm[line[0]]) + " + " + str(audio[line[1]]))



    

# Main Execution
if __name__ == "__main__":
    sheet_music = sys.argv[1]
    voice_data = sys.argv[2]
    piano_data = sys.argv[3]
    bpm = 110
    if(len(sys.argv) == 5):
        bpm = int(sys.argv[4])
    
    timing_algo(sheet_music, [voice_data, piano_data], bpm)

    #test_script(sheet_music, piano_data)
