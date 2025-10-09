# import whisper  # Temporarily disabled for deployment
from gtts import gTTS
import tempfile
import os
import asyncio
from typing import Optional
import aiofiles
# from mutagen import File as MutagenFile  # Temporarily disabled

from app.core.config import ALLOWED_AUDIO_TYPES, MAX_FILE_SIZE
from app.core.database import supabase

class VoiceService:
    def __init__(self):
        # Whisper model loading temporarily disabled for deployment
        # self.whisper_model = whisper.load_model("base")
        pass

    async def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio file to text using Whisper (temporarily disabled)"""
        try:
            # Temporary placeholder - return indicating voice was received
            # TODO: Re-enable Whisper after deployment dependencies are resolved
            return "[Voice message received - STT temporarily disabled for deployment]"
            
            # Original Whisper code (commented out for deployment):
            # result = await asyncio.to_thread(
            #     self.whisper_model.transcribe,
            #     audio_file_path,
            #     language="en"
            # )
            # return result["text"].strip()
            
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            raise Exception("Failed to transcribe audio")

    async def text_to_speech(self, text: str, language: str = "en") -> str:
        """Convert text to speech using gTTS and upload to Supabase storage"""
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_path = temp_file.name

            # Generate speech
            tts = gTTS(text=text, lang=language, slow=False)
            await asyncio.to_thread(tts.save, temp_path)

            # Upload to Supabase storage
            audio_url = await self._upload_audio_to_storage(temp_path, "tts")
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return audio_url
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            raise Exception("Failed to generate speech")

    async def _upload_audio_to_storage(self, file_path: str, folder: str = "audio") -> str:
        """Upload audio file to Supabase storage and return public URL"""
        try:
            # Generate unique filename
            import uuid
            filename = f"{folder}/{uuid.uuid4()}.mp3"
            
            # Read file
            async with aiofiles.open(file_path, 'rb') as f:
                file_data = await f.read()
            
            # Upload to Supabase storage
            response = supabase.storage.from_("audio").upload(filename, file_data)
            
            if response:
                # Get public URL
                public_url = supabase.storage.from_("audio").get_public_url(filename)
                return public_url
            else:
                raise Exception("Failed to upload to storage")
                
        except Exception as e:
            print(f"Error uploading audio: {e}")
            raise Exception("Failed to upload audio file")

    async def validate_audio_file(self, file_path: str, max_size: int = MAX_FILE_SIZE) -> bool:
        """Validate audio file format and size (simplified for deployment)"""
        try:
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > max_size:
                raise Exception(f"File too large. Maximum size is {max_size/1024/1024}MB")
            
            # Simplified validation - just check if file exists and has reasonable size
            # TODO: Re-enable mutagen validation after deployment
            # audio_file = MutagenFile(file_path)
            # if audio_file is None:
            #     raise Exception("Invalid audio file format")
            
            return True
            
        except Exception as e:
            print(f"Audio validation error: {e}")
            return False

    async def process_voice_message(self, audio_file_path: str, user_id: str, thread_id: str) -> dict:
        """Process voice message: transcribe and prepare for AI response"""
        try:
            # Validate audio file
            if not await self.validate_audio_file(audio_file_path):
                raise Exception("Invalid audio file")
            
            # Transcribe audio
            transcribed_text = await self.transcribe_audio(audio_file_path)
            
            if not transcribed_text:
                raise Exception("Could not transcribe audio")
            
            # Upload original audio to storage
            audio_url = await self._upload_audio_to_storage(audio_file_path, "user_audio")
            
            return {
                "transcribed_text": transcribed_text,
                "audio_url": audio_url,
                "success": True
            }
            
        except Exception as e:
            print(f"Error processing voice message: {e}")
            return {
                "transcribed_text": "",
                "audio_url": None,
                "success": False,
                "error": str(e)
            }

# Global voice service instance
voice_service = VoiceService()