import os
import uuid
from django.conf import settings
from openai import OpenAI

# OpenAI API Key setup
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-proj-placeholder")
client = OpenAI(api_key=OPENAI_API_KEY)

class VoiceService:
    @staticmethod
    def transcribe_audio(audio_file):
        """
        Whisper API yordamida audio faylni o'zbekcha matnga o'giradi.
        """
        # Vaqtinchalik faylni saqlash
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp_voice")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Audio kengaytmasini aniqlash (default webm yoki wav)
        ext = "webm"
        if audio_file.name:
            ext = audio_file.name.split(".")[-1]
            
        temp_filename = f"transcribe_{uuid.uuid4().hex}.{ext}"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        try:
            with open(temp_path, "wb+") as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)
            
            # Whisper orqali transkripsiya qilish
            with open(temp_path, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="uz"
                )
            
            return transcription.text
        except Exception as e:
            print(f"STT Error: {str(e)}")
            raise e
        finally:
            # Vaqtinchalik faylni tozalash
            if os.path.exists(temp_path):
                os.remove(temp_path)

    @staticmethod
    def synthesize_speech(text, voice_type="alloy"):
        """
        OpenAI TTS API yordamida matnli javobni audio faylga (MP3) o'giradi va URL qaytaradi.
        """
        voice_dir = os.path.join(settings.MEDIA_ROOT, "voice_responses")
        os.makedirs(voice_dir, exist_ok=True)
        
        filename = f"voice_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(voice_dir, filename)
        
        try:
            # OpenAI TTS chaqiruvi
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice_type, # alloy, echo, fable, onyx, nova, shimmer
                input=text
            )
            
            # Faylga yozish
            response.write_to_file(filepath)
            
            # Fayl URL manzilini qaytarish
            audio_url = f"{settings.MEDIA_URL}voice_responses/{filename}"
            return audio_url
        except Exception as e:
            print(f"TTS Error: {str(e)}")
            return None
