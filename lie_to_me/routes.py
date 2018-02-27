import os
import subprocess
import threading
from flask import render_template, request, jsonify, abort
from lie_to_me import app, video, basedir, socketio, FFMPEG_PATH


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'file' in request.files:
        filename = video.save(request.files['file'])

        threading.Thread(target=process_video, args=[os.path.join('uploads', filename)]).start()

        return jsonify({'success': True}), 200, {'ContentType': 'application/json'}

    elif request.method == 'GET':
        print(basedir)
        return render_template('home.html')


def convert_to_frames(filepath):
    output = os.path.join(basedir, 'static', 'data', 'tmp', "thumb%09d.jpg") # output filename

    try:
        command = [ FFMPEG_PATH, '-i', filepath, output, '-hide_banner' ]
        subprocess.call(command)  # break video to its frames
        # subprocess.call(['rm', '-fr', 'attachments'])
    except Exception as e:
        print(e)
        return abort(404)


def process_video(filepath):
    """
        Processes Video Submitted by User
    """
    convert_to_frames(filepath)


def cleanup(filepath):
    # CleanUp Temporary files
    subprocess.call(['rm', '-rf', 'uploads/*'])
    subprocess.call(['rm', '-rf', os.path.join(basedir, 'static', 'data', 'tmp', '*')])
        
