import os
import pyaudio
import wave
import openai
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import struct
import pvporcupine
import pvcobra
import requests
import time

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PICOVOICE_API_KEY = os.getenv('PICOVOICE_API_KEY')

# Set the OpenAI API key
openai.api_key = OPENAI_API_KEY

def wait_for_wake_word():
	porcupine = pvporcupine.create(access_key=PICOVOICE_API_KEY, keywords=["Art-Frame"])
	pa = pyaudio.PyAudio()
	stream = pa.open(format=pyaudio.paInt16, channels=1, rate=porcupine.sample_rate,
					 input=True, frames_per_buffer=porcupine.frame_length)

	print("Listening for the wake word...")
	while True:
		pcm = stream.read(porcupine.frame_length)
		pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
		keyword_index = porcupine.process(pcm)
		if keyword_index >= 0:
			print("Wake word detected")
			break

	stream.stop_stream()
	stream.close()
	pa.terminate()
	porcupine.delete()

def record_audio_until_silence():
	cobra = pvcobra.create(access_key=PICOVOICE_API_KEY)
	pa = pyaudio.PyAudio()
	stream = pa.open(format=pyaudio.paInt16, rate=cobra.sample_rate, channels=1,
					 input=True, frames_per_buffer=cobra.frame_length)

	print("Recording...")
	frames = []
	last_voice_time = time.time()
	while True:
		pcm = stream.read(cobra.frame_length)
		pcm = struct.unpack_from("h" * cobra.frame_length, pcm)
		if cobra.process(pcm) > 0.2:
			last_voice_time = time.time()
			frames.append(struct.pack('h' * len(pcm), *pcm))
		elif (time.time() - last_voice_time) > 3:
			print("Silence detected, stopping recording.")
			break

	stream.stop_stream()
	stream.close()
	pa.terminate()
	cobra.delete()

	return b''.join(frames), cobra.sample_rate

def transcribe_and_generate_image(audio_data, sample_rate):
	# Save audio to file
	wav_file_path = Path(__file__).parent / "temp_recording.wav"
	with wave.open(str(wav_file_path), 'wb') as wf:
		wf.setnchannels(1)
		wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
		wf.setframerate(sample_rate)
		wf.writeframes(audio_data)

	# Transcribe audio
	transcription_response = openai.audio.transcriptions.create(
		model="whisper-1",
		file=open(wav_file_path, 'rb'),
		response_format="text"
	)
	transcription = transcription_response
	print("Transcription:", transcription)

	# Generate image with DALL-E
	response = openai.images.generate(
		model="dall-e-3",
		prompt=transcription,
		size="1024x1024",
		n=1
	)
	image_url = response.data[0].url
	image_path = Path(__file__).parent / f"DALLE{next_image_number()}.jpg"
	image_data = requests.get(image_url).content
	with open(image_path, "wb") as img_file:
		img_file.write(image_data)

	# Download the image
	image_data = requests.get(image_url).content
	with open(image_path, "wb") as f:
		f.write(image_data)

	# Open the image in the default viewer
	subprocess.run(["cmd", "/c", "start", "", str(image_path)], shell=True)

def next_image_number():
	existing_files = list(Path(__file__).parent.glob('DALLE*.jpg'))
	return len(existing_files) + 1

def main():
	while True:
		wait_for_wake_word()
		audio_data, sample_rate = record_audio_until_silence()
		transcribe_and_generate_image(audio_data, sample_rate)


if __name__ == "__main__":
	main()
