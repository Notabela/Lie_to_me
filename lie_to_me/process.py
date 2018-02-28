import os
import subprocess
from flask import abort
import re
import base64
from flask_socketio import emit
from lie_to_me import basedir, FFMPEG_PATH, app, socketio

frames_dir = os.path.join(basedir, 'static', 'data', 'tmp')
base64_frames = {}

def convert_to_frames(filepath):
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)

    output = os.path.join(frames_dir, "thumb%09d.jpg") # output filename

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
    convert_to_frames(filepath) # convert the video to images
    ordered_files = sorted(os.listdir(frames_dir), key=lambda x: (int(re.sub(r'\D','',x)),x))

    # Convert all frames to base64 images and begin calling
    for index, frame in enumerate(ordered_files):
        with open(os.path.join(frames_dir, frame), 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read())
            base64_frames[index] = encoded_string

    cleanup()

    # Frames are ready - start sending them to for pooling
    # Let's emit a message indicating that we're about to start sending files
    with app.test_request_context('/'):
        socketio.emit('frames_ready', {'data': 'Frames Ready'})


def cleanup():
    # CleanUp Temporary files
    subprocess.call(['rm', '-rf', 'uploads/*'])
    subprocess.call(['rm', '-rf', os.path.join(basedir, 'static', 'data', 'tmp', '*')])
