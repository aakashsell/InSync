import xml.etree.ElementTree as ET
import random
import zipfile
import os


import xml.etree.ElementTree as ET


def parse_musicxml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    parts = {}

    # Default tempo in beats per minute
    default_tempo = 120
    quarter_note_duration = 60 / default_tempo

    for part in root.findall(".//part"):
        part_id = part.get("id")
        
        # Initialize staff-specific data structures
        staves = {}  # Dictionary to store notes for each staff
        current_onsets = {}  # Track current onset for each staff
        chord_onsets = {}  # Track chord onset for each staff
        chord_durations = {}  # Track chord duration for each staff
        current_chord_notes = {}  # Track current chord notes for each staff
        
        divisions_element = root.find(".//attributes/divisions")
        divisions = float(divisions_element.text) if divisions_element is not None else 1

        tempo = default_tempo

        # Initialize data structures for each staff
        staves_element = root.find(".//attributes/staves")
        num_staves = int(staves_element.text) if staves_element is not None else 1
        
        for staff_num in range(1, num_staves + 1):
            staves[staff_num] = []
            current_onsets[staff_num] = 0
            chord_onsets[staff_num] = None
            chord_durations[staff_num] = None
            current_chord_notes[staff_num] = []

        for measure in part:
            # Check for tempo changes
            for direction in measure.findall("direction"):
                sound = direction.find("sound")
                if sound is not None and "tempo" in sound.attrib:
                    tempo = float(sound.get("tempo"))
                    quarter_note_duration = 60 / tempo

            for note in measure:
                if note.tag != "note":
                    continue

                # Get staff number (default to 1 if not specified)
                staff_elem = note.find("staff")
                staff_num = int(staff_elem.text) if staff_elem is not None else 1
                
                is_chord = note.find("chord") is not None
                duration_elem = note.find("duration")
                
                # Calculate note duration
                if duration_elem is not None:
                    duration = (int(duration_elem.text) / divisions) * quarter_note_duration

                # Get pitch information
                pitch_elem = note.find("pitch")
                if pitch_elem is not None:
                    step = pitch_elem.find("step").text
                    octave = pitch_elem.find("octave").text
                    alter_elem = pitch_elem.find("alter")
                    
                    # Handle accidentals
                    alter = ""
                    if alter_elem is not None:
                        alter_value = int(alter_elem.text)
                        if alter_value == 1:
                            alter = "#"
                        elif alter_value == -1:
                            alter = "b"
                    
                    pitch = f"{step}{alter}{octave}"

                    if is_chord:
                        # Add to current chord with the same onset time as first note
                        current_chord_notes[staff_num].append(
                            (pitch, chord_onsets[staff_num], chord_durations[staff_num])
                        )
                    else:
                        # If there were previous chord notes, add them
                        if current_chord_notes[staff_num]:
                            staves[staff_num].extend(current_chord_notes[staff_num])
                            current_chord_notes[staff_num] = []
                        
                        # Store onset and duration for potential chord notes
                        chord_onsets[staff_num] = current_onsets[staff_num]
                        chord_durations[staff_num] = duration
                        
                        # Add the current note
                        current_chord_notes[staff_num] = [
                            (pitch, current_onsets[staff_num], duration)
                        ]
                        
                        # Update onset time for next note/chord
                        current_onsets[staff_num] += duration

                # Handle rest notes
                elif note.find("rest") is not None and duration_elem is not None:
                    # If there were previous chord notes, add them
                    if current_chord_notes[staff_num]:
                        staves[staff_num].extend(current_chord_notes[staff_num])
                        current_chord_notes[staff_num] = []
                    
                    # Update onset time for this staff
                    current_onsets[staff_num] += (int(duration_elem.text) / divisions) * quarter_note_duration

            # Handle any remaining chord notes at the end of the measure
            for staff_num in current_chord_notes:
                if current_chord_notes[staff_num]:
                    staves[staff_num].extend(current_chord_notes[staff_num])
                    current_chord_notes[staff_num] = []

        # Combine all staff notes and sort by onset time
        all_notes = []
        for staff_notes in staves.values():
            all_notes.extend(staff_notes)
        all_notes.sort(key=lambda x: x[1])  # Sort by onset time
        
        parts[part_id] = all_notes

    return parts


def delayed_music(file_path, delay_range=(-0.2, 0.2)):
    tree = ET.parse(file_path)
    root = tree.getroot()
    parts = {}

    # Default tempo in beats per minute
    default_tempo = 120
    quarter_note_duration = 60 / default_tempo

    for part in root.findall(".//part"):
        part_id = part.get("id")
        
        # Initialize staff-specific data structures
        staves = {}  # Dictionary to store notes for each staff
        current_onsets = {}  # Track current onset for each staff
        chord_onsets = {}  # Track chord onset for each staff
        chord_durations = {}  # Track chord duration for each staff
        current_chord_notes = {}  # Track current chord notes for each staff
        
        divisions_element = root.find(".//attributes/divisions")
        divisions = float(divisions_element.text) if divisions_element is not None else 1

        tempo = default_tempo

        # Initialize data structures for each staff
        staves_element = root.find(".//attributes/staves")
        num_staves = int(staves_element.text) if staves_element is not None else 1
        
        for staff_num in range(1, num_staves + 1):
            staves[staff_num] = []
            current_onsets[staff_num] = 0
            chord_onsets[staff_num] = None
            chord_durations[staff_num] = None
            current_chord_notes[staff_num] = []

        for measure in part:
            # Check for tempo changes
            for direction in measure.findall("direction"):
                sound = direction.find("sound")
                if sound is not None and "tempo" in sound.attrib:
                    tempo = float(sound.get("tempo"))
                    quarter_note_duration = 60 / tempo

            for note in measure:
                if note.tag != "note":
                    continue

                # Get staff number (default to 1 if not specified)
                staff_elem = note.find("staff")
                staff_num = int(staff_elem.text) if staff_elem is not None else 1
                
                is_chord = note.find("chord") is not None
                duration_elem = note.find("duration")
                
                # Calculate note duration
                if duration_elem is not None:
                    duration = (int(duration_elem.text) / divisions) * quarter_note_duration

                # Get pitch information
                pitch_elem = note.find("pitch")
                if pitch_elem is not None:
                    step = pitch_elem.find("step").text
                    octave = pitch_elem.find("octave").text
                    alter_elem = pitch_elem.find("alter")
                    
                    # Handle accidentals
                    alter = ""
                    if alter_elem is not None:
                        alter_value = int(alter_elem.text)
                        if alter_value == 1:
                            alter = "#"
                        elif alter_value == -1:
                            alter = "b"
                    
                    pitch = f"{step}{alter}{octave}"

                    if is_chord:
                        # Add to current chord with the same onset time as first note
                        current_chord_notes[staff_num].append(
                            (pitch, chord_onsets[staff_num], chord_durations[staff_num])
                        )
                    else:
                        # If there were previous chord notes, add them
                        if current_chord_notes[staff_num]:
                            staves[staff_num].extend(current_chord_notes[staff_num])
                            current_chord_notes[staff_num] = []
                        
                        # Store onset and duration for potential chord notes
                        chord_onsets[staff_num] = current_onsets[staff_num]
                        chord_durations[staff_num] = duration
                        
                        # Add the current note
                        random_delay = random.uniform(*delay_range)
                        current_chord_notes[staff_num] = [
                            (pitch, current_onsets[staff_num] + random_delay, duration)
                        ]
                        
                        # Update onset time for next note/chord
                        current_onsets[staff_num] += duration

                # Handle rest notes
                elif note.find("rest") is not None and duration_elem is not None:
                    # If there were previous chord notes, add them
                    if current_chord_notes[staff_num]:
                        staves[staff_num].extend(current_chord_notes[staff_num])
                        current_chord_notes[staff_num] = []
                    
                    # Update onset time for this staff
                    current_onsets[staff_num] += (int(duration_elem.text) / divisions) * quarter_note_duration

            # Handle any remaining chord notes at the end of the measure
            for staff_num in current_chord_notes:
                if current_chord_notes[staff_num]:
                    staves[staff_num].extend(current_chord_notes[staff_num])
                    current_chord_notes[staff_num] = []

        # Combine all staff notes and sort by onset time
        all_notes = []
        for staff_notes in staves.values():
            all_notes.extend(staff_notes)
        all_notes.sort(key=lambda x: x[1])  # Sort by onset time
        
        parts[part_id] = all_notes

    return parts