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
        var userList = data.users;
        console.log(userList);
        var chatList = document.querySelector('.chat-list');
        
        chatList.innerHTML = '';
        
        userList.forEach(function(username) {
            var link = document.createElement('a');
            link.setAttribute('href', '#');
            link.textContent = username;
            link.setAttribute('username', username);
            chatList.appendChild(link);
            if (link.getAttribute('username') === opponentUsername) {
                link.classList.add('current');
            }
            

            link.addEventListener('click', function(event) {
                event.preventDefault(); // Prevent the default link behavior
                
            if (!link.classList.contains('current')) {
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
        chatContent.scrollTop = chatContent.scrollHeight;
        console.log("new message: "+ data.text)
    });
    

    function sendMessage(message) {
        socket.send(message);
    }

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
        console.log(message);
        

        var timestamp = formatTimestamp(new Date());
        var messageData = {
        text: message,
        timestamp: timestamp,
        sender: account_username,
        receiver: opponentUsername
        };
        
        console.log(messageData);
        socket.emit('message', messageData);
        messageInput.value = '';
    }
});

function formatTimestamp(date) {
    var year = date.getFullYear();
    var month = (date.getMonth() + 1).toString().padStart(2, '0'); // Add leading zero if needed
    var day = date.getDate().toString().padStart(2, '0'); // Add leading zero if needed
    var hours = date.getHours().toString().padStart(2, '0'); // Add leading zero if needed
    var minutes = date.getMinutes().toString().padStart(2, '0'); // Add leading zero if needed

    return `${year}-${month}-${day} ${hours}:${minutes}`;
}