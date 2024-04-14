document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById('sendButton');
    const dictateButton = document.getElementById('dictateButton');

    sendButton.addEventListener('click', sendPrompt);
    dictateButton.addEventListener('click', startDictation);
});

let isProcessing = false;

function sendPrompt() {
    if (isProcessing) return;
    isProcessing = true;
    showLoadingBar(true);

    const promptInput = document.getElementById('promptInput');
    const prompt = promptInput.value.trim();
    processPrompt(prompt);
}

function processPrompt(prompt) {
    if (!prompt) {
        alert('Please enter a prompt.');
        showLoadingBar(false);
        isProcessing = false;
        return;
    }
    generateImage(prompt)
        .then(() => {
            showLoadingBar(false);
            isProcessing = false;
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Failed to generate image. Check the console for more information.');
            showLoadingBar(false);
            isProcessing = false;
        });
}

function startDictation() {
    if (isProcessing) return;
    isProcessing = true;
    const dictateButton = document.getElementById('dictateButton');
    dictateButton.innerText = 'Recording...';
    dictateButton.disabled = true;

    navigator.mediaDevices.getUserMedia({ audio: true, video: false })
        .then(stream => {
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            const audioChunks = [];
            mediaRecorder.addEventListener("dataavailable", event => {
                audioChunks.push(event.data);
            });

            setTimeout(() => {
                mediaRecorder.stop();
            }, 5000); // Stop after 5 seconds

            mediaRecorder.addEventListener("stop", () => {
                const audioBlob = new Blob(audioChunks);
                sendAudioToServer(audioBlob);
            });
        });
}

function sendAudioToServer(audioBlob) {
    const formData = new FormData();
    formData.append("audio", audioBlob);

    fetch('http://localhost:3000/transcribe-audio', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('promptInput').value = data.transcription;
        processPrompt(data.transcription);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error processing audio. See console for details.');
    })
    .finally(() => {
        document.getElementById('dictateButton').innerText = 'Dictate';
        document.getElementById('dictateButton').disabled = false;
        isProcessing = false;
    });
}

function generateImage(prompt) {
    return fetch('http://localhost:3000/generate-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt: prompt })
    })
    .then(response => response.json())
    .then(data => {
        if (data && data.data && data.data[0].url) {
            displayImage(data.data[0].url);
        } else {
            throw new Error('Failed to generate image');
        }
    });
}

function displayImage(imageUrl) {
    const imageContainer = document.getElementById('imageContainer');
    imageContainer.innerHTML = `<img src="${imageUrl}" alt="Generated Image">`;
}

function showLoadingBar(show) {
    const loadingBar = document.getElementById('loadingBar');
    if (show) {
        loadingBar.classList.remove('hidden');
        loadingBar.style.width = '100%';
    } else {
        loadingBar.style.width = '0';
        setTimeout(() => loadingBar.classList.add('hidden'), 500);
    }
}
