import os
import subprocess
import threading
from flask import render_template, request, jsonify, abort
from lie_to_me import app, video, basedir, FFMPEG_PATH


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

    # Frame conversion complete
    # Frames sit at os.path.join(basedir, 'static', 'data', 'tmp') and will be named
    # accordingly -> 001, 002, 003 etc.
    # for each file send five files and wait
    # when you hear back from the front end, send another five

    # We night need a local db with the following parameters
    # Frame number
    # base64 value
    # Time stamp
    # emotion data
    # eye_blink data


def cleanup(filepath):
    # CleanUp Temporary files
    subprocess.call(['rm', '-rf', 'uploads/*'])
    subprocess.call(['rm', '-rf', os.path.join(basedir, 'static', 'data', 'tmp', '*')])
        

# dev docs, when upload is complete, affectiva will be ready and connected
# python breaks file into its frame
# for each frame in the frames created
# give the frame an id
# convert the frame to a base64 image
# insert into a json of the frame and the base 64
# emit 5 frames to affectiva and await response for 5 frames -> Then send 5 more
