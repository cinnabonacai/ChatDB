const chatbox = document.getElementById('chatbox');
const userInput = document.getElementById('user-input');
const submitBtn = document.getElementById('submit-btn');

// Function to send the message
function sendMessage() {
    const userQuestion = userInput.value.trim(); // Trim whitespace

    // Check if the input is empty
    if (userQuestion === '') {
        return; // Don't send an empty message
    }

    userInput.value = ''; // Clear input field

    // Display user's question
    displayMessage('user', userQuestion);

    // TODO: Send userQuestion to your backend (ChatDB)
    // TODO: Receive response from backend 
    // Example using fetch API:
    fetch('/your-backend-endpoint', {  // Replace with your actual endpoint
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userQuestion })
    })
    .then(response => response.json())
    .then(data => {
        // Display response in chatbox
        displayMessage('bot', data.response); 
    })
    .catch(error => {
        console.error('Error:', error);
        displayMessage('bot', "Sorry, there was an error processing your request.");
    });
}

// Event listener for submit button
submitBtn.addEventListener('click', sendMessage);

// Event listener for Enter key press
userInput.addEventListener('keyup', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

function displayMessage(sender, message) {
    const messageElement = document.createElement('div');
    messageElement.classList.add(sender);
    messageElement.textContent = message;
    chatbox.appendChild(messageElement);

    // Auto-scroll to bottom
    chatbox.scrollTop = chatbox.scrollHeight;
}