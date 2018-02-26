from flask import Flask
from flask_jsglue import JSGlue
from flask_uploads import UploadSet, configure_uploads, ALL
import os

#UPLOAD_FOLDER = os.path.abspath('uploads')
#ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

jsglue = JSGlue()

app = Flask(__name__)
video = UploadSet('videos', ALL)
app.config['UPLOADED_VIDEOS_DEST'] = 'uploads'
configure_uploads(app, video)

jsglue.init_app(app)
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = "VgGbw86h5A37B0Q6EA4t"

import lie_to_me.routes