import os
from flask import Flask, jsonify,  request, redirect, url_for, render_template, session
from flask_socketio import SocketIO, send, emit, disconnect
from flask_cors import CORS
# from gevent.pywsgi import WSGIServer
# import hashlib
#my libs
from message_store import MessageStore




users = {}
user_sockets = {}

message_storage = MessageStore()
message_storage.add_message('User1', 'User2', {'text': 'Hello!', 'timestamp': '2024-04-05 12:00:00', 'sender': 'User1'})
message_storage.add_message('User1', 'User1', {'text': 'Hello me!', 'timestamp': '2024-04-05 12:00:00', 'sender': 'User1'})
message_storage.add_message('User2', 'User1', {'text': 'Hi there!', 'timestamp': '2024-04-05 12:01:00', 'sender': 'User2'})


active_users = set()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'admin'
socketio = SocketIO(app, manage_session=True)



@socketio.on('connect')
def handle_connect():
    # Get the username from the client
    username = request.args.get('username')
    if username:
        if username in users.keys():
            active_users.add(username)
            # Store the username and its corresponding socket in the dictionary
            user_sockets[username] = request.sid
            print(user_sockets[username])
            print(f"Socket connected for user: {username}")
            emit('update_users', {'users': sorted(list(active_users))}, broadcast=True)
        else:
            print(f"Connection denied for unknown user: {username}")
            disconnect()

@socketio.on('message')
def handle_message(data):
    print('Received message:',data)
    sender = data['sender']
    receiver = data['receiver']
    text = data['text']
    timestamp = data['timestamp']
    message_storage.add_message(sender, receiver, {'text': text, 'timestamp': timestamp, 'sender': sender})

    sender_sid = user_sockets.get(sender)
    receiver_sid = user_sockets.get(receiver)

    # Emit the message to the sender and receiver if they are online
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

            emit('update_users', {'users': sorted(list(active_users))}, broadcast=True)
            break

@app.route('/')
def index():
    # return render_template('login.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get username and password from form submission
        username = request.form['username']
        password = request.form['password']


        if not username or not password:
            return render_template('login.html', error="Invalid username or password.")
        if username.strip() == '' or password.strip() == '':
            return render_template('login.html', error="Invalid username or password.")
        if username in users.keys():
            if password != users[username]:
                return render_template('login.html', error="Invalid username or password.")
            active_users.add(username)
            return redirect(url_for('chat_list', username=username, opponent_username=username))
        else:
            active_users.add(username)
            users[username] = password
            # If valid, redirect to chat list page
            return redirect(url_for('chat_list', username=username, opponent_username=username))

    # Render the login page template for GET requests
    return render_template('login.html')

@app.route('/chat/<username>/<opponent_username>')
def chat_list(username, opponent_username):
    self_messages = message_storage.get_messages(username, opponent_username)
    return render_template('chat_list.html', username=username, opponent_username=opponent_username, active_users=active_users, messages=self_messages)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080,  allow_unsafe_werkzeug=True, debug=True)





