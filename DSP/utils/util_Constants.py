# Constants for audio stream
BUFFER_SIZE = 256  # Standard Buffer Size
SAMPLE_RATE = 44100  # Common sample rate for audio
PITCH_TOLERANCE = 0.8 # Required confidence of pitch value
DEFAULT_BPM = 120 # Number of quarter-notes per minute
AUDIO_FORMAT = pyaudio.paFloat32 # Float format of audio data
MAX_MIDI = 108 # Highest note on a piano C8