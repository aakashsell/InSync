from music_manager import MusicManager
import socket
import pickle
import subprocess
import os
import struct
class Info:
    def __init__(self,is_sync, beat):
        self.is_sync = is_sync
        self.beat = beat

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65435  # Port to listen on (non-privileged ports are > 1023)

def create_and_handle_session(sheet_path, music_xml_path,image_path, voice_path, piano_path, bpm):
    
    manager = MusicManager(sheet_path,music_xml_path,image_path)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        process = subprocess.Popen(["python3", "../TimingAlgo/timing_algo.py", os.getcwd() + "/"+ music_xml_path,voice_path,piano_path,str(bpm)] )
        print("Starting Socket")
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        #s.sendall
        count = 0
        severity = 0
        while True:
            data = conn.recv(4)
            print("buf len", len(data))
            if not data:
                break
            received_int = struct.unpack('!i', data)[0] 
            
            #restored_obj = pickle.loads(data)
            if(count%3 == 0):
                severity = received_int
            if(count%3 == 1):
                manager.set_sync_status(received_int,False,severity)
            else:
                manager.set_sync_status(received_int,True,severity)
            count += 1
            conn.sendall(data)
        manager.done()
            
    
