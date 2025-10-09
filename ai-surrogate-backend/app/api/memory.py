from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.models.schemas import Memory, MemoryCreate, MemoryBase
from app.core.database import supabase
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Memory])
async def get_user_memories(
    limit: Optional[int] = 20,
    importance_threshold: Optional[int] = 1,
    current_user: dict = Depends(get_current_user)
):
    """Get user's memories filtered by importance"""
    try:
        query = supabase.table("memory").select("*").eq("user_id", current_user.id)
        
        if importance_threshold:
            query = query.gte("importance_score", importance_threshold)
        
        response = query.order("created_at", desc=True).limit(limit).execute()
        
        return response.data or []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Memory)
async def create_memory(
    memory_data: MemoryBase,
    current_user: dict = Depends(get_current_user)
):
    """Create a new memory entry"""
    try:
        new_memory = {
            "user_id": current_user.id,
            "summary": memory_data.summary,
            "context": memory_data.context,
            "importance_score": memory_data.importance_score or 1
        }
        
        response = supabase.table("memory").insert(new_memory).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(status_code=400, detail="Failed to create memory")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{memory_id}", response_model=Memory)
async def update_memory(
    memory_id: str,
    memory_data: MemoryBase,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing memory"""
    try:
        # Verify memory ownership
        memory_check = supabase.table("memory").select("id").eq("id", memory_id).eq("user_id", current_user.id).single()
        
        if not memory_check.data:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        update_data = {
            "summary": memory_data.summary,
            "context": memory_data.context,
            "importance_score": memory_data.importance_score or 1,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("memory").update(update_data).eq("id", memory_id).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(status_code=400, detail="Failed to update memory")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a memory"""
    try:
        # Verify memory ownership
        memory_check = supabase.table("memory").select("id").eq("id", memory_id).eq("user_id", current_user.id).single()
        
        if not memory_check.data:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        response = supabase.table("memory").delete().eq("id", memory_id).execute()
        
        return {"message": "Memory deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/analyze")
async def analyze_user_patterns(
    days_back: Optional[int] = 30,
    current_user: dict = Depends(get_current_user)
):
    """Analyze user conversation patterns and emotional trends"""
    try:
        # Get date threshold
        threshold_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
        
        # Get recent messages with emotions
        messages_response = supabase.table("messages").select("""
            emotion, created_at, role, content,
            threads!inner(user_id)
        """).eq("threads.user_id", current_user.id).gte("created_at", threshold_date).execute()
        
        if not messages_response.data:
            return {
                "message": "Not enough data for analysis",
                "analysis": {}
            }
        
        # Analyze emotions
        emotions = {}
        message_count = 0
        ai_message_count = 0
        
        for msg in messages_response.data:
            if msg["role"] == "assistant" and msg.get("emotion"):
                emotion = msg["emotion"]
                emotions[emotion] = emotions.get(emotion, 0) + 1
                ai_message_count += 1
            message_count += 1
        
        # Calculate patterns
        most_common_emotion = max(emotions, key=emotions.get) if emotions else "neutral"
        emotion_diversity = len(emotions)
        avg_messages_per_day = message_count / days_back if days_back > 0 else 0
        
        # Get conversation topics from memories
        memory_response = supabase.table("memory").select("summary").eq("user_id", current_user.id).gte("created_at", threshold_date).execute()
        
        topics = []
        if memory_response.data:
            topics = [mem["summary"][:50] + "..." for mem in memory_response.data[:5]]
        
        analysis = {
            "time_period_days": days_back,
            "total_messages": message_count,
            "ai_messages": ai_message_count,
            "avg_messages_per_day": round(avg_messages_per_day, 2),
            "emotional_patterns": {
                "most_common_emotion": most_common_emotion,
                "emotion_distribution": emotions,
                "emotion_diversity_score": emotion_diversity
            },
            "conversation_topics": topics,
            "engagement_level": "high" if avg_messages_per_day > 5 else "medium" if avg_messages_per_day > 2 else "low"
        }
        
        return {
            "message": "Analysis completed",
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/consolidate")
async def consolidate_memories(
    current_user: dict = Depends(get_current_user)
):
    """Consolidate old memories to reduce storage and improve relevance"""
    try:
        # Get old memories (older than 30 days)
        threshold_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        
        old_memories = supabase.table("memory").select("*").eq("user_id", current_user.id).lt("created_at", threshold_date).order("importance_score", desc=False).execute()
        
        if not old_memories.data or len(old_memories.data) < 5:
            return {
                "message": "Not enough old memories to consolidate",
                "consolidated": 0
            }
        
        # Import AI service for consolidation
        from app.services.ai_service import ai_service
        
        # Group memories by importance and consolidate low-importance ones
        low_importance_memories = [mem for mem in old_memories.data if mem["importance_score"] <= 3]
        
        if len(low_importance_memories) >= 3:
            # Create consolidated summary
            summaries = [mem["summary"] for mem in low_importance_memories[:10]]  # Max 10 to avoid token limits
            consolidated_text = " ".join(summaries)
            
            consolidation_prompt = f"""Consolidate these memory summaries into a single, comprehensive summary that captures the most important information:

{consolidated_text}

Create a consolidated summary:"""
            
            try:
                # Generate consolidated summary (you would use ai_service here)
                consolidated_summary = f"Consolidated memory from {len(low_importance_memories)} entries: {consolidated_text[:200]}..."
                
                # Create new consolidated memory
                consolidated_memory = {
                    "user_id": current_user.id,
                    "summary": consolidated_summary,
                    "context": f"Consolidated from {len(low_importance_memories)} memories",
                    "importance_score": 4  # Medium importance for consolidated memories
                }
                
                supabase.table("memory").insert(consolidated_memory).execute()
                
                # Delete old low-importance memories
                memory_ids_to_delete = [mem["id"] for mem in low_importance_memories]
                for mem_id in memory_ids_to_delete[:5]:  # Delete max 5 at a time to be safe
                    supabase.table("memory").delete().eq("id", mem_id).execute()
                
                return {
                    "message": "Memories consolidated successfully",
                    "consolidated": min(5, len(memory_ids_to_delete)),
                    "new_memory_id": consolidated_memory
                }
                
            except Exception as e:
                print(f"Error in consolidation: {e}")
                return {
                    "message": "Consolidation failed",
                    "consolidated": 0
                }
        
        return {
            "message": "No memories needed consolidation",
            "consolidated": 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_memories(
    query: str,
    limit: Optional[int] = 10,
    current_user: dict = Depends(get_current_user)
):
    """Search through user memories"""
    try:
        if not query or len(query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
        
        # Simple text search in memories (can be enhanced with vector search)
        response = supabase.table("memory").select("*").eq("user_id", current_user.id).ilike("summary", f"%{query}%").order("importance_score", desc=True).limit(limit).execute()
        
        return {
            "query": query,
            "results": response.data or [],
            "count": len(response.data) if response.data else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))