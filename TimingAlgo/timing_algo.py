# Aakash Sell (asell)


import time


from parse_musicxml import *
from file_conversions import *
from processing import *

import partitura as pt

from music21 import converter, note

def parse_audio(file_path):
    file = open(file_path, mode='r')
    lines = file.readlines()
    file.close

    data = []

    start = float(lines[0].strip())
    end = float(lines[-1].strip())

    lines = lines[1:len(lines)-1]

    for line in lines:
        line_data = line.split()
        tmp_data = (int(float(line_data[0])), float(line_data[1]), float(line_data[2]) - float(line_data[1]))
        data.append(tmp_data)
        
    return data


def find_out_of_sync(shared_notes, singer_sm2audio, piano_sm2audio, singer_audio, piano_audio):
    new_path = []
    s_path = {}
    p_path = {}
    thres = 0.01


    delays = []

    for val in singer_sm2audio:
        s_path[val[0]] = val[1]
        
    for val in piano_sm2audio:
        p_path[val[0]] = val[1]



    for val in shared_notes:
        
        tmp = (s_path[val[0]], p_path[val[1]])
  
        new_path.append(tmp)

    for val in new_path:
        s = singer_audio[val[0]]
        p = piano_audio[val[1]]
        
        diff = s[1] - p[1]

        if diff > thres:
            delays.append((s[1], diff))


    return delays
  




def find_simultaneous_notes(notes1, notes2, time_tolerance=0.01):
    if notes1 is None or notes2 is None:
        raise Exception("invalid files")
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
file_path = "./test.xml"

audio_data = "./temp.out"


def main(sheet_music_path, audio_data_path):

    parts_data = parse_musicxml_file(sheet_music_path)
    delay_data = delayed_music(sheet_music_path)

    singer_sm = parts_data.get('P1', None)
    singer_sm = [(note.Note(val[0]).pitch.midi, val[1], val[2]) for val in singer_sm]

    singer_delay = delay_data.get('P1')
    singer_delay = [(note.Note(val[0]).pitch.midi, val[1], val[2]) for val in singer_delay]


    piano_sm = parts_data.get('P2', None)

    same = find_simultaneous_notes(singer_sm, singer_sm)



    

    



    singer_audio = parse_audio(audio_data_path)

 

    singer_distance, singer_path = process(singer_sm, singer_sm)

    piano_distance, piano_path = process(singer_sm, singer_delay)

    

    piano_audio = None

    out = find_out_of_sync(same, singer_path, singer_path, singer_sm, singer_delay)

    print(out)

    #print(distance)

    #for p in same:
        #print(str(singer_sm[p[0]]) + " + "  + str(piano_sm[p[1]]))

        


    






    





if __name__ == "__main__":
    main(file_path, audio_data)














