
from flask_socketio import emit
from lie_to_me import socketio

# An active connection exists between client and server
@socketio.on('connection_active')
def handle_client_connect_event(json):
    emit('connect_ack', {'data': 'Server ack connection'})
    print('Connection Active: {0}'.format(str(json)))

# Server received a message from Client
@socketio.on('message')
def handle_message_receival(json):
    print('Received: {0}'.format(str(json)))

# Client disconnected from Server
@socketio.on('disconnect')
def handle_disconnect(json = None):
    print('Client Disconnected: {0}'.format(str(json)))


# auto implemented backends are 'connect', 'disconnect', 'message' and 'json'
# to send data -> use send to send a standard Message (under the message)
# use emit to send a custom message to the client
