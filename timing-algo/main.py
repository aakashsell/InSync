import time

tempo = 60 #bpm
second_per_beat = 60/tempo

start_time = time.time()

# Get sheet music data
sheet_music = ['d1/4', 'e1/4', 'e1/2', 'e1/4', 'e1/4', 'e1/4']

#transform sheet music into time series data.

sheet_music = ['d', 'e', 'e', 'e', 'e', 'e', 'e']


# Get Audio Data

audio_data1 = [(0, 'd'), (1, 'e'), (2, 'e'), (4, 'e'), (5, 'e'), (6, 'e')]
audio_data2 = [(0, 'd'), (2, 'e'), (2, 'e'), (4, 'e'), (5, 'e'), (6, 'e')]

# compare data

def compare(sheet, audio1, audio2):
    #check where the data is in the music
    



