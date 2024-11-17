# Aakash Sell (asell)


import time


from parse_musicxml import *
from file_conversions import *
from processing import *


from music21 import converter, note



def parse_audio(file_path):
    file = open(file_path, mode='r')
    lines = file.readlines()
    file.close

    data = []

    start = float(lines[0].strip())
    end = float(lines[-1].strip())

    lines = lines[1:len(lines)-1]


    for i in range(len(lines)):
        line = lines[i]
        line_data = line.split()

        if(len(line_data) == 1):
            if i > 0 and i < len(lines) - 1:
                prev = lines[i-1].split()
                next = lines[i+1].split()
                data.append((0, float(prev[2]), float(next[1]) - float(prev[2])))

        if(len(line_data) == 3):

            pitch = int(float(line_data[0]))
            onset = float(line_data[1])
            duration = float(line_data[2]) - float(line_data[1])

            tmp_data = (pitch, onset, duration)
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
            delays.append((s_path[val[0]], diff))
    


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
file_path = "./score.xml"

voice_data = "./voice.out"

piano_data = "./piano.out"



def timing_algo(sheet_music_path, audio_data_path):

    parts_data = parse_musicxml_file(sheet_music_path)

    singer_sm = parts_data.get('P1', None)
    singer_sm = [(note.Note(val[0]).pitch.midi if val[0] != 'rest' else 0, val[1], val[2]) for val in singer_sm]




    piano_sm = parts_data.get('P2', None)
    piano_sm = [(note.Note(val[0]).pitch.midi if val[0] != 'rest' else 0, val[1], val[2]) for val in piano_sm]




    same = find_simultaneous_notes(singer_sm, piano_sm)

    



    singer_audio = parse_audio(audio_data_path[0])

    piano_audio = parse_audio(audio_data_path[1])



    singer_distance, singer_path = process(singer_sm, singer_audio)


    piano_distance, piano_path = process(piano_sm, piano_audio)

    delays = find_out_of_sync(same, singer_path, piano_path, singer_audio, piano_audio)

    
    
    for line in delays:
        print(line)
        pass




 


   # piano_distance, piano_path = process(piano_sm, piano_delay)

    

    piano_audio = None

   # out = find_out_of_sync(same, singer_path, piano_path, singer_delay, piano_delay)

    #print(out)

        


    






    





if __name__ == "__main__":
    timing_algo(file_path, [voice_data, piano_data])














