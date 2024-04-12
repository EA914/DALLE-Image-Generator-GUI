import os
import pyaudio
import wave
import openai
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import keyboard
import requests

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set the OpenAI API key
openai.api_key = OPENAI_API_KEY

def transcribe_audio_from_mic():
	# Set up audio recording parameters
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 16000
	CHUNK = 1024

	# Initialize PyAudio and start recording
	audio = pyaudio.PyAudio()
	stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

	print("Recording... Press Enter to stop.")

	frames = []
	while True:
		data = stream.read(CHUNK)
		frames.append(data)
		if keyboard.is_pressed('enter'):  # Stop recording when Enter key is pressed
			print("Stop recording.")
			break

	# Stop and close the stream and PyAudio
	stream.stop_stream()
	stream.close()
	audio.terminate()

	# Save the recorded frames as a WAV file
	wav_file_path = Path(__file__).parent / "temp_recording.wav"
	with wave.open(str(wav_file_path), 'wb') as wf:
		wf.setnchannels(CHANNELS)
		wf.setsampwidth(audio.get_sample_size(FORMAT))
		wf.setframerate(RATE)
		wf.writeframes(b''.join(frames))

	# Transcribe the audio using OpenAI's Whisper model
	with open(wav_file_path, 'rb') as audio_file:
		transcription_response = openai.audio.transcriptions.create(
			model="whisper-1",
			file=audio_file,
			response_format="text"
		)

	transcription = transcription_response
	print("Transcription response:", transcription)

	return transcription

def generate_and_open_image(prompt):
	"""Generate an image from the prompt and open it using the default image viewer"""
	# Generate an image using DALL-E 3
	response = openai.images.generate(
		model="dall-e-3",
		prompt=prompt,
		size="1024x1024",
		quality="standard",
		n=1
	)
	
	image_url = response.data[0].url
	image_path = Path(__file__).parent / f"DALLE{next_image_number()}.jpg"

	# Download the image
	image_data = requests.get(image_url).content
	with open(image_path, "wb") as f:
		f.write(image_data)

	# Open the image in the default viewer
	subprocess.run(["cmd", "/c", "start", "", str(image_path)], shell=True)

def next_image_number():
	"""Generate the next image file number"""
	existing_files = list(Path(__file__).parent.glob('DALLE*.jpg'))
	return len(existing_files) + 1

def main_loop():
	while True:
		transcription = transcribe_audio_from_mic()
		if transcription.strip().lower() in ["exit", "exit.", "exit", "exit."]:
			print("Exiting...")
			break
		elif transcription:
			generate_and_open_image(transcription)

# Main program loop
if __name__ == "__main__":
	main_loop()
