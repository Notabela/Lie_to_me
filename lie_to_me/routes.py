""" Routes of Flask Web Application """
import os
import threading
from flask import render_template, request, jsonify
from lie_to_me import app, video
from lie_to_me.process import process_video


@app.route('/', methods=['GET', 'POST'])
def upload():
    """
        Homepage Route
        Provides the ability to upload video file for analysis
    """
    if request.method == 'POST' and 'file' in request.files:
        # Video has been uploaded
        filename = video.save(request.files['file'])

        # Process video on a new thread
        threading.Thread(target=process_video, args=[os.path.join('uploads', filename)]).start()

        return jsonify({'success': True}), 200, {'ContentType': 'application/json'}

    elif request.method == 'GET':
        return render_template('home.html')
