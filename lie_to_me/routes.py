""" Routes of Flask Web Application """
import os
import threading
import shelve
from pathlib import Path
from flask import render_template, request, jsonify
from lie_to_me import app, video, basedir
from lie_to_me.process import process_video, process_audio


@app.route('/', methods=['GET', 'POST'])
def upload():
    """ Home Page Route
        Upload and Analyze Video
    :return: home.html template
    """
    if request.method == 'POST' and 'file' in request.files:
        # Video has been uploaded
        filename = video.save(request.files['file'])

        # Process video on a new thread
        threading.Thread(target=process_video, args=[os.path.join('uploads', filename)]).start()
        threading.Thread(target=process_audio, args=[os.path.join('uploads', filename)]).start()

        return jsonify({'success': True}), 200, {'ContentType': 'application/json'}

    elif request.method == 'GET':
        return render_template('home.html')


@app.route('/analysis', methods=['GET'])
def analysis():
    """ Analysis Route
        View Final Analysis of Uploaded Video
    :return:
    """
    json_path = os.path.join(basedir, 'static', 'data', 'tmp_json')

    audio_file = Path(os.path.join(json_path, 'audio_data.shlf.db'))
    video_file = Path(os.path.join(json_path, 'facial_data.shlf.db'))

    # Files exists
    if audio_file.is_file() and video_file.is_file():
        print('')
        with shelve.open(os.path.join(json_path, 'facial_data.shlf')) as shelf:
            emotion_data = shelf['emotion_data']
            microexpression_data = shelf['micro_expression_data']
            blink_data = shelf['blink_data']

        with shelve.open(os.path.join(json_path, 'audio_data.shlf')) as shelf:
            audio_data = shelf['audio_data']

    else:
        emotion_data = None
        microexpression_data = None
        blink_data = None
        audio_data = None

    return render_template('analysis.html', audio_data=audio_data, blink_data=blink_data,
                           microexpression_data=microexpression_data, emotion_data=emotion_data)
