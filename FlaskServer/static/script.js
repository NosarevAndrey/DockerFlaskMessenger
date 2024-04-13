document.addEventListener('DOMContentLoaded', function () {
    var account_username = document.getElementById('data-username').getAttribute('data-username');
    var opponentUsername = document.getElementById('opponent_username').getAttribute('opponent_username');
    console.log(opponentUsername);
    var chatList = document.querySelectorAll('.chat-list a');

    chatList.forEach(function (link) {
        console.log(link.getAttribute('username'))
        if (link.getAttribute('username') === opponentUsername) {
            link.classList.add('current');
        }
    });
    
    chatList.forEach(function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent the default link behavior
            
            if (!link.classList.contains('current')) {
                console.log(account_username)
                
                var opponentUsername = link.getAttribute('username'); // Get the opponent's username from the link
                
                // Send a request to the server to redirect to the new chat
                window.location.href = '/chat/' + account_username + '/' + opponentUsername;
            }
        });
    });



    
    var socket = io({ query: { username: account_username } });

    socket.on('connect', () => {
        console.log('WebSocket connection established.');
    });
    socket.on('disconnect', function() {
        console.log('WebSocket connection closed.');
    });

    socket.on('update_users', function (data) { 
        console.log("Called update_users")
        var userStatusList = data.user_status_list;
        console.log(userStatusList);
        var chatList = document.querySelector('.chat-list');
        
        chatList.innerHTML = '';
        
        userStatusList.forEach(function (user) {
            var username = user[0];
            var isOnline = user[1];

            var userDiv = document.createElement('div');
            userDiv.classList.add('user');

            var link = document.createElement('a');
            link.setAttribute('href', '#');
            link.textContent = username;
            link.setAttribute('username', username);
           

            var circle = document.createElement('div');
            circle.classList.add('online-indicator');
            if (isOnline) {
                circle.classList.add('online');
            }
            
            userDiv.appendChild(circle);
            userDiv.appendChild(link);


            chatList.appendChild(userDiv);

            if (username === opponentUsername) {
                userDiv.classList.add('current');
            }
            

            userDiv.addEventListener('click', function(event) {
                event.preventDefault(); // Prevent the default link behavior
                
                if (!userDiv.classList.contains('current')) {
                    var opponentUsername = link.getAttribute('username'); // Get the opponent's username from the link
                    
                    // Send a request to the server to redirect to the new chat
                    window.location.href = '/chat/' + account_username + '/' + opponentUsername;
                }
            });

 
        });
        
    });

    socket.on('new_message', function (data) {
        if (data.sender !== opponentUsername && data.sender !== account_username)
            return;

        var messageDiv = document.createElement('div');
        var messageClass = (data.sender === account_username) ? 'from-user' : '';
        messageDiv.className = 'message ' + messageClass;

        var textElement = document.createElement('p');
        textElement.className = 'text';
        var formattedText = data.text.replace(/\n/g, '<br>');
        textElement.innerHTML = formattedText;

        var dateElement = document.createElement('p');
        dateElement.className = 'message-date';
        dateElement.textContent = data.timestamp;

        messageDiv.appendChild(textElement);
        messageDiv.appendChild(dateElement);

        var chatContent = document.querySelector('.chat-content .messages');
        chatContent.appendChild(messageDiv);

        // Scroll to the bottom of the chat content
//        chatContent.scrollTop = chatContent.scrollHeight;
        window.scrollTo(0, document.body.scrollHeight);
        console.log("new message: "+ data.text)
    });
    
    window.addEventListener('beforeunload', function(event) {
    // Perform actions before the page is unloaded (e.g., closing WebSocket connections)
    socket.disconnect(); // Disconnect the WebSocket connection
    });

    var sendButton = document.getElementById('send-button');
    var messageInput = document.getElementById('message-input');

    sendButton.addEventListener('click', function () {
        sendMessage();
    });

    messageInput.addEventListener('keydown', function (event) {
        if (event.ctrlKey && event.keyCode === 13) {
            sendMessage();
        }
    });
    
    function sendMessage() {
        var message = messageInput.value.trim();
        if (message == '') { return; }
        message = message.replace(/<hr>/g, '&dot-line;');
        message = message.replace(/</g, '&lt;').replace(/>/g, '&gt;');
        message = message.replace(/&dot-line;/g, '<hr>');
        console.log(message);
        
        var messageData = {
        text: message,
        sender: account_username,
        receiver: opponentUsername
        };
        
        console.log(messageData);
        socket.emit('message', messageData);
        messageInput.value = '';
    }
});