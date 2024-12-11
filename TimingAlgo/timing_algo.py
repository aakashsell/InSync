# Aakash Sell (asell)

import math
import sys
import numpy as np
import matplotlib.pyplot as plt
from parse_musicxml import parse_musicxml_file
from processing import process
from music21 import note
import socket
import struct
import pickle
# Plot Functions
class Info:
    def __init__(self,is_sync, beat):
        self.is_sync = is_sync
        self.beat = beat

def plot_music(sheet_data, audio_data, part): 
    plt.figure(figsize=(10, 6))

    # Plot sheet music
    for idx, (pitch, onset, duration) in enumerate(sheet_data):
        plt.plot([onset, onset + duration], [pitch, pitch], color='blue', marker='o', markersize=5, 
                 label="Sheet Music" if idx == 0 else "")

    # Plot audio data
    for idx, (pitch, onset, duration) in enumerate(audio_data):
        plt.plot([onset, onset + duration], [pitch, pitch], color='red', marker='o', markersize=5, 
                 label="Audio Data" if idx == 0 else "")

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
                 label="Sheet Music" if idx == 0 else "")

    # Plot audio data
    for idx, (pitch, onset, duration) in enumerate(audio_data):
        plt.plot([onset, onset + duration], [pitch, pitch], color='red', marker='o', markersize=5, 
                 label="Audio Data" if idx == 0 else "")

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

    for line in lines[1:]:
        line_data = line.split()
        if len(line_data) == 3:
            pitch = int(float(line_data[0]))
            onset = float(line_data[1])
            duration = float(line_data[2]) - float(line_data[1])
            data.append((pitch, onset, duration))
    
    return data


def seconds_to_beats(seconds, tempo):
    return math.floor(seconds * (tempo / 60))


def find_out_of_sync(shared_notes, singer_map, piano_map, singer_audio, piano_audio, tempo, thres=0.1):
    delays = []
    delay_path = []

    for s_idx, p_idx in shared_notes:
        if s_idx in singer_map and p_idx in piano_map:
            singer_note = singer_audio[singer_map[s_idx]]
            piano_note = piano_audio[piano_map[p_idx]]
            diff = singer_note[1] - piano_note[1]

            if diff > thres:
                first_beat = seconds_to_beats(singer_note[1], tempo)
                second_beat = first_beat + seconds_to_beats(diff, tempo)
                delays.append((first_beat, second_beat))
                delay_path.append((singer_map[s_idx], piano_map[p_idx]))

    return delays, delay_path


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
def timing_algo(sheet_music_path, audio_data_paths):
    parts_data = parse_musicxml_file(sheet_music_path, 110)
    tempo = parts_data[1]

    # Extract and format sheet music data
    singer_sm = [(note.Note(n[0]).pitch.midi if n[0] != 'rest' else 0, n[1], n[2]) for n in parts_data[0].get('P1', [])]
    piano_sm = [(note.Note(n[0]).pitch.midi if n[0] != 'rest' else 0, n[1], n[2]) for n in parts_data[0].get('P2', [])]

    # Parse audio data
    singer_audio = parse_audio(audio_data_paths[0])
    piano_audio = parse_audio(audio_data_paths[1])

    # Process paths
    _, singer_path = process(singer_sm, singer_audio)
    _, piano_path = process(piano_sm, piano_audio)

    singer_path = remove_duplicate_paths(singer_path)
    piano_path = remove_duplicate_paths(piano_path)

    # Find out-of-sync notes
    shared_notes = find_simultaneous_notes(singer_sm, piano_sm)
    delays, new_path = find_out_of_sync(shared_notes, dict(singer_path), dict(piano_path), singer_audio, piano_audio, tempo)
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65432  # The port used by the server
    # Plot results
    print(delays)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        for status in delays:
        
            res = Info(False, status[0])
            print(f"beat: {res.beat}, start_status: {res.is_sync}")
            
            my_bytes = pickle.dumps(res)
            print(f"test {len(my_bytes)}")
            s.sendall(struct.pack('!i', status[0]))
            s.recv(1024)

            res = Info(True, status[1])
            print(f"beat: {res.beat}, start_status: {res.is_sync}")
            
            my_bytes = pickle.dumps(res)
            print(f"test {len(my_bytes)}")
            s.sendall(struct.pack('!i', status[1]))
            s.recv(1024)
    plot_paths(singer_sm, singer_audio, "Singer", singer_path)
    plt.show()


# Main Execution
if __name__ == "__main__":
    sheet_music = sys.argv[1]
    voice_data = sys.argv[2]
    piano_data = sys.argv[3]
    
    timing_algo(sheet_music, [voice_data, piano_data])
