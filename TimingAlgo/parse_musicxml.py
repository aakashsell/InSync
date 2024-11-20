import xml.etree.ElementTree as ET

def insert_sorted(l1, l2):
    i = 0
    j = 0
    final = []
    last_time = float('-inf')  # Track the last appended end time (start + duration)
    
    # Compare and merge the two lists
    while i < len(l1) and j < len(l2):
        time1 = l1[i][1]
        time2 = l2[j][1]
        end1 = time1 + l1[i][2]
        end2 = time2 + l2[j][2]
        
        if time1 < time2:
            final.append(l1[i])
            last_time = end1
            i += 1
        else:
            final.append(l2[j])
            last_time = end2
            j += 1

    while i < len(l1):
        time1 = l1[i][1]
        end1 = time1 + l1[i][2]
        final.append(l1[i])
        last_time = end1
        i += 1
    
    while j < len(l2):
        time2 = l2[j][1]
        end2 = time2 + l2[j][2]
        final.append(l2[j])
        last_time = end2
        j += 1

    return final




def parse_musicxml_file(file_path, tempo):
    tree = ET.parse(file_path)
    root = tree.getroot()

    data = {}  # Dictionary to hold parts data
    divisions = 1  # Default divisions value for measures
    tempo = tempo

    metronome_tempo = root.find(".//metronome/per-minute")
    sound_tempo = root.find(".//sound")

    if metronome_tempo is not None:
        tempo = int(metronome_tempo.text)
    elif sound_tempo is not None and 'tempo' in sound_tempo.attrib:
        tempo = int(sound_tempo.attrib['tempo'])


    # Loop through each part
    for part in root.findall('part'):
        part_id = part.attrib.get('id', 'Unknown')
        data[part_id] = []  # Initialize list for this part's notes
        onset_time1 = 0  # Reset onset time for each part
        onset_time2 = 0

        tmp1 = []
        tmp2 = []

        # Process measures in the part
        for measure in part.findall('measure'):
            # Check for divisions in measure attributes
            attributes = measure.find('attributes')
            if attributes is not None:
                divisions_element = attributes.find('divisions')
                if divisions_element is not None:
                    divisions = int(divisions_element.text)

            direction = measure.find('direction')
            if direction is not None:
                tempo_element = direction.find('tempo')
                if tempo_element is not None:
                    tempo = int(tempo_element.text)

            # Process notes in the measure
            for note in measure.findall('note'):
                duration_element = note.find('duration')
                duration = int(duration_element.text) if duration_element is not None else 0
                duration_in_beats = duration / divisions
                duration_in_seconds = duration_in_beats * float(60 / tempo)

                pitch_element = note.find('pitch')
                rest_element = note.find('rest')
                chord = note.find('chord')
                staff = note.find('staff')


                #Process voice
                if part_id == 'P1':
                    if pitch_element is not None:  # Regular note
                        step = pitch_element.find('step').text
                        octave = pitch_element.find('octave').text
                        pitch = f"{step}{octave}"
                        data[part_id].append((pitch, round(onset_time1, 3), duration_in_seconds))
                    elif rest_element is not None:  # Explicit rest
                        data[part_id].append(("rest", round(onset_time1, 3), duration_in_seconds))
                    
                    # Increment Onset Time
                    onset_time1 += duration_in_seconds

                
                # Process Piano
                # First Staff
                if part_id == 'P2':
                    if chord is None and staff is not None and staff.text == '1':
                        if pitch_element is not None:  # Regular note
                            step = pitch_element.find('step').text
                            octave = pitch_element.find('octave').text
                            pitch = f"{step}{octave}"
                            tmp1.append((pitch, round(onset_time1, 3), duration_in_seconds))
                        elif rest_element is not None:  # Explicit rest
                            tmp1.append(("rest", round(onset_time1, 3), duration_in_seconds))
                        
                        # Increment Onset Time
                        onset_time1 += duration_in_seconds

                            
                    # Second Staff
                    elif chord is None:
                        if pitch_element is not None and staff is not None and staff.text == '2':  # Regular note
                            step = pitch_element.find('step').text
                            octave = pitch_element.find('octave').text
                            pitch = f"{step}{octave}"
                            tmp2.append((pitch, round(onset_time2, 3), duration_in_seconds))
                        elif rest_element is not None:  # Explicit rest
                            tmp2.append(("rest", round(onset_time2, 3), duration_in_seconds))
                        # Increment Onset Time
                        onset_time2 += duration_in_seconds

        data[part_id].extend(tmp1)


                    




    return data, tempo