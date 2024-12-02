# Aakash Sell (asell)


import math


from parse_musicxml import *
from processing import *
import matplotlib.pyplot as plt
from tests import *


from music21 import note


def plot_music(sheet_data, audio_data, part): 
    plt.figure(figsize=(10, 6))

    for pitch, onset, duration in sheet_data:
        plt.plot([onset, onset + duration], [pitch, pitch], color='blue', marker='o', markersize=5, label="Sheet Music" if onset == sheet_data[0][1] else "")

    for pitch, onset, duration in audio_data:
        plt.plot([onset, onset + duration], [pitch, pitch], color='red', marker='o', markersize=5, label="Audio Data" if onset == audio_data[0][1] else "")

    plt.xlabel('Onset Time (s)')
    plt.ylabel('Pitch (MIDI Number)')
    title = "Sheet Music vs. Audio Data ({part})".format(part=part)
    plt.title(title)

    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

    plt.tight_layout()

def plot_paths(sheet_data, audio_data, part, matching_paths):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))

    # Plot sheet music data
    for idx, (pitch, onset, duration) in enumerate(sheet_data):
        plt.plot(
            [onset, onset + duration],
            [pitch, pitch],
            color='blue',
            marker='o',
            markersize=5,
            label="Singer Sheet Music" if idx == 0 else ""
        )

    # Plot audio data
    for idx, (pitch, onset, duration) in enumerate(audio_data):
        plt.plot(
            [onset, onset + duration],
            [pitch, pitch],
            color='red',
            marker='o',
            markersize=5,
            label="Singer Audio Data" if idx == 0 else ""
        )

    # Plot matching paths
    for i, j in matching_paths:
        sheet_point = sheet_data[i]
        audio_point = audio_data[j]
        plt.plot(
            [sheet_point[1], audio_point[1]],
            [sheet_point[0], audio_point[0]],
            color='green',
            linestyle='--',
            label="Matching Path" if (i, j) == matching_paths[0] else ""
        )

    plt.xlabel('Onset Time (s)')
    plt.ylabel('Pitch (MIDI Number)')
    title = f"Corresponding Notes"
    plt.title(title)

    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

    plt.tight_layout()


def show_delays(sheet_data, audio_data, part, matching_paths):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))

    # Plot sheet music data
    for idx, (pitch, onset, duration) in enumerate(sheet_data):
        plt.plot(
            [onset, onset + duration],
            [pitch, pitch],
            color='blue',
            marker='o',
            markersize=5,
            label="Singer Audio" if idx == 0 else ""
        )

    # Plot audio data
    for idx, (pitch, onset, duration) in enumerate(audio_data):
        plt.plot(
            [onset, onset + duration],
            [pitch, pitch],
            color='red',
            marker='o',
            markersize=5,
            label="Piano Audio" if idx == 0 else ""
        )

    # Plot matching horizontal lines at the bottom
    y_bottom = min([pitch for pitch, _, _ in sheet_data + audio_data]) - 5
    for i, j in matching_paths:
        sheet_point = sheet_data[i]
        audio_point = audio_data[j]
        plt.plot(
            [sheet_point[1], audio_point[1]],
            [y_bottom, y_bottom],
            color='green',
            linestyle='--',
            label="Delay" if (i, j) == matching_paths[0] else ""
        )

    plt.xlabel('Onset Time (s)')
    plt.ylabel('Pitch (MIDI Number)')
    title = f"Delays ({part})"
    plt.title(title)

    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

    plt.tight_layout()





def parse_audio(file_path):
    file = open(file_path, mode='r')
    lines = file.readlines()
    file.close

    data = []

    start = float(lines[0].strip())
    #end = float(lines[-1].strip())

    lines = lines[1:len(lines)]

    for i in range(0, len(lines)):
        line = lines[i]
        line_data = line.split()


        if(len(line_data) == 3):

            pitch = int(float(line_data[0]))
            onset = float(line_data[1]) - start
            duration = float(line_data[2]) - float(line_data[1])

            tmp_data = (pitch, onset, duration)
            data.append(tmp_data)
    
    
        
    return data

# tempo = bpm
# 60/tempo = bps
# tempo/60 * seconds = beats
def seconds_to_beats(seconds, tempo):
    return math.floor(seconds * (tempo/60))


def find_out_of_sync(shared_notes, singer_sm2audio, piano_sm2audio, singer_audio, piano_audio, tempo):
    new_path = []
    s_path = {}
    p_path = {}
    thres = 0.1

    delay_path = []

    delays = []

    for val in singer_sm2audio:
        s_path[val[0]] = val[1]
        
    for val in piano_sm2audio:
        p_path[val[0]] = val[1]

    for val in shared_notes:
        if val[0] in s_path and val[1] in p_path:  # Ensure indices exist
            tmp = (s_path[val[0]], p_path[val[1]])
            new_path.append(tmp)

    # Calculate delays
    for val in new_path:
        s = singer_audio[val[0]]
        p = piano_audio[val[1]]

        
        diff = s[1] - p[1] # Difference in onset times

        if diff > thres:            
            #delays.append((seconds_to_beats(s[1], tempo), seconds_to_beats(diff, tempo))) 

            delay_path.append(val)
             

            first_beat = seconds_to_beats(s[1], tempo)
            second_beat = first_beat + seconds_to_beats(diff, tempo)

            delays.append((first_beat, second_beat))  
            #delays.append(seconds_to_beats(s[1], tempo))

    return delays, delay_path


  




def find_simultaneous_notes(notes1, notes2, time_tolerance=0.01):
    if notes1 is None or notes2 is None:
        raise Exception("invalid inputs")
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


# get sheetmusic




# Example usage
file_path = "./sheet_music/FMTM.xml"

voice_data = "./audio_data/perf.out"

piano_data = "./audio_data/piano.out"


def remove_duplicate_paths(path):
    final_path = []
    final_path.append(path[0])
    for i in range(1, len(path)):
        if path[i][0] != path[i-1][0]:
            final_path.append(path[i])
    return final_path



def timing_algo(sheet_music_path, audio_data_path):
    
    print("Parsing Sheet Music")
    print()
    parts_data = parse_musicxml_file(sheet_music_path, 110)

    
    print("Recieving Singer Portion of Sheet Music")
    singer_sm = parts_data[0].get('P1', None)
    singer_sm = [(note.Note(val[0]).pitch.midi if val[0] != 'rest' else 0, val[1], val[2]) for val in singer_sm]
    for i in range(5):
        print(singer_sm[i])
    print("...")
    print()




    print("Recieving Piano Portion of Sheet Music")
    piano_sm = parts_data[0].get('P2', None)
    piano_sm = [(note.Note(val[0]).pitch.midi if val[0] != 'rest' else 0, val[1], val[2]) for val in piano_sm]
    for i in range(5):
        print(piano_sm[i])
    print("...")
    print()

    tempo = parts_data[1]



    print("Finding Shared Simultanious notes between singer and pianist")
    same = find_simultaneous_notes(singer_sm, piano_sm)
    for i in range(5):
        print(same[i])
    print("...")
    print()



    print("Parsing singer audio data")
    singer_audio = parse_audio(audio_data_path[0])
    for i in range(5):
        print(singer_audio[i])
    print("...")
    print()

    print("Parsing piano audio data")
    piano_audio = parse_audio(audio_data_path[1])
    for i in range(5):
        print(piano_audio[i])
    print("...")
    print()
    


    print("Aligning Singer sheet music and audio data")
    singer_distance, singer_path = process(singer_sm, singer_audio)
    singer_path = remove_duplicate_paths(singer_path)


    clean_singer = []
    past_s = -1
    for val in singer_path:
        if val[1] != past_s:
            past_s = val[1]
            clean_singer.append(val)
    singer_path = clean_singer

    for i in range(5):
        print(singer_path[i])
    print("...")
    print()


    print("Aligning Piano sheet music and audio data")
    piano_distance, piano_path = process(piano_sm, piano_audio)


    clean_pianos = []
    past_p = -1
    for val in piano_path:
        if val[1] != past_p:
            past_p = val[1]
            clean_pianos.append(val)
    piano_path = clean_pianos

    piano_path = remove_duplicate_paths(piano_path)
    for i in range(5):
        print(piano_path[i])
    print("...")
    print()

    print("Finding where the two audio data sets are out of sync")
    out_of_sync = find_out_of_sync(same, singer_path, piano_path, singer_audio, piano_audio, tempo)
    delays = out_of_sync[0]

    new_path = out_of_sync[1]


    clean_delays = []
    past_val = -1
    for val in new_path:
        if val[1] != past_val:
            past_val = val[1]
            clean_delays.append(val)


    for i in range(5):
        pass
        print(delays[i])
    print("...")
    print()

    for val in singer_audio:
        print(val)




    #plot_music(singer_sm, singer_audio, "singer")

    plot_paths(singer_sm, singer_audio, "singer", singer_path)


    #plot_paths(singer_audio, piano_audio, "Both", clean_delays)

    #show_delays(singer_audio, piano_audio, "both", clean_delays)

    #print(singer_path)


    plt.show()



    


    




 

    

    piano_audio = None



    
    






    





if __name__ == "__main__":
    timing_algo(file_path, [voice_data, piano_data])
    #parts_data = parse_musicxml_file(file_path, 110)
    #print(parts_data[0].get("P2"))














