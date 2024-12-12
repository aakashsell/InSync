import InSync_DSP

#   Record (Optional)
#   Generate data with multiple silence thresholds
onsets = ["hfc","complex","phase"]

for onset_type in onsets:
    for silence in range(-90,0,5):
        process_file(audio_source, silence_threshold=silence, onset=onset_type)