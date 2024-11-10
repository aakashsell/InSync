# Aakash Sell (asell)


import time

from fastdtw import fastdtw
import numpy as np



from parse_musicxml import *
from file_conversions import *
from processing import *

import partitura as pt

from music21 import converter, note


def find_simultaneous_notes(notes1, notes2, time_tolerance=0.01):
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
file_path = "./music.xml"


def main():
    pass

    parts_data = parse_musicxml_file(file_path)

    singer_sm = parts_data['P1']

    piano_sm = parts_data['P2']

    s_onsets = [val[1] for val in singer_sm]
    p_onsets = [val[1] for val in piano_sm]

    
    singer_delayed = create_delayed(file_path)['P1']
    piano_delayed = create_delayed(file_path)['P2']


    s_real = [(note.Note(val[0]).pitch.midi, val[1], val[2]) for val in singer_sm]
    s_delay = [(note.Note(val[0]).pitch.midi, val[1], val[2]) for val in singer_delayed]

    p_real = [(note.Note(val[0]).pitch.midi, val[1], val[2]) for val in piano_sm]
    p_delay = [(note.Note(val[0]).pitch.midi, val[1], val[2]) for val in singer_sm]




    idk = find_simultaneous_notes(singer_sm, singer_delayed)


    #for val in idk:
        #print(str(singer_delayed[val[0]]) + ' and ' + str(piano_sm[val[1]]))

    
    distance, path = process(s_real, s_delay)

    print(singer_sm)

 

    #for val in path:
       #print(str(singer_sm[val[0]]) + " " + str(singer_delayed[val[1]]))



    





if __name__ == "__main__":
    main()














