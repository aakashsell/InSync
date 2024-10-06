import pyaudio
import aubio
import numpy as np
import time

# Constants for audio stream
BUFFER_SIZE = 1024  # Standard Buffer Size
SAMPLE_RATE = 44100  # Common sample rate for audio

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open the input stream from the Scarlett 2i2 device
# Need to find exact path still
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=BUFFER_SIZE)

# Initialize aubio pitch detection and onset detection
onset_detector = aubio.onset("default", BUFFER_SIZE, BUFFER_SIZE // 2, SAMPLE_RATE)
pitch_detector = aubio.pitch("default", BUFFER_SIZE, BUFFER_SIZE // 2, SAMPLE_RATE)
pitch_detector.set_unit("Hz")
pitch_detector.set_silence(-40)  # Adjust this to control pitch detection sensitivity

def process_audio():
    # Keep track of previous note information
    current_note = None
    note_start_time = None

    while True:
        # Read audio data from stream
        audio_data = np.frombuffer(stream.read(BUFFER_SIZE), dtype=np.float32)
        
        # Detect pitch
        pitch = pitch_detector(audio_data)[0]

        # Detect note onset
        if onset_detector(audio_data):
            note_start_time = time.time()
            # debug print(f"Note started: {pitch} Hz at {note_start_time}")
            current_note = pitch

        # Detect note end and duration
        if current_note is not None and not onset_detector(audio_data):
            note_end_time = time.time()
            note_duration = note_end_time - note_start_time
            # debug print(f"Note ended: {current_note} Hz, Duration: {note_duration} seconds")
            current_note = None

# Run the audio processing
if __name__ == "__main__":
    try:
        print("Starting audio processing...")
        process_audio()
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        # Close stream and PyAudio when finished
        stream.stop_stream()
        stream.close()
        p.terminate()
