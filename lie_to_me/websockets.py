
from flask_socketio import emit
from flask import request
from lie_to_me import socketio


# An active connection exists between client and server
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Server received a message from Client
@socketio.on('message')
def handle_message_receival(json):
    print('Received: {0}'.format(str(json)))

# Affective Client ready to receive photos
@socketio.on('ready_receive')
def handle_ready_receive(json):
    print('Client Ready to Recieve: {0}'.format(str(json)))

# auto implemented backends are 'connect', 'disconnect', 'message' and 'json'
# to send data -> use send to send a standard Message (under the message)
# use emit to send a custom message to the client
