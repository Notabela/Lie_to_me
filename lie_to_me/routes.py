""" Routes of Flask Web Application """
import os
import threading
from flask import render_template, request, jsonify
from lie_to_me import app, video
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

    return render_template('analysis.html')
