const chatbox = document.getElementById('chatbox'); // the elements embedded into the chatbox
const userInput = document.getElementById('user-input'); // the input field where the user types his/her message

let attachedFiles = []; // all files required to be uploaded
let lastAttachedFiles = []; // used to store the last uploaded files

/* Function to upload one or more files at the input text, then move one keyword downward to generate the input text */
function handleFileUpload() {
    let fileUpload = document.getElementById('file-upload');
    const allFiles = Array.from(fileUpload.files);

    // Get all files
    allFiles.forEach((file) => {
        if (file.name.endsWith('.json')) {
            attachedFiles.push(`../Database/NoSQL/${file.name}`);
        } else if (file.name.endsWith('.csv')) {
            attachedFiles.push(`../Database/SQL/data/${file.name}`);
        }
        userInput.value += `${file.name} `;
    });
}

/* Function to dynamically render data as a table */
function renderTable(data) {
    //print(data)
    const tableContainer = document.createElement('div');
    tableContainer.classList.add('table-container');

    Object.keys(data).forEach((key) => {
        const section = data[key];

        // Create a table title
        const title = document.createElement('h3');
        title.textContent = key;
        tableContainer.appendChild(title);

        // Create the table element
        const table = document.createElement('table');
        table.classList.add('data-table');

        // Create the header row
        const headerRow = document.createElement('tr');
        section.fields.forEach((field) => {
            const headerCell = document.createElement('th');
            headerCell.textContent = field;
            headerRow.appendChild(headerCell);
        });
        table.appendChild(headerRow);

        // Create the data rows
        section.rows.forEach((row) => {
            const dataRow = document.createElement('tr');
            section.fields.forEach((field) => {
                const dataCell = document.createElement('td');
                dataCell.textContent = row[field];
                dataRow.appendChild(dataCell);
            });
            table.appendChild(dataRow);
        });
        tableContainer.appendChild(table);
    });

    chatbox.appendChild(tableContainer);
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

    // (4) Determine query text based on whether files were uploaded
    const queryParts = userTyped.split('\n');
    const query_text = queryParts.length > 1 ? queryParts[1] : queryParts[0];

    //(5) create a new div element to display the user's message 
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', 'user-message');
    messageElement.textContent = query_text;
    chatbox.appendChild(messageElement);

    // (6) Check for files
    if (attachedFiles.length === 0 && lastAttachedFiles.length > 0) {
        alert('No files uploaded. Using the previously uploaded files.');
        attachedFiles = [...lastAttachedFiles];
    } else if (attachedFiles.length === 0 && lastAttachedFiles.length === 0) {
        alert('No files uploaded and no previous files available.');
        return;
    }

    // (7) send the message to the backend using a variable called 'data'
    fetch(`http://localhost:6600/generate_query?query=${query_text}&files=${JSON.stringify(attachedFiles)}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to send the message');
        }
        return response.json();
    })
    .then(data => {
        if (data.type === 'query') {
            // If the result is a query, display it as plain text
            const responseElement = document.createElement('pre');
            responseElement.classList.add('message', 'bot-message');
            responseElement.textContent = data.result;
            chatbox.appendChild(responseElement);
        } else if (data.type === 'data') {
            const responseElement = document.createElement('pre');
            responseElement.classList.add('message', 'bot-message');
            responseElement.textContent = data.result;
            chatbox.appendChild(responseElement);
            // If the result is data, parse it and render it as a table
            //try {
                //const parsedData = JSON.parse(data.result);
                //renderTable(parsedData);
            //} catch (error) {
                //console.error('Failed to parse data:', error);
            //}
        }

        // Save uploaded files for future use
        lastAttachedFiles = [...attachedFiles];
        attachedFiles = []; // Clear current files
    })
    .catch(error => {
        console.error("Error occurred: ", error);
    });
}
