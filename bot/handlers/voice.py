from ..config import Groq_Client

def transcribe_audio(audio_file_path):
    try:
        # Open the audio file and send it to Groq's Whisper model
        with open(audio_file_path, "rb") as file:
            transcription = Groq_Client.audio.transcriptions.create(
                file=(audio_file_path, file.read()),
                model="whisper-large-v3-turbo",
                language="en",
                response_format="verbose_json",
            )
            
            return transcription.text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None