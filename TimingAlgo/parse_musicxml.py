import xml.etree.ElementTree as ET

def parse_musicxml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    data = {}  # Dictionary to hold parts data
    divisions = 1  # Default divisions value for measures

    # Loop through each part
    for part in root.findall('part'):
        part_id = part.attrib.get('id', 'Unknown')
        data[part_id] = []  # Initialize list for this part's notes
        onset_time = 0  # Reset onset time for each part

        # Process measures in the part
        for measure in part.findall('measure'):
            # Check for divisions in measure attributes
            attributes = measure.find('attributes')
            if attributes is not None:
                divisions_element = attributes.find('divisions')
                if divisions_element is not None:
                    divisions = int(divisions_element.text)

            # Process notes in the measure
            for note in measure.findall('note'):
                duration_element = note.find('duration')
                duration = int(duration_element.text) if duration_element is not None else 0
                duration_in_beats = duration / divisions

                pitch_element = note.find('pitch')
                rest_element = note.find('rest')

                if pitch_element is not None:  # Regular note
                    step = pitch_element.find('step').text
                    octave = pitch_element.find('octave').text
                    pitch = f"{step}{octave}"
                    data[part_id].append((pitch, round(onset_time, 3), duration_in_beats))
                elif rest_element is not None:  # Explicit rest
                    data[part_id].append(("rest", round(onset_time, 3), duration_in_beats))

                # Increment onset time
                onset_time += duration_in_beats

    return data