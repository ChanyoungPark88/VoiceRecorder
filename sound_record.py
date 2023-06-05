import os
import wave
import time
import threading
import tkinter as tk
import pyaudio
import sounddevice as sd
from PIL import Image, ImageTk


class VoiceRecorder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title('Voice recorder')

        # Load and resize the image
        image_path = os.path.expanduser("~/Desktop/VoiceRecorder/recorder.png")
        image = Image.open(image_path)
        resized_image = image.resize((120, 120))
        button_image = ImageTk.PhotoImage(resized_image)

        self.button = tk.Button(image=button_image, command=self.click_handler)
        self.button.image = button_image
        self.button.pack()

        self.device_listbox = tk.Listbox()
        self.device_listbox.pack()
        self.label = tk.Label(text='00:00:00')
        self.label.pack()
        self.recording = False

        self.populate_device_list()

        self.root.mainloop()

    def populate_device_list(self):
        devices = sd.query_devices()
        input_devices = [
            device for device in devices if device['max_input_channels'] > 0]

        for device in input_devices:
            self.device_listbox.insert(
                tk.END, f"{device['name']}")

    def click_handler(self):
        if self.recording:
            self.recording = False
            self.button.config(fg='black')
        else:
            self.recording = True
            self.button.config(fg='red')
            threading.Thread(target=self.record).start()

    def record(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1,
                            rate=44100, input=True, frames_per_buffer=1024)

        frames = []

        start = time.time()

        while self.recording:
            data = stream.read(1024)
            frames.append(data)

            passed = time.time() - start
            secs = passed % 60
            mins = passed // 60
            hours = mins // 60

            self.label.config(
                text=f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d}")

        stream.stop_stream()
        stream.close()
        audio.terminate()

        exists = True
        i = 1
        while exists:
            if os.path.exists(f'recording{i}.wav'):
                i += 1
            else:
                exists = False

        sound_file = wave.open(f'recording{i}.wav', 'wb')
        sound_file.setnchannels(1)
        sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        sound_file.setframerate(44100)
        sound_file.writeframes(b''.join(frames))
        sound_file.close()


VoiceRecorder()
