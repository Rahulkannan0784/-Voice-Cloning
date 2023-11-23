import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from deep_translator import GoogleTranslator
from gtts import gTTS
import playsound
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from pydub import AudioSegment

# Get the current working directory
base_path = Path(__file__).resolve().parent

# A dictionary containing language names and their corresponding codes
dic = {'English': 'en', 'Hindi': 'hi', 'Telugu': 'te'}

class TranslatorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Audio/Video Translator")
        
        self.file_path_label = tk.Label(self.master, text="File Path:")
        self.file_path_label.grid(row=0, column=0)

        self.file_path_entry = tk.Entry(self.master, width=50)
        self.file_path_entry.grid(row=0, column=1)

        self.browse_button = tk.Button(self.master, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2)

        self.language_label = tk.Label(self.master, text="Target Language:")
        self.language_label.grid(row=1, column=0)

        # Create a list of language names
        language_names = list(dic.keys())
        self.language_var = tk.StringVar(self.master)
        self.language_var.set(language_names[0])  # Default language
        self.language_menu = tk.OptionMenu(self.master, self.language_var, *language_names)
        self.language_menu.grid(row=1, column=1)

        self.translate_button = tk.Button(self.master, text="Translate and Play", command=self.translate_and_play)
        self.translate_button.grid(row=2, column=0, columnspan=3)

    def browse_file(self):
        file_path = filedialog.askopenfilename()

        # Replace special characters in file path
        file_path = file_path.replace("&", "_")

        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)

    def convert_to_pcm_wav(self, input_file, output_file):
        audio = AudioSegment.from_file(input_file)
        audio.export(output_file, format="wav")

    def translate_and_play(self):
        file_path = self.file_path_entry.get()
        lang_name = self.language_var.get()

        if not file_path:
            print("Please select a file.")
            return

        if lang_name not in dic:
            print("Invalid language name.")
            return

        lang_code = dic[lang_name]

        print("Full File Path:", file_path)  # Display the full file path for debugging

        media_type = "audio"  # Assume the file is audio, change to "video" if needed

        try:
            if media_type == "audio":
                pcm_wav_path = base_path / "converted_audio.wav"
                self.convert_to_pcm_wav(file_path, pcm_wav_path)
                self.translate_and_play_audio(pcm_wav_path, lang_code)
            elif media_type == "video":
                self.translate_and_play_video(file_path, lang_code)
        except Exception as e:
            print(f"Translation error: {e}")
            translated_text = "Translation not available"
            print("Translated text:", translated_text)

    def translate_and_play_audio(self, file_path, lang_code):
        recognizer = sr.Recognizer()

        # Convert MP3 to WAV
        audio = AudioSegment.from_mp3(file_path)
        wav_path = base_path / "temp.wav"
        audio.export(wav_path, format="wav")

        try:
            with sr.AudioFile(wav_path) as source:
                audio_text = recognizer.record(source)
        except FileNotFoundError:
            print(f"Error: File not found at {wav_path}")
            return

        translator = GoogleTranslator(source='auto', target=lang_code)
        translated_text = translator.translate(text=audio_text, lang_src='auto', lang_tgt=lang_code)

        speak = gTTS(text=translated_text, lang=lang_code, slow=False)
        speak.save("captured_voice.mp3")

        # Using the file path variable
        playsound.playsound(str(wav_path), True)

        # Clean up the temporary WAV file
        os.remove(wav_path)

    def translate_and_play_video(self, file_path, lang_code):
        video_clip = VideoFileClip(file_path)
        audio_clip = video_clip.audio

        # Convert the audio
        audio_clip.write_audiofile("captured_audio.mp3", codec="pcm_s16le", ffmpeg_params=["-ac", "2"])

        recognizer = sr.Recognizer()

        with sr.AudioFile("captured_audio.mp3") as source:
            audio_text = recognizer.record(source)

        translator = GoogleTranslator(source='auto', target=lang_code)
        translated_text = translator.translate(text=audio_text, lang_src='auto', lang_tgt=lang_code)

        speak = gTTS(text=translated_text, lang=lang_code, slow=False)
        speak.save("captured_voice.mp3")

        # Using the file path variable
        playsound.playsound("captured_voice.mp3", True)

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()
