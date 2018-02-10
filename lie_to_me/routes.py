from lie_to_me import app
from flask import render_template

@app.route('/emotion_demo', methods=['GET'])
def emotion_demo():
    """
        Demo of Affectiva Usage
    """

    return render_template('home.html')