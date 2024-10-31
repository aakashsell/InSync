# Aakash Sell (asell)


import time

from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import numpy as np



from parse_musicxml import *
from file_conversions import *
from processing import *

import partitura as pt

from music21 import converter, note



# get sheetmusic




# Example usage
file_path = "./music.xml"


def main():
    pass

    parts_data, time_signature = parse_musicxml_file(file_path)

    singer_sm = parts_data['P1']

    piano_sm = parts_data['P2']

    
    singer_delayed = create_delayed(file_path)['P1']
    piano_delayed = create_delayed(file_path)['P2']

    s_real = [(note.Note(val[0]).pitch.midi, val[1], val[2]) for val in singer_sm]
    s_delay = [(note.Note(val[0]).pitch.midi, val[1], val[2]) for val in singer_delayed]

    p_real = [(note.Note(val[0]).pitch.midi, val[1], val[2]) for val in piano_sm]
    p_delay = [(note.Note(val[0]).pitch.midi, val[1], val[2]) for val in singer_sm]

    create_musicxml_from_parts({'P1': singer_sm}, time_signature)

    print(singer_sm)


    
    distance, path = fastdtw(s_real, s_delay)




    for val in path:
       print(str(singer_sm[val[0]]) + " " + str(singer_delayed[val[1]]))





if __name__ == "__main__":
    main()














