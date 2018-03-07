from flask import Flask
from flask_jsglue import JSGlue
from flask_socketio import SocketIO
from flask_uploads import UploadSet, configure_uploads, AllExcept, SCRIPTS, EXECUTABLES
import os

# Base directory of webapp - should return ...somefolder/Lie_to_me
basedir = os.path.abspath(os.path.dirname(__file__))

# Path to FFMPEG/FFPROBE - set this to FFMPEG PATH in Windows/Mac
FFMPEG_PATH  = '/usr/local/bin/ffmpeg' 
FFPROBE_PATH = '/usr/local/bin/ffprobe'

jsglue = JSGlue()
video = UploadSet('videos', AllExcept(SCRIPTS + EXECUTABLES))

app = Flask(__name__)

app.config['UPLOADED_VIDEOS_DEST'] = 'uploads'
app.config['SECRET_KEY'] = "VgGbw86h5A37B0Q6EA4t"

configure_uploads(app, video)
jsglue.init_app(app)
socketio = SocketIO(app)

import lie_to_me.routes
import lie_to_me.websockets