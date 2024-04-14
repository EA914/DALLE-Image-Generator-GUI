import express from 'express';
import multer from 'multer';
import fetch from 'node-fetch';
import { config } from 'dotenv';
import fs from 'fs';
import FormData from 'form-data';
import { exec } from 'child_process';

config();

const app = express();
const port = process.env.PORT || 3000;
const upload = multer({ dest: 'uploads/' }); // Temporary storage for audio files

app.use(express.static('public'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.post('/generate-image', async (req, res) => {
    const { prompt } = req.body;
    const apiKey = process.env.OPENAI_API_KEY;
    const url = 'https://api.openai.com/v1/images/generations';

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: "dall-e-3",
                prompt: prompt,
                n: 1,
                size: "1024x1024",
                quality: "standard"
            })
        });
        const data = await response.json();
        res.status(200).send(data);
    } catch (error) {
        console.error('Error:', error);
        res.status(500).send({ message: 'Failed to generate image', error });
    }
});

app.post('/transcribe-audio', upload.single('audio'), async (req, res) => {
    if (!req.file) {
        return res.status(400).send({ message: 'No file uploaded.' });
    }

    const filePath = req.file.path;
    const outputFilePath = `${filePath}.wav`;
    const command = `"C:\PATH\TO\ffmpeg.exe" -i "${filePath}" "${outputFilePath}"`;

    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error('Error converting file:', stderr);
            fs.unlinkSync(filePath); // Clean up original file
            return res.status(500).send({ message: 'Failed to convert audio', error: stderr });
        }
        console.log('Conversion stdout:', stdout);
        sendAudioForTranscription(outputFilePath, res);
        fs.unlinkSync(filePath); // Clean up original file after conversion
    });
});

function sendAudioForTranscription(filePath, res) {
    const apiKey = process.env.OPENAI_API_KEY;
    const url = 'https://api.openai.com/v1/audio/transcriptions';

    const formData = new FormData();
    formData.append('file', fs.createReadStream(filePath));
    formData.append('model', 'whisper-1');

    fetch(url, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            ...formData.getHeaders()
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        fs.unlinkSync(filePath); // Clean up the WAV file after processing
        if (data.error) {
            console.error('Transcription error:', data.error);
            res.status(500).send({ message: 'Failed to transcribe audio', error: data.error });
            return;
        }
        console.log('Transcription:', data.text); // Adjust to match the response structure
        res.status(200).send({ transcription: data.text }); // Adjust to match the response structure
    })
    .catch(error => {
        console.error('Error during transcription:', error);
        fs.unlinkSync(filePath); // Clean up the WAV file after processing
        res.status(500).send({ message: 'Failed to transcribe audio', error });
    });
}


app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
