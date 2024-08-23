document.addEventListener('DOMContentLoaded', function() {
    const chatbotButton = document.getElementById('chatbotButton');
    const chatbotInterface = document.getElementById('chatbotInterface');
    const closeChatbot = document.getElementById('closeChatbot');
    const userInput = document.getElementById('userInput');
    const sendMessage = document.getElementById('sendMessage');
    const chatMessages = document.getElementById('chatMessages');

    chatbotButton.addEventListener('click', function() {
        chatbotInterface.style.display = 'block';
    });

    closeChatbot.addEventListener('click', function() {
        chatbotInterface.style.display = 'none';
    });

    sendMessage.addEventListener('click', sendUserMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendUserMessage();
        }
    });

    function sendUserMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessageToChat('User', message);
            userInput.value = '';
            // Simulate AI response (replace with actual AI integration)
            setTimeout(() => {
                addMessageToChat('AI', 'Thank you for your message. How can I assist you today?');
            }, 1000);
        }
    }

    function addMessageToChat(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});