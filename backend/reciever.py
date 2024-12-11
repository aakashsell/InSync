import multiprocessing
from flask import Flask, request, redirect, send_file, url_for, make_response,jsonify
from werkzeug.utils import secure_filename
import subprocess
import os
import xml.etree.ElementTree as ET
import cv2
import session
import shutil
import zipfile
import json
from datetime import datetime
app = Flask(__name__)
UPLOAD_FOLDER = './upload_folder'
RESULTS = './fresults'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','pdf'}
AUDIVERIES_COMMAND = '/Users/mathiasthomas/Documents/18500/audiveris/app/build/distributions/app-5.4-alpha/bin/Audiveris'

super_dict = dict()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/upload', methods=["POST", "OPTIONS"])
def upload():
    
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    saved_name = request.headers.get('name')
    print(request.files)
    if 'file' not in request.files:
        print(request.files)
        return redirect(request.url)
    file = request.files['file']
    if file and allowed_file(file.filename):
            filename = secure_filename(saved_name  + ".pdf")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            result = subprocess.run([AUDIVERIES_COMMAND, "-export", "-batch", "-option","org.audiveris.omr.sheet.ProcessingSwitches.indentations=false",
                                   "-option", "org.audiveris.omr.sheet.BookManager.useSeparateBookFolders=false",file_path])
            #subprocess.Popen().kill()
            return_code = result.returncode
            extract_to_directory = f"{UPLOAD_FOLDER}/{saved_name}"
            os.remove(file_path)
            os.mkdir(f"{UPLOAD_FOLDER}/{saved_name}")
            os.mkdir(f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}sheet")
            os.mkdir(f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}music")
            extract_to_directory = f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}music"
            extract_to_directory2 = f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}sheet"
            shutil.move(f"/Users/mathiasthomas/Library/AudiverisLtd/audiveris/data/{saved_name}/{saved_name}.mxl", f"{UPLOAD_FOLDER}/{saved_name}")
            shutil.move(f"/Users/mathiasthomas/Library/AudiverisLtd/audiveris/data/{saved_name}/{saved_name}.omr", f"{UPLOAD_FOLDER}/{saved_name}")
            with zipfile.ZipFile( f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}.mxl", 'r') as zip_ref:
                zip_ref.extractall(extract_to_directory)
            with zipfile.ZipFile( f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}.omr", 'r') as zip_ref:
                zip_ref.extractall(extract_to_directory2)
            os.remove( f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}.mxl")
            os.remove( f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}.omr")
            return _corsify_actual_response(jsonify(os.listdir(UPLOAD_FOLDER)))
    
    return "No"
def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response
@app.route('/startsong', methods=['POST', 'OPTIONS'])
def start_song():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    
    print("Recieved Start Song")
    song_name_dict = str(request.get_data())
    song_name_dict = song_name_dict[2:len(song_name_dict) - 1]
    print(song_name_dict)
    data = json.loads(song_name_dict)
    song_name = data['song']
    print(song_name)
    ap = subprocess.Popen(["python3", "../DSP/InSync_DSP.py", "-p", song_name])
    global super_dict
    super_dict[song_name] = ap
    print(song_name)
    '''
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], song_name)
    music_path = ""
    sheets = []
    images = []
    for dir_path in os.listdir(data_path):
         for dir_path2 in os.listdir(os.path.join(data_path,dir_path)):
              
              if(dir_path.endswith("sheet")):
                   if(os.path.isdir(os.path.join(data_path, dir_path,dir_path2))):
                        for dir_path3 in os.listdir(os.path.join(data_path,dir_path,dir_path2)):
                             print(dir_path3)
                             if(dir_path3.endswith(".png")):
                                  images.append(os.path.join(data_path, dir_path, dir_path2, dir_path3))
                             else:
                                  sheets.append(os.path.join(data_path, dir_path, dir_path2, dir_path3))
              else:
                   if(os.path.isfile(os.path.join(data_path, dir_path,dir_path2))):
                        music_path = os.path.join(data_path, dir_path,dir_path2)
    
    print(sheets)
    print(images)
    sheets.reverse()
    images.reverse()
    print( "path:" +music_path)          
    p = multiprocessing.Process(target=session.create_and_handle_session, args=(sheets,music_path,images))
    p.start()
    p.join()
    prefixed = [filename for filename in os.listdir('.') if filename.startswith("result")]
    curr = datetime.now()
    print(prefixed)
    os.mkdir(f"{RESULTS}/{song_name}{curr.strftime("%d%m_%Y_%H:%M:%S")}")
    for pre in prefixed:
        shutil.move(f"./{pre}",f"{RESULTS}/{song_name}{curr.strftime("%d%m_%Y_%H:%M:%S")}" )
    return _corsify_actual_response(jsonify(os.listdir(RESULTS)))
    '''
    '''
    files_to_zip = [
        'results0.png',
        'results1.png',
        'results2.png'
    ]
    zip_filename = 'files.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_zip:
            # Ensure the file exists before adding it
            if os.path.exists(file_path):
                zipf.write(file_path, os.path.basename(file_path))
    
    print("Done")
    return send_file(zip_filename,as_attachment=True, download_name='files.zip')
    '''
    return _corsify_actual_response(jsonify("Success"))

@app.route('/done_song', methods=['POST', 'OPTIONS'])
def done_song():
    
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    song_name_dict = str(request.get_data())
    song_name_dict = song_name_dict[2:len(song_name_dict) - 1]
    print(song_name_dict)
    data = json.loads(song_name_dict)
    song_name = data['song']
    print(song_name)
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], song_name)
    #Commenting out for now since just testing done
    '''
    global super_dict
    process = super_dict[song_name]
    process.kill()
    shutil.move(../DSP/modfied.out, ./)
    '''
    #TODO save a pre-done piano file

    piano_file =  os.getcwd() + "/piano.out"
    singer_file = os.getcwd() + "/modfied.out"
    music_path = ""
    sheets = []
    images = []
    for dir_path in os.listdir(data_path):
         for dir_path2 in os.listdir(os.path.join(data_path,dir_path)):
              
              if(dir_path.endswith("sheet")):
                   if(os.path.isdir(os.path.join(data_path, dir_path,dir_path2))):
                        for dir_path3 in os.listdir(os.path.join(data_path,dir_path,dir_path2)):
                             print(dir_path3)
                             if(dir_path3.endswith(".png")):
                                  images.append(os.path.join(data_path, dir_path, dir_path2, dir_path3))
                             else:
                                  sheets.append(os.path.join(data_path, dir_path, dir_path2, dir_path3))
              else:
                   if(os.path.isfile(os.path.join(data_path, dir_path,dir_path2))):
                        music_path = os.path.join(data_path, dir_path,dir_path2)
    
    print(sheets)
    print(images)
    sheets.reverse()
    images.reverse()
    print( "path:" +music_path)          
    p = multiprocessing.Process(target=session.create_and_handle_session, args=(sheets,music_path,images,singer_file,piano_file))
    p.start()
    p.join()
    prefixed = [filename for filename in os.listdir('.') if filename.startswith("result")]
    curr = datetime.now()
    print(prefixed)
    os.mkdir(f"{RESULTS}/{song_name}{curr.strftime("%d%m_%Y_%H:%M:%S")}")
    for pre in prefixed:
        shutil.move(f"./{pre}",f"{RESULTS}/{song_name}{curr.strftime("%d%m_%Y_%H:%M:%S")}" )
    return _corsify_actual_response(jsonify(os.listdir(RESULTS)))

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
@app.route('/get_all_songs', methods=['GET', 'OPTIONS'])
def get_all_songs():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
  
    return _corsify_actual_response(jsonify(os.listdir(UPLOAD_FOLDER)))
@app.route('/get_all_results', methods=['GET', 'OPTIONS'])
def get_all_results():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
  
    return _corsify_actual_response(jsonify(os.listdir(RESULTS)))
@app.route('/get_result', methods=['POST', 'OPTIONS'])
def get_result():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    song_name = str(request.get_data())
    song_name = song_name[2:len(song_name) - 1]
    files_to_zip = []
    for file in os.listdir(os.path.join(RESULTS, song_name)):
        files_to_zip.append(os.path.join(os.path.join(RESULTS, song_name), file))
    zip_filename = 'files.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_zip:
            # Ensure the file exists before adding it
            if os.path.exists(file_path):
                zipf.write(file_path, os.path.basename(file_path))
    return _corsify_actual_response(send_file(zip_filename,as_attachment=True, download_name='files.zip'))
'''
This function parses the position of the note elements from the XML and sorts them
It sorts first by y postion and groups elements with similar y positions into there own list(measure)
then by x position within each measure
'''
def parse_xml(path):
     file = ET.parse(path)
     root = file.getroot()
     page = root.find('page')
     system = page.find('system')
     heads = system.findall('head')
     template = cv2.imread('BINARY.png')

     for head in heads:
        bounds = head.find('bounds').text
        print(bounds)
        
     
    