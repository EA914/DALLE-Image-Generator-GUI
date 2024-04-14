# DALLE Image Generator with Dictation Website

![dalleweb](https://github.com/EA914/DALLE-Image-Generator-GUI/assets/14112758/b944004f-c64e-4e02-976d-26c6332b547e)


## Instructions

1. Clone the repository
`git clone https://github.com/EA914/DALLE-Image-Generator-GUI.git`
2. Navigate to project repository
`cd Dalle-Image-Generator-GUI`
3. Install dependencies
`npm install`
4. Run the server
`node server.mjs`
5. Open your web browser and go to `http://localhost:3000`

## Edits you must make
1. Line 54 in `server.mjs` must be changed to point to the ffmpeg.exe file path:
Copy and paste your file path in

`const command = "C:\PATH\TO\ffmpeg.exe" -i "${filePath}" "${outputFilePath}";`

3. [Open AI API Key](https://platform.openai.com/account/api-keys) must be inserted in the .env file



# Dependencies
* [FFMPEG](https://ffmpeg.org/)
