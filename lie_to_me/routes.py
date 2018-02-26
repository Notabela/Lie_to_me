from lie_to_me import app, video
import os
from flask import render_template, request, jsonify


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'file' in request.files:
        filename = video.save(request.files['file'])
        return jsonify({'success': True}), 200, {'ContentType': 'application/json'}
    elif request.method == 'GET':
        return render_template('home.html')