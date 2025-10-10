from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import Optional
import tempfile
import os
import aiofiles

from app.models.schemas import VoiceRequest
from app.services.voice_service import voice_service
from app.core.database import supabase
from app.api.auth import get_current_user

router = APIRouter()

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    thread_id: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Transcribe audio file to text"""
    try:
        # Validate file type
        if file.content_type not in ["audio/mpeg", "audio/wav", "audio/m4a", "audio/mp3", "audio/webm"]:
            raise HTTPException(status_code=400, detail="Unsupported audio format")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_path = temp_file.name
            
        # Save uploaded file
        async with aiofiles.open(temp_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        try:
            # Process voice message
            result = await voice_service.process_voice_message(
                audio_file_path=temp_path,
                user_id=current_user.id,
                thread_id=thread_id
            )
            
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result.get("error", "Failed to process audio"))
            
            return {
                "transcribed_text": result["transcribed_text"],
                "audio_url": result["audio_url"]
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/speak")
async def text_to_speech(
    text: str = Form(...),
    language: str = Form("en"),
    current_user: dict = Depends(get_current_user)
):
    """Convert text to speech"""
    try:
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(text) > 1000:
            raise HTTPException(status_code=400, detail="Text too long. Maximum 1000 characters.")
        
        # Generate speech
        audio_url = await voice_service.text_to_speech(text, language)
        
        return {
            "audio_url": audio_url,
            "text": text,
            "language": language
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate speech: {str(e)}")

@router.post("/process")
async def process_voice_message(
    file: UploadFile = File(...),
    thread_id: str = Form(...),
    voice_response: bool = Form(True),
    current_user: dict = Depends(get_current_user)
):
    """Process complete voice message flow: transcribe → AI response → TTS"""
    try:
        # Validate thread ownership
        thread_check = supabase.table("threads").select("id").eq("id", thread_id).eq("user_id", current_user.id).single()
        if not thread_check.data:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_path = temp_file.name
            
        # Save uploaded file
        async with aiofiles.open(temp_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        try:
            # Process voice message
            voice_result = await voice_service.process_voice_message(
                audio_file_path=temp_path,
                user_id=current_user.id,
                thread_id=thread_id
            )
            
            if not voice_result["success"]:
                raise HTTPException(status_code=400, detail=voice_result.get("error", "Failed to process audio"))
            
            transcribed_text = voice_result["transcribed_text"]
            user_audio_url = voice_result["audio_url"]
            
            # Save user message to database
            user_message = {
                "thread_id": thread_id,
                "role": "user",
                "content": transcribed_text,
                "audio_url": user_audio_url
            }
            
            message_response = supabase.table("messages").insert(user_message).execute()
            
            # Import here to avoid circular imports
            from app.agents.simple_orchestrator import agent_orchestrator
            
            # Generate AI response using orchestrator
            ai_result = await agent_orchestrator.process_message(
                message=transcribed_text,
                user_id=current_user["id"] if "id" in current_user else "anonymous",
                thread_id=thread_id,
                context="",  # Voice context can be added later
                memory=""   # Voice memory can be added later
            )
            
            ai_response = ai_result["response"]
            emotion = ai_result["emotion"]
            
            # Generate AI speech if requested
            ai_audio_url = None
            if voice_response:
                ai_audio_url = await voice_service.text_to_speech(ai_response)
            
            # Save AI message to database
            ai_message = {
                "thread_id": thread_id,
                "role": "assistant",
                "content": ai_response,
                "emotion": emotion,
                "audio_url": ai_audio_url,
                "metadata": ai_result.get("metadata", {})
            }
            
            ai_message_response = supabase.table("messages").insert(ai_message).execute()
            
            return {
                "user_message": {
                    "text": transcribed_text,
                    "audio_url": user_audio_url
                },
                "ai_response": {
                    "text": ai_response,
                    "audio_url": ai_audio_url,
                    "emotion": emotion
                },
                "thread_id": thread_id
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/test")
async def test_voice_service():
    """Test endpoint for voice service"""
    try:
        # Test TTS
        test_audio_url = await voice_service.text_to_speech("Hello, this is a test of the voice service.")
        
        return {
            "status": "Voice service is working",
            "test_audio_url": test_audio_url
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice service test failed: {str(e)}")