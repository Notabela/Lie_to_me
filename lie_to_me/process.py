import os
import subprocess
from flask import abort
import re
import base64
from flask_socketio import emit
from lie_to_me import basedir, FFMPEG_PATH
from lie_to_me.websockets import clients

frames_dir = os.path.join(basedir, 'static', 'data', 'tmp')
base64_frames = []
current_frame = 0

def convert_to_frames(filepath):
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
    ordered_files = sorted(os.listdir(frames_dir), key=lambda x: (int(re.sub('\D','',x)),x))

    # Convert all frames to base64 images and begin calling
    for index, frame in enumerate(ordered_files):
        with open(os.path.join(frames_dir, frame), 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read())
            base64_frames.append((index, encoded_string))


    # Frames are ready - start sending them to for pooling
    # Let's emit a message indicating that we're about to start sending files
    print(clients)
    emit('frames_ready', {'data': 'Frames Ready'}, room=clients[0])


def cleanup(filepath):
    # CleanUp Temporary files
    subprocess.call(['rm', '-rf', 'uploads/*'])
    subprocess.call(['rm', '-rf', os.path.join(basedir, 'static', 'data', 'tmp', '*')])
