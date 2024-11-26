
const chatbox = document.getElementById('chatbox'); // the elements embedded into the chatbox
const userInput = document.getElementById('user-input'); // the input field where the user types his/her message






let attachedFiles = []; // all files required to be uploaded
/* Function to upload one or more files at the input text, then move one keyword downard to generate the input text*/
function handleFileUpload() {
    let fileUpload = document.getElementById('file-upload');
    const allFiles = Array.from(fileUpload.files);
   
    // Get all files
    allFiles.forEach((file) => {
        if (file.name.endsWith('.json')) {
            attachedFiles.push(`../Database/NoSQL/${file.name}`);
        }
        else if (file.name.endsWith('.csv')) {
            attachedFiles.push(`../Database/SQL/data/${file.name}`);
        }    
        userInput.value += `${file.name} `
    });
}


/* Function to send the message to the backend */
function sendMessage() {

    /* step 1: retrieve the user's question */
    
    // (1) trim() removes the whitespace from both ends of the string
    const userTyped = userInput.value.trim();

    // (2) Check if the input is empty. If so, the empty message will be returned
    if (userTyped === '') {
        return; // Don't send an empty message
    }

    // (3) Clear the input field
    userInput.value = ''; // Clear input field

    // (4) place the content at the chatbox
    const query_text = userTyped.split('\n')[1]; 
    
    
    //(5) create a new div element to display the user's message 
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', 'user-message');
    messageElement.textContent = query_text;
    chatbox.appendChild(messageElement);

    // (6) stimulate a bot response
    setTimeout(() => {
        
        let responseQuery = '';
        // send the message to the backend using a variable called 'data'
        fetch(`http://localhost:6600/generate_query?query=${query_text}&files=${JSON.stringify(attachedFiles)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to send the message')
            }
            return response.json();
        })
        .then(data => {
            console.log("data is: ", data);
            responseQuery = data['result']
            
            console.log("My current responseQuery is: " + responseQuery);
            const responseElement = document.createElement('pre');
            responseElement.classList.add('message', 'bot-message');
            responseElement.textContent = responseQuery;
            chatbox.appendChild(responseElement);
            attachedFiles = [];
        })
        .catch(error => {
            console.error("Error occurred: ", error);
        })
    }, 1000);
}