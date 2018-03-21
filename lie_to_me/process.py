import os
import glob
import subprocess
from flask import abort
from math import cos, log10, pi
from numpy import abs
import shelve
import re
import base64
from flask import abort
from flask_socketio import emit
from lie_to_me import basedir, FFMPEG_PATH, FFPROBE_PATH, app, socketio
from lie_to_me.modules import thinkdsp, audio

frames_dir = os.path.join(basedir, 'static', 'data', 'tmp_video')
audio_dir = os.path.join(basedir, 'static', 'data', 'tmp_audio')
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


def convert_audio(filepath):
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    output = os.path.join(audio_dir, "%03d.wav")

    try:
        ffmpeg_command = [FFMPEG_PATH, '-i', filepath, '-ar', '11000', '-ac', '2',
                          '-f', 'segment', '-segment_time', '-2', output]
        subprocess.call(ffmpeg_command)  # convert video into wave file

        files = [(audio_dir + '/' + f) for f in os.listdir(audio_dir)]
        return files

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

    cleanup_video()

    # Frames are ready - start sending them to for pooling
    # Let's emit a message indicating that we're about to start sending files
    socketio.emit('canvas_width_height', {'width': width, 'height': height})


def process_audio(filepath):
    """ Process Audio component of Video
    """
    json_path = os.path.join(basedir, 'static', 'data', 'tmp_json')
    results = []
    output = convert_audio(filepath)

    for files in output:
        frames, framelength = audio.split(files)
        filteredframes = audio.applyhamming(frames)
        energy = audio.energy(filteredframes)
        fourier = audio.fourier(filteredframes)
        frames = audio.inverse_fourier(fourier)
        pitchamp, pitchperiod = audio.sampling(frames)

        # Implemented Features, read audio.py for return values
        data1 = audio.meanenergy(energy)
        data2 = audio.maxpitchamp(pitchamp)
        data3 = audio.vowelduration(pitchamp, data2)
        data4 = audio.fundamentalf(pitchperiod, framelength)

        results.append((data1, data2, data3, data4))

    with shelve.open(os.path.join(json_path, 'audio_data.shlf')) as shelf:
        shelf['audio_data'] = results

    cleanup_audio()


def detect_blinks(eye_closure_list):
    """
        Returns the frames where blinks occured
    """
    eye_cl_thresh = 70          # eye closure >= 70 to be considered closed
    eye_cl_consec_frames = 4    # 4 or more consecutive frames to be considered a blink
    counter = 0

    # Array of frames where blink occured
    blink_frames = []

    for frame_number, eye_thresh in enumerate(eye_closure_list):
        if eye_thresh is None:
            continue
        elif eye_thresh > eye_cl_thresh:
            counter += 1
        else:
            if counter >= eye_cl_consec_frames:
                blink_frames.append(frame_number)
            counter = 0

    return blink_frames


def microexpression_analyzer(emotions, fps):
    """Micro expressions happen in 1/25th of a second or 15 frames

        Microexpression_analyzer:
        Function parameters:
          **emotions: A dictionary of emotions and their coresponding
          number value from 1 to 100 and the index is
          the current frame e.g emotions[0]['anger']
        Return:
          The function returns a list of timestamps where a
          possible micro expression was detechted
    """
    current_max = 0
    previous_max = 0
    microexpression_loop_counter = 0
    flag = 0
    previous_emotion = ''
    emotion_at_start = ''
    list_of_emotions = ['anger', 'contempt', 'disgust', 'fear', 'happiness', 'joy', 'sadness', 'surprise']
    timestamps = []

    for i in range(len(emotions)):
        # Store current max of emotions
        if not emotions:
            continue

        current_max = max(emotions[i]['anger'],
                          emotions[i]['contempt'],
                          emotions[i]['disgust'],
                          emotions[i]['happiness'],
                          emotions[i]['joy'],
                          emotions[i]['sadness'],
                          emotions[i]['surprise'])

        # Store the current emotion
        for key in emotions[i].keys():
            if current_max == emotions[i][key]:
                current_emotion = key

        if i == 0:
            previous_max = current_max
            previous_emotion = current_emotion
            continue

        # If previous_emotion is not equal to current_emotion then reset the counter and emotion_at_start
        if previous_emotion != current_emotion:
            if microexpression_loop_counter != 15:
                microexpression_loop_counter = 0
                microexpression_loop_counter += 1
                emotion_at_start = previous_emotion

        # Checking to see if the expression stayed the same, if so we increment a
        elif previous_emotion == current_emotion:
            microexpression_loop_counter += 1
        # If the micro expression changed back to the original expression it came from then
        # We have a possible lie and the timestamp is recorded.
        if emotion_at_start == current_emotion and microexpression_loop_counter == 15:
            seconds = i / fps
            minutes = seconds / 60
            if minutes < 1:
                minutes = 0
            timestamps.append('{}:{}'.format(minutes, seconds))
            microexpression_loop_counter = 0
            emotion_at_start = ''
            flag = 0
            continue
        # Record current max and previous max for next the analysis of the next ones
        previous_max = current_max
        previous_emotion = current_emotion

    return timestamps


def cleanup_video():
    """ Clean up temporary frames and uploaded file
    """
    for fl in glob.glob(os.path.join(basedir, 'static', 'data', 'tmp_video', '*')):
        os.remove(fl)

    for fl in glob.glob(os.path.join('uploads', '*')):
        os.remove(fl)


def cleanup_audio():
    """ Clean up temporary audio files
    """
    for fl in glob.glob(os.path.join(basedir, 'static', 'data', 'tmp_audio', '*')):
        os.remove(fl)


def cleanup_data():
    """ Clean up temporary stored data
    """
    for fl in glob.glob(os.path.join(basedir, 'static', 'data', 'tmp_json', '*')):
        os.remove(fl)