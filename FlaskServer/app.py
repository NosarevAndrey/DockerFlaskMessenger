import datetime
import os
import psycopg2
from flask import Flask, jsonify,  request, redirect, url_for, render_template, session
from flask_socketio import SocketIO, send, emit, disconnect
from datetime import datetime
from flask_cors import CORS

# from gevent.pywsgi import WSGIServer
# import hashlib

#my libs
from message_store import MessageStore
from database_handler import DatabaseHandler as dbh
from database_handler import DbhResponse
from utils import *


users = {} #TODO: Delete
user_sockets = {}
active_users = set()

message_storage = MessageStore()
message_storage.add_message('User1', 'User2', {'text': 'Hello!', 'timestamp': '2024-04-05 12:00:00', 'sender': 'User1'})
message_storage.add_message('User1', 'User1', {'text': 'Hello me!', 'timestamp': '2024-04-05 12:00:00', 'sender': 'User1'})
message_storage.add_message('User2', 'User1', {'text': 'Hi there!', 'timestamp': '2024-04-05 12:01:00', 'sender': 'User2'})




app = Flask(__name__)
app.config['SECRET_KEY'] = 'admin'
socketio = SocketIO(app, manage_session=True)


@socketio.on('connect')
def handle_connect():
    # Get the username from the client
    username = request.args.get('username')

    if not username:
        return

    get_response = dbh().get_user(username)

    if not get_response.valid():
        return

    if not get_response.data:
        print(f"Connection denied for unknown user: {username}")
        disconnect()
        return

    active_users.add(username)
    # Store the username and its corresponding socket in the dictionary
    user_sockets[username] = request.sid
    print(user_sockets[username])
    print(f"Socket connected for user: {username}")

    sorted_users = merge_and_sort(set(active_users), users.keys())
    user_status_list = [(username, (username in active_users)) for username in sorted_users]
    emit('update_users', {'user_status_list': user_status_list}, broadcast=True)



@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    sender = data['sender']
    receiver = data['receiver']
    text = data['text']

    timestamp = datetime.now()
    response = dbh().store_message(sender, receiver, text, timestamp)
    if not response.valid():
        return

    message_storage.add_message(sender, receiver, {
        'text': text,
        'timestamp': format_timestamp(timestamp),
        'sender': sender})

    sender_sid = user_sockets.get(sender)
    receiver_sid = user_sockets.get(receiver)

    data['timestamp'] = format_timestamp(timestamp)
    if sender_sid:
        emit('new_message', data, room=sender_sid)
    if receiver_sid and sender_sid != receiver_sid:
        emit('new_message', data, room=receiver_sid)

@socketio.on('disconnect')
def handle_disconnect():
    # Remove the username and its corresponding socket from the dictionary upon disconnection
    for username, sid in user_sockets.items():
        if sid == request.sid:
            del user_sockets[username]
            print(f"Socket disconnected for user: {username}")
            active_users.remove(username)


            sorted_users = merge_and_sort(set(active_users), users.keys())
            user_status_list = [(username, (username in active_users)) for username in sorted_users]
            emit('update_users', {'user_status_list': user_status_list}, broadcast=True)
            break

@app.route('/')
def index():
    # return render_template('login.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Render the login page template for GET requests
        return render_template('login.html')

    # Get username and password from form submission
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        return render_template('login.html', error="Invalid username or password.")
    if username.strip() == '' or password.strip() == '':
        return render_template('login.html', error="Invalid username or password.")

    get_response = dbh().get_user(username)

    if not get_response.valid():
        return render_template('login.html', error="Failed to add user. Please try again later.")

    if get_response.data:
        if password != get_response.data[1]:
            return render_template('login.html', error="Invalid username or password.")
    else:
        add_response = dbh().add_user(username, password)
        if not add_response.valid():
            return render_template('login.html', error="Failed to add user. Please try again later.")

    #active_users.add(username)
    return redirect(url_for('chat_list', username=username, opponent_username=username))

@app.route('/chat/<username>/<opponent_username>')
def chat_list(username, opponent_username):
    messages = message_storage.get_messages(username, opponent_username)
    messages_response = dbh().get_chat_messages(username, opponent_username)
    
    if not messages_response.valid():
        return render_template('chat_list.html',
                               username=username,
                               opponent_username=opponent_username,
                               active_users=active_users,
                               messages={},
                               error="Failed to load messages")

    return render_template('chat_list.html',
                           username=username,
                           opponent_username=opponent_username,
                           active_users=active_users,
                           messages=messages_response.data)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080,  allow_unsafe_werkzeug=True, debug=True)





