import os
import uuid
from django.conf import settings
from openai import OpenAI

# OpenAI API Key setup - lazy loading to ensure .env is loaded first
def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY", "")
    return OpenAI(api_key=api_key)

class VoiceService:
    @staticmethod
    def transcribe_audio(audio_file):
        """
        Whisper API yordamida audio faylni matnga o'giradi.
        Til avtomatik aniqlanadi (o'zbek, rus, ingliz tillarni qo'llab-quvvatlaydi).
        """
        client = get_openai_client()
        
        # Vaqtinchalik faylni saqlash
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp_voice")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Audio kengaytmasini aniqlash (default webm)
        ext = "webm"
        if audio_file.name:
            name_parts = audio_file.name.rsplit(".", 1)
            if len(name_parts) > 1:
                ext = name_parts[-1].lower()
            
        temp_filename = f"transcribe_{uuid.uuid4().hex}.{ext}"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        try:
            with open(temp_path, "wb+") as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)
            
            # Audio fayl o'lchamini tekshirish
            file_size = os.path.getsize(temp_path)
            if file_size < 500:
                raise ValueError(f"Audio fayl juda kichik ({file_size} bayt). Iltimos qayta urinib ko'ring.")
            
            # Whisper orqali transkripsiya qilish (til avtomatik aniqlanadi)
            with open(temp_path, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    # language parametri ko'rsatilmaydi - Whisper o'zi aniqlaydi
                    # (o'zbek, rus, ingliz va 98+ til qo'llab-quvvatlanadi)
                )
            
            return transcription.text
        except ValueError as e:
            print(f"STT Validation Error: {str(e)}")
            raise e
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
        client = get_openai_client()
        
        voice_dir = os.path.join(settings.MEDIA_ROOT, "voice_responses")
        os.makedirs(voice_dir, exist_ok=True)
        
        filename = f"voice_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(voice_dir, filename)
        
        try:
            # OpenAI TTS chaqiruvi
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice_type,  # alloy, echo, fable, onyx, nova, shimmer
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
