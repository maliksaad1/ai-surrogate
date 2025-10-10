from fastapi import APIRouter, HTTPException, Depends
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from datetime import datetime

from app.models.schemas import ChatRequest, ChatResponse, MessageCreate, Message
from app.core.database import supabase
from app.api.auth import get_current_user
from app.services.voice_service import voice_service
# Use our custom agent orchestrator
from app.agents.simple_orchestrator import agent_orchestrator

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send a text message and get AI response"""
    try:
        # Verify thread ownership
        thread_check = supabase.table("threads").select("id").eq("id", chat_request.thread_id).eq("user_id", current_user.id).single()
        
        if not thread_check.data:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Save user message
        user_message = {
            "thread_id": chat_request.thread_id,
            "role": "user",
            "content": chat_request.message
        }
        
        user_msg_response = supabase.table("messages").insert(user_message).execute()
        
        if not user_msg_response.data:
            raise HTTPException(status_code=400, detail="Failed to save user message")
        
        # Get conversation context (last 10 messages)
        recent_messages = supabase.table("messages").select("role, content").eq("thread_id", chat_request.thread_id).order("created_at", desc=True).limit(10).execute()
        
        context = ""
        if recent_messages.data:
            context_messages = []
            for msg in reversed(recent_messages.data):
                role = "User" if msg["role"] == "user" else "AI"
                context_messages.append(f"{role}: {msg['content']}")
            context = "\n".join(context_messages)
        
        # Get user memory for context
        memory_response = supabase.table("memory").select("summary, context").eq("user_id", current_user.id).order("created_at", desc=True).limit(3).execute()
        
        memory_context = ""
        if memory_response.data:
            memory_summaries = [mem["summary"] for mem in memory_response.data if mem["summary"]]
            memory_context = "\n".join(memory_summaries)
        
        # Generate AI response using our custom agent orchestrator
        try:
            # First, let's test if the orchestrator is working
            if supabase is None:
                ai_response = "Hello! I'm your AI Surrogate companion. I'm working properly now and ready to chat with you!"
                emotion = "friendly"
                metadata = {"test_mode": True}
            else:
                ai_result = await agent_orchestrator.process_message(
                    message=chat_request.message,
                    user_id=current_user.get("id", "anonymous"),
                    thread_id=chat_request.thread_id,
                    context=context,
                    memory=memory_context
                )
                
                ai_response = ai_result["response"]
                emotion = ai_result["emotion"]
                metadata = ai_result["metadata"]
            
        except Exception as ai_error:
            print(f"Agent orchestrator error: {ai_error}")
            # Fallback to simple response
            ai_response = f"I understand your message: '{chat_request.message}'. I'm here to help and chat with you! [Error: {str(ai_error)}]"
            emotion = "neutral"
            metadata = {"fallback": True, "error": str(ai_error)}
        
        # Generate voice response if requested
        audio_url = None
        if chat_request.voice_mode:
            try:
                audio_url = await voice_service.text_to_speech(ai_response)
            except Exception as e:
                print(f"TTS generation failed: {e}")
                # Continue without audio
        
        # Save AI response
        ai_message = {
            "thread_id": chat_request.thread_id,
            "role": "assistant",
            "content": ai_response,
            "emotion": emotion,
            "audio_url": audio_url,
            "metadata": metadata
        }
        
        ai_msg_response = supabase.table("messages").insert(ai_message).execute()
        
        if not ai_msg_response.data:
            raise HTTPException(status_code=400, detail="Failed to save AI response")
        
        # Update thread last_message_at
        supabase.table("threads").update({
            "last_message_at": datetime.utcnow().isoformat()
        }).eq("id", chat_request.thread_id).execute()
        
        return ChatResponse(
            message=ai_response,
            emotion=emotion,
            audio_url=audio_url,
            thread_id=chat_request.thread_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{thread_id}/messages", response_model=List[Message])
async def get_messages(
    thread_id: str,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get messages for a specific thread"""
    try:
        # Verify thread ownership
        thread_check = supabase.table("threads").select("id").eq("id", thread_id).eq("user_id", current_user.id).single()
        
        if not thread_check.data:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Get messages
        response = supabase.table("messages").select("*").eq("thread_id", thread_id).order("created_at", desc=False).range(offset, offset + limit - 1).execute()
        
        return response.data or []
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{thread_id}/messages/{message_id}")
async def delete_message(
    thread_id: str,
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a specific message"""
    try:
        # Verify thread ownership
        thread_check = supabase.table("threads").select("id").eq("id", thread_id).eq("user_id", current_user.id).single()
        
        if not thread_check.data:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Verify message exists in thread
        message_check = supabase.table("messages").select("id").eq("id", message_id).eq("thread_id", thread_id).single()
        
        if not message_check.data:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Delete message
        delete_response = supabase.table("messages").delete().eq("id", message_id).execute()
        
        return {"message": "Message deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{thread_id}/summarize")
async def summarize_conversation(
    thread_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Summarize conversation for memory storage"""
    try:
        # Verify thread ownership
        thread_check = supabase.table("threads").select("id").eq("id", thread_id).eq("user_id", current_user.id).single()
        
        if not thread_check.data:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Get all messages from thread
        messages_response = supabase.table("messages").select("role, content, created_at").eq("thread_id", thread_id).order("created_at", desc=False).execute()
        
        if not messages_response.data:
            raise HTTPException(status_code=400, detail="No messages to summarize")
        
        # Import AI service for summarization
        from app.services.ai_service import ai_service
        
        # Generate summary
        summary = await ai_service.summarize_conversation(messages_response.data)
        
        if summary:
            # Save to memory
            memory_data = {
                "user_id": current_user.id,
                "summary": summary,
                "context": f"Thread: {thread_id}",
                "importance_score": 5  # Default importance
            }
            
            memory_response = supabase.table("memory").insert(memory_data).execute()
            
            return {
                "summary": summary,
                "memory_saved": bool(memory_response.data)
            }
        else:
            return {
                "summary": "Unable to generate summary",
                "memory_saved": False
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))