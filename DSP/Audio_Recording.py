# import sys
# from os.path import join
# from queue import Queue
# from threading import Thread

# from sounddevice import InputStream
# from soundfile import SoundFile

# import numpy  # Make sure NumPy is loaded before it is used in the callback

# assert numpy   # avoid "imported but unused" message (W0611)

# def find_device(name:str):
#     """
#     Searches for a Scarlett Audio Interface and returns its device index. Returns
#     default audio device of the system (typically built-in microphone) if none found.
#     The device index is used by pyaudio to select I/O

#     Args:
#         name (str): Name of audio device to be found. Returns first index if
#         multiple found.

#     Returns:
#         int: Index used to access the audio device with pyaudio. Returns -1 if
#         not found.
#     """
#     p = pyaudio.PyAudio()
#     # Iterate through all available devices
#     for i in range(p.get_device_count()):
#         device_info = p.get_device_info_by_index(i)
#         device_name = device_info.get('name')

#         # Check if the device name contains name provided
#         if name in device_name:
#             print("Found Device: ", device_name)
#             p.terminate()
#             return i
#     p.terminate()
#     return -1

# def file_writing_thread(*, q, **soundfile_args):
#     """Write data from queue to file until *None* is received."""
#     # NB: If you want fine-grained control about the buffering of the file, you
#     #     can use Python's open() function (with the "buffering" argument) and
#     #     pass the resulting file object to sf.SoundFile().
#     with SoundFile(**soundfile_args) as f:
#         while True:
#             data = q.get()
#             if data is None:
#                 break
#             f.write(data)

# def record_device(device_id:int, channels:int, piece:str):
#     def audio_callback(data, frames, time, status):
#         # Called for each audio block per thread
#         if status:
#             print(status, file=sys.stderr)
#         audio_q.put(data.copy())

#     file_name = join(rec_dir, f"rec_dev{piece}.wav")

#     stream = InputStream(
#         samplerate=SAMPLE_RATE, 
#         device=device_id, 
#         channels=channels, 
#         callback=audio_callback
#     )
#     stream.start()
#     print(f"started stream {stream} ...")

#     audio_q = Queue()
#     print(f"generated queue {audio_q} ...")

#     thread = Thread(
#         target=file_writing_thread,
#         kwargs=dict(
#             file=file_name,
#             mode="w",
#             samplerate=int(stream.samplerate),
#             channels=stream.channels,
#             q=audio_q,
#         ),
#     )
#     thread.start()
#     if VERBOSE_MODE:
#         print(f"started thread {thread} ...")
#         print(f'recording file "{file_name}" ...')
#         print("#" * 40)