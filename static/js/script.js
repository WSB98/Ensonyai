document.addEventListener('DOMContentLoaded', async function () {
    const chatBox = document.getElementById('chat-box');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-btn');
    let chatHistory = []; // Initialize chat history

    // Function to add message to chat box
    function addMessageToChat(message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        // regex
        var text = message;
        text = text.replace(/<(.+?)>/g, "&lt;$1&gt"); // Replace all tags
        text = text.replace(/(?:\r\n|\r|\n)/g, '<br>'); // Replace all new lines
        text = text.replace(/```(.+?)```/g, "<pre><code>$1</code></pre>"); // Replace backticks with pre/code
        // Add a regex to handle **bold** text
        text = text.replace(/\*\*(.*?)\*\*/g, "<b>$1</b>");
        // Add a regex to handle * bullet points
        text = text.replace(/\* (.*?)(<br>|$)/g, "<li>$1</li>");
        // Wrap the resulting text in a list if there are bullet points
        if (text.includes("<li>")) {
          text = "<ul>" + text + "</ul>";
        }
        text = `<code>${text}</code>`;
        messageElement.innerHTML = text;
        // Assuming user and bot roles for message formatting
        messageElement.classList.add(message.role === 'user' ? 'user-message' : 'bot-message');
        chatBox.appendChild(messageElement);
        // Scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function getEnsonyaHistory(){
        const ensonyaJSON = await fetch('http://localhost:5000/api/getChatHistory');
        const response = await ensonyaJSON.json();
        return response.history
    }
    chatHistory = await getEnsonyaHistory();
    console.log(chatHistory)

    // Function to send message to Flask API
    async function sendMessageToAPI(message) {
        try {
            const response = await fetch('http://localhost:5000/api/sendMessage', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ "message":message, 'history': chatHistory })
            });
            if (response.ok) {
                const responseData = await response.json();
                // Assuming the API returns the processed message
                const processedMessage = responseData.message.content.content;
                addMessageToChat(processedMessage);
                chatHistory = responseData.history
                chatHistory.push({"role":"assistant","content":processedMessage})
                return processedMessage
            } else {
                throw new Error('Failed to send message to API');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // Event listener for send button click
    sendButton.addEventListener('click', function () {
        var message = messageInput.value.trim();
        if (message !== '') {
            const userMessage = { "role": 'user', "content": message };
            addMessageToChat(userMessage.content);
            sendMessageToAPI(message);
            messageInput.value = ''; // Clear input field
           
        }
    });
});

