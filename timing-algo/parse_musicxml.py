import xml.etree.ElementTree as ET
import random
import zipfile
import os


def parse_musicxml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    parts = {}
    time_signature = None  # Initialize time_signature variable

    # Default tempo in beats per minute (quarter notes per minute)
    default_tempo = 120  # Default tempo if not specified
    quarter_note_duration = 60 / default_tempo  # Duration of a quarter note in seconds at default tempo

    for part in root.findall(".//part"):
        part_id = part.get("id")
        notes = []
        onset_time = 0  # Running total to calculate the relative onset time
        divisions_element = root.find(".//attributes/divisions")
        divisions = float(divisions_element.text) if divisions_element is not None else 1

        # Get time signature
        time_signature_element = root.find(".//attributes/time")
        if time_signature_element is not None:
            beats = time_signature_element.find("beats")
            beat_type = time_signature_element.find("beat-type")
            if beats is not None and beat_type is not None:
                time_signature = f"{beats.text}/{beat_type.text}"

        tempo = default_tempo  # Initialize with default tempo

        for measure in part:
            chord_notes = []  # Store notes of a chord temporarily

            # Check for tempo changes in the measure
            for direction in measure.findall("direction"):
                sound = direction.find("sound")
                if sound is not None and "tempo" in sound.attrib:
                    tempo = float(sound.get("tempo"))
                    quarter_note_duration = 60 / tempo  # Update quarter note duration

            for note in measure:
                pitch = None
                duration = 0

                # Check for rests or notes with missing duration
                if note.tag == "note":
                    is_chord = note.find("chord") is not None

                    # Get duration if this is not part of a chord or first note of a chord
                    duration_element = note.find("duration")
                    if duration_element is not None and not is_chord:
                        # Convert MusicXML duration to seconds based on divisions and quarter note duration
                        duration = (int(duration_element.text) / divisions) * quarter_note_duration

                    # Separate assignment for pitch
                    pitch_tag = note.find("pitch")
                    if pitch_tag is not None:
                        pitch = f"{pitch_tag.find('step').text}{pitch_tag.find('octave').text}"

                    # Append the note or chord data with the onset time
                    chord_notes.append((pitch, onset_time, duration))

                    # If not a chord note, commit the chord notes and increment onset
                    if not is_chord:
                        notes.extend(chord_notes)
                        chord_notes = []
                        onset_time += duration  # Increment onset by the total duration of the chord or note

        parts[part_id] = notes

    return parts, time_signature  # Return both parts and time_signature


def create_delayed(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    parts = {}

    # Default tempo in beats per minute (quarter notes per minute)
    default_tempo = 120  # Default tempo if not specified
    quarter_note_duration = 60 / default_tempo  # Duration of a quarter note in seconds at default tempo

    for part in root.findall(".//part"):
        part_id = part.get("id")
        notes = []
        onset_time = 0  # Running total to calculate the relative onset time
        divisions_element = root.find(".//attributes/divisions")
        divisions = float(divisions_element.text) if divisions_element is not None else 1

        tempo = default_tempo  # Initialize with default tempo

        for measure in part:
            chord_notes = []  # Store notes of a chord temporarily

            # Check for tempo changes in the measure
            for direction in measure.findall("direction"):
                sound = direction.find("sound")
                if sound is not None and "tempo" in sound.attrib:
                    tempo = float(sound.get("tempo"))
                    quarter_note_duration = 60 / tempo  # Update quarter note duration

            for note in measure:
                pitch = None
                duration = 0

                # Check for rests or notes with missing duration
                if note.tag == "note":
                    is_chord = note.find("chord") is not None

                    # Get duration if this is not part of a chord or first note of a chord
                    duration_element = note.find("duration")
                    if duration_element is not None and not is_chord:
                        # Convert MusicXML duration to seconds based on divisions and quarter note duration
                        duration = (int(duration_element.text) / divisions) * quarter_note_duration

                        # Add a small random variation to the duration (e.g., between -0.05 and 0.05 seconds)
                        duration += random.uniform(-0.05, 0.05)

                    # Separate assignment for pitch
                    pitch_tag = note.find("pitch")
                    if pitch_tag is not None:
                        pitch = f"{pitch_tag.find('step').text}{pitch_tag.find('octave').text}"

                    # Add a small random delay to the onset time (e.g., between -0.02 and 0.02 seconds)
                    onset_delay = random.uniform(0, 0.02)
                    chord_notes.append((pitch, onset_time + onset_delay, duration))

                    # If not a chord note, commit the chord notes and increment onset
                    if not is_chord:
                        notes.extend(chord_notes)
                        chord_notes = []
                        onset_time += duration  # Increment onset by the total duration of the chord or note

        parts[part_id] = notes
    return parts


def create_container_file(container_file="META-INF/container.xml"):
    # Create the META-INF directory and the container.xml file
    os.makedirs(os.path.dirname(container_file), exist_ok=True)
    
    container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
        <rootfiles>
            <rootfile full-path="output_music.xml" media-type="application/vnd.recordare.musicxml" />
        </rootfiles>
    </container>
    '''
    
    with open(container_file, "w") as f:
        f.write(container_xml.strip())


def create_musicxml_from_parts(parts, time_signature, output_xml_file="output_music.xml", output_mxl_file="output_music.mxl"):
    # Create the MusicXML structure
    score_partwise = ET.Element("score-partwise", version="3.1")
    part_list = ET.SubElement(score_partwise, "part-list")

    for part_id in parts.keys():
        score_part = ET.SubElement(part_list, "score-part", id=part_id)
        ET.SubElement(score_part, "part-name").text = f"Part {part_id}"

    # Create the attributes element for time signature
    attributes = ET.SubElement(score_partwise, "attributes")
    if time_signature:
        time_element = ET.SubElement(attributes, "time")
        beats = ET.SubElement(time_element, "beats")
        beat_type = ET.SubElement(time_element, "beat-type")
        beats.text, beat_type.text = time_signature.split('/')

    for part_id, notes in parts.items():
        part = ET.SubElement(score_partwise, "part", id=part_id)
        
        measure_number = 1
        onset_time = 0  
        measure = ET.SubElement(part, "measure", number=str(measure_number))

        for pitch, note_onset, duration in notes:
            # If the note's onset time indicates it should go into a new measure, create a new measure
            while note_onset > onset_time + 4:  # Assuming a threshold of 4 seconds for new measures
                measure_number += 1
                measure = ET.SubElement(part, "measure", number=str(measure_number))
                onset_time += 4  # Adjust based on your desired measure length
            
            note = ET.SubElement(measure, "note")
            duration_element = ET.SubElement(note, "duration")
            duration_element.text = str(int(duration * 4))  # Convert to divisions based on quarter notes
            
            # Determine the type of note based on duration
            if duration == 1:
                type_element = ET.SubElement(note, "type")
                type_element.text = "quarter"
            elif duration == 0.5:
                type_element = ET.SubElement(note, "type")
                type_element.text = "eighth"
            elif duration == 2:
                type_element = ET.SubElement(note, "type")
                type_element.text = "half"
            else:
                type_element = ET.SubElement(note, "type")
                type_element.text = "whole"  # Add more types as needed

            if pitch is None:
                ET.SubElement(note, "rest")
            else:
                pitch_element = ET.SubElement(note, "pitch")
                step = ET.SubElement(pitch_element, "step")
                octave = ET.SubElement(pitch_element, "octave")
                step.text, octave.text = pitch[:-1], pitch[-1]

            onset_time += duration  # Update the running total of onset time

    # Write the MusicXML to a .xml file
    tree = ET.ElementTree(score_partwise)
    tree.write(output_xml_file, encoding="utf-8", xml_declaration=True)

    # Create the META-INF container
    create_container_file()

    # Compress to .mxl
    with zipfile.ZipFile(output_mxl_file, 'w', zipfile.ZIP_DEFLATED) as mz:
        mz.write(output_xml_file, arcname=os.path.basename(output_xml_file))
        mz.write("META-INF/container.xml", arcname="META-INF/container.xml")
        
    # Clean up
    os.remove(output_xml_file)
    os.remove("META-INF/container.xml")


