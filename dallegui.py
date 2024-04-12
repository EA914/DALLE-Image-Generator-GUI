import os
import tkinter as tk
from tkinter import messagebox, PhotoImage, filedialog, Menu
import threading
import pyaudio
import wave
import openai
import requests
from pathlib import Path
from dotenv import load_dotenv
import json
import queue

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set the OpenAI API key
openai.api_key = OPENAI_API_KEY

def transcribe_audio_from_mic(callback, status_queue):
	"""Records audio from the microphone and returns its transcription using Whisper."""
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 16000
	CHUNK = 1024
	RECORD_SECONDS = 5	

	audio = pyaudio.PyAudio()
	stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
	frames = []

	recording_label.config(text="Recording...")	 # Show recording label

	for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		data = stream.read(CHUNK)
		frames.append(data)

	recording_label.config(text="")	 # Hide recording label after stopping

	stream.stop_stream()
	stream.close()
	audio.terminate()

	status_queue.put("Recording complete. Processing...")  # Send status update

	wav_file_path = Path(__file__).parent / "temp_recording.wav"
	with wave.open(str(wav_file_path), 'wb') as wf:
		wf.setnchannels(CHANNELS)
		wf.setsampwidth(audio.get_sample_size(FORMAT))
		wf.setframerate(RATE)
		wf.writeframes(b''.join(frames))

	with open(wav_file_path, 'rb') as audio_file:
		transcription_response = openai.audio.transcriptions.create(
			model="whisper-1",
			file=audio_file,
			response_format="text"
		)

	transcription = transcription_response 
	callback(transcription)	 # Pass the transcription to the callback


def handle_transcription(transcription):
	root.dictate_button.config(text="Dictate", state=tk.NORMAL)
	prompt_entry.delete(0, tk.END)
	prompt_entry.insert(0, transcription)
	generate_and_display_image(transcription)


def on_dictate_button_clicked():
	threading.Thread(target=lambda: transcribe_audio_from_mic(handle_transcription, status_queue), daemon=True).start()


def generate_and_display_image(prompt):
	loading_label.config(text="Loading image...")  # Show loading label

	def do_image_tasks():  
		payload = {
			"model": "dall-e-3",
			"prompt": prompt,
			"size": "1024x1024",
			"quality": "standard",
			"n": 1
		}
		print("Sending payload: ", json.dumps(payload))
		response = openai.images.generate(**payload)  
		print("Received response: ", response.data)

		image_url = response.data[0].url
		image_data = requests.get(image_url).content
		image_path = Path(__file__).parent / "output_image.png"
		with open(image_path, "wb") as f:
			f.write(image_data)

		global current_image_path
		current_image_path = image_path

		root.after(10, update_image_and_window)
		loading_label.config(text="")  # Hide loading label

	threading.Thread(target=do_image_tasks, daemon=True).start()

def update_image_and_window():
	img = PhotoImage(file=current_image_path)
	image_label.config(image=img)
	image_label.image = img

	window_width = img.width() + 50 
	window_height = img.height() + 100 
	root.geometry(f"{window_width}x{window_height}")

def save_image_as():
	if current_image_path:
		file_path = filedialog.asksaveasfilename(defaultextension=".png",
												 filetypes=[("PNG files", "*.png")],
												 title="Save Image As")
		if file_path:
			current_image_path.rename(file_path)
			messagebox.showinfo("Success", f"Image saved successfully at {file_path}")
	else:
		messagebox.showerror("Error", "No image to save.")


def create_context_menu(event):
	context_menu = Menu(root, tearoff=0)
	context_menu.add_command(label="Save", command=save_image_as)
	context_menu.post(event.x_root, event.y_root)


def update_status():
	try:
		status_text = status_queue.get_nowait()	 
		status_label.config(text=status_text)
	except queue.Empty:
		pass
	root.after(100, update_status) 


def on_close():
	root.destroy()	# Close the application
	
# UI Setup
root = tk.Tk()
root.title("DALL-E 3 Image Generator")
root.configure(bg='#282a36')

frame = tk.Frame(root, bg='#282a36')
frame.pack(pady=20)

prompt_entry = tk.Entry(frame, width=80)
prompt_entry.pack(side=tk.LEFT, padx=(0, 10))

generate_button = tk.Button(frame, text="Generate", command=lambda: generate_and_display_image(prompt_entry.get()), bg='#6272a4', fg='white', padx=10, pady=5)
generate_button.pack(side=tk.LEFT, padx=10)

dictate_button = tk.Button(frame, text="Dictate", command=on_dictate_button_clicked, bg='#ff5555', fg='white', padx=10, pady=5)
dictate_button.pack(side=tk.LEFT)
root.dictate_button = dictate_button

image_label = tk.Label(root, bg='#282a36')
image_label.pack(pady=20)
image_label.bind("<Button-3>", create_context_menu)

close_button_img = PhotoImage(file="close_icon.png") 
close_button = tk.Button(root, image=close_button_img, command=on_close, bg='#282a36', bd=0, activebackground='#282a36') 
close_button.pack(pady=10)	

status_label = tk.Label(root, text="", bg='#282a36', fg='white') 
status_label.pack()

recording_label = tk.Label(root, text="", bg='#282a36', fg='white')
recording_label.pack()

loading_label = tk.Label(root, text="", bg='#282a36', fg='white')
loading_label.pack()

current_image_path = None

status_queue = queue.Queue() 
root.after(100, update_status) 

root.mainloop() 