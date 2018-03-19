import os
import glob
import subprocess
from flask import abort
import re
import base64
from flask_socketio import emit
from lie_to_me import basedir, FFMPEG_PATH, FFPROBE_PATH, app, socketio

frames_dir = os.path.join(basedir, 'static', 'data', 'tmp')
base64_frames = {}


def convert_to_frames(filepath):
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)

    output = os.path.join(frames_dir, "thumb%09d.jpg") # output filename

    try:
        ffprobe_command = [ FFPROBE_PATH, '-v', 'error', '-show_entries', 'stream=width,height', '-of', 'default=noprint_wrappers=1', filepath]
        ffmpeg_command = [ FFMPEG_PATH, '-i', filepath, output, '-hide_banner' ]

        proc = subprocess.Popen(ffprobe_command, stdout=subprocess.PIPE)
        output = proc.stdout.read().decode('utf-8')
        regex = re.compile(r"[a-z]+=([0-9]+)\n[a-z]+=([0-9]+)\n")
        width, height = regex.match(output).groups()

        subprocess.call(ffmpeg_command)  # break video to its frames

        return width, height
    except Exception as e:
        print(e)
        return abort(404)


def process_video(filepath):
    """
        Processes Video Submitted by User

    """
    width, height = convert_to_frames(filepath) # convert the video to images
    ordered_files = sorted(os.listdir(frames_dir), key=lambda x: (int(re.sub(r'\D','',x)),x))

    # Convert all frames to base64 images and begin calling
    for index, frame in enumerate(ordered_files):
        with open(os.path.join(frames_dir, frame), 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read())
            base64_frames[index] = encoded_string.decode('utf-8')

    #cleanup()

    # Frames are ready - start sending them to for pooling
    # Let's emit a message indicating that we're about to start sending files
    #with app.test_request_context('/'):
    socketio.emit('canvas_width_height', {'width': width, 'height': height})


def cleanup():
    # CleanUp Temporary files
    for fl in glob.glob(os.path.join(basedir, 'static', 'data', 'tmp', '*')):
        os.remove(fl)

    for fl in glob.glob(os.path.join('uploads', '*')):
        os.remove(fl)
