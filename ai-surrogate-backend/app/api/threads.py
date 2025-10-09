from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime

from app.models.schemas import Thread, ThreadCreate, ThreadBase
from app.core.database import supabase
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Thread])
async def get_user_threads(current_user: dict = Depends(get_current_user)):
    """Get all threads for the current user"""
    try:
        response = supabase.table("threads").select("""
            *,
            messages(content, created_at)
        """).eq("user_id", current_user.id).order("last_message_at", desc=True).execute()
        
        return response.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Thread)
async def create_thread(thread_data: ThreadBase, current_user: dict = Depends(get_current_user)):
    """Create a new thread for the current user"""
    try:
        new_thread = {
            "user_id": current_user.id,
            "title": thread_data.title,
            "last_message_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("threads").insert(new_thread).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(status_code=400, detail="Failed to create thread")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{thread_id}", response_model=Thread)
async def get_thread(thread_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific thread by ID"""
    try:
        response = supabase.table("threads").select("*").eq("id", thread_id).eq("user_id", current_user.id).single()
        
        if response.data:
            return response.data
        else:
            raise HTTPException(status_code=404, detail="Thread not found")
            
    except Exception as e:
        raise HTTPException(status_code=404, detail="Thread not found")

@router.put("/{thread_id}", response_model=Thread)
async def update_thread(thread_id: str, thread_data: ThreadBase, current_user: dict = Depends(get_current_user)):
    """Update a thread"""
    try:
        # Verify thread ownership
        thread_check = supabase.table("threads").select("id").eq("id", thread_id).eq("user_id", current_user.id).single()
        
        if not thread_check.data:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        update_data = {
            "title": thread_data.title,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("threads").update(update_data).eq("id", thread_id).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(status_code=400, detail="Failed to update thread")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{thread_id}")
async def delete_thread(thread_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a thread and all its messages"""
    try:
        # Verify thread ownership
        thread_check = supabase.table("threads").select("id").eq("id", thread_id).eq("user_id", current_user.id).single()
        
        if not thread_check.data:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Delete thread (messages will be cascade deleted due to foreign key)
        response = supabase.table("threads").delete().eq("id", thread_id).execute()
        
        return {"message": "Thread deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{thread_id}/messages")
async def get_thread_messages(thread_id: str, current_user: dict = Depends(get_current_user)):
    """Get all messages for a specific thread"""
    try:
        # Verify thread ownership
        thread_check = supabase.table("threads").select("id").eq("id", thread_id).eq("user_id", current_user.id).single()
        
        if not thread_check.data:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        response = supabase.table("messages").select("*").eq("thread_id", thread_id).order("created_at", desc=False).execute()
        
        return response.data or []
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))