document.addEventListener('DOMContentLoaded', () => {
    const tweetForm = document.getElementById('tweet-form');
    const uploadResult = document.getElementById('upload-result');
    const statsDiv = document.getElementById('stats');

    async function uploadFile() {
        const fileInput = document.getElementById('file-input');
        const file = fileInput.files[0];

        if (!file) {
            alert('Please select a file.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (data.error) {
                alert('Error uploading file: ' + data.error);
            } else {
                alert('File uploaded successfully.');
            }
            console.log(data);
        } catch (error) {
            console.error('Error uploading file:', error);
            alert('Error uploading file.');
        }
    }

    
    // WebSocket connection for real-time statistics
    const socket = io('/stats');

    socket.on('connect', () => {
        console.log('Connected to WebSocket server');
    });

    socket.on('update', (data) => {
        statsDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from WebSocket server');
    });

    socket.on('connect_error', (error) => {
        console.error('WebSocket error:', error);
    });

    // Expose the uploadFile function to the global scope
    window.uploadFile = uploadFile;
});
