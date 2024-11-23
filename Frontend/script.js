const chatbox = document.getElementById('chatbox');
const userInput = document.getElementById('user-input');
const submitBtn = document.getElementById('submit-btn');
const fileUpload = document.getElementById('file-upload');
const uploadedFileInfo = document.getElementById('uploaded-file-info');

let uploadedFile = null;

// Function to send the message
function sendMessage() {
    const userQuestion = userInput.value.trim();

    // Check if the input is empty
    if (userQuestion === '') {
        return; // Don't send an empty message
    }

    userInput.value = ''; // Clear input field

    // Display user's question
    displayMessage('user', userQuestion);

    // Prepare data to send to backend
    const formData = new FormData();
    formData.append('question', userQuestion);
    if (uploadedFile) {
        formData.append('file', uploadedFile);
    }

    // Send userQuestion and file (if any) to your backend
    fetch('/your-backend-endpoint', {  // Replace with your actual endpoint
        method: 'POST',
        body: formData
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

function handleFileUpload(event) {
    uploadedFile = event.target.files[0];
    if (uploadedFile) {
        uploadedFileInfo.textContent = `Uploaded file: ${uploadedFile.name}`;
        displayMessage('user', `File uploaded: ${uploadedFile.name}`);
    }
}

// Event listener for file upload
fileUpload.addEventListener('change', handleFileUpload);

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
    messageElement.classList.add('message', `${sender}-message`);
    messageElement.textContent = message;
    chatbox.appendChild(messageElement);

    // Auto-scroll to bottom
    chatbox.scrollTop = chatbox.scrollHeight;
}