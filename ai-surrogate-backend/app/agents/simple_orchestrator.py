from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime
import google.generativeai as genai

from app.core.config import GEMINI_API_KEY
from app.services.ai_service import ai_service

class AgentType:
    CHAT = "chat"
    EMOTION = "emotion"
    MEMORY = "memory"
    SCHEDULER = "scheduler"
    DOCS = "docs"

class SimpleAgentOrchestrator:
    """
    Lightweight agent orchestrator without LangChain dependencies.
    Routes messages to appropriate specialized agents based on content analysis.
    """
    
    def __init__(self):
        self.agents = {
            AgentType.CHAT: ChatAgent(),
            AgentType.EMOTION: EmotionAgent(),
            AgentType.MEMORY: MemoryAgent(),
            AgentType.SCHEDULER: SchedulerAgent(),
            AgentType.DOCS: DocsAgent(),
        }
    
    async def process_message(
        self, 
        message: str, 
        user_id: str, 
        thread_id: str, 
        context: Optional[str] = None,
        memory: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user message by routing to appropriate agents
        """
        try:
            # Step 1: Analyze message intent and route to primary agent
            primary_agent = await self._route_message(message)
            
            # Step 2: Get primary response
            primary_response = await self.agents[primary_agent].process(
                message=message,
                context=context,
                memory=memory,
                user_id=user_id,
                thread_id=thread_id
            )
            
            # Step 3: Analyze emotion in parallel
            emotion_task = asyncio.create_task(
                self.agents[AgentType.EMOTION].analyze_emotion(primary_response["content"])
            )
            
            # Step 4: Check if memory update is needed
            memory_task = asyncio.create_task(
                self.agents[AgentType.MEMORY].should_update_memory(message, primary_response["content"])
            )
            
            # Wait for parallel tasks
            emotion, memory_update = await asyncio.gather(emotion_task, memory_task)
            
            # Step 5: Update memory if needed
            if memory_update:
                await self.agents[AgentType.MEMORY].update_memory(
                    user_id=user_id,
                    conversation_summary=f"User: {message}\nAI: {primary_response['content']}",
                    importance_score=memory_update.get("importance", 3)
                )
            
            return {
                "response": primary_response["content"],
                "emotion": emotion,
                "agent_used": primary_agent,
                "metadata": {
                    "memory_updated": bool(memory_update),
                    "processing_time": primary_response.get("processing_time"),
                    "confidence": primary_response.get("confidence", 0.8)
                }
            }
            
        except Exception as e:
            print(f"Error in agent orchestration: {e}")
            # Fallback to basic chat
            fallback_response = await self.agents[AgentType.CHAT].process(
                message=message,
                context=context,
                memory=memory,
                user_id=user_id,
                thread_id=thread_id
            )
            
            return {
                "response": fallback_response["content"],
                "emotion": "neutral",
                "agent_used": "fallback",
                "metadata": {"error": str(e)}
            }
    
    async def _route_message(self, message: str) -> str:
        """
        Analyze message content to determine which agent should handle it
        """
        try:
            # Use simple keyword-based routing with optional AI enhancement
            message_lower = message.lower()
            
            # Schedule-related keywords
            schedule_keywords = [
                "schedule", "calendar", "appointment", "meeting", "reminder",
                "tomorrow", "today", "next week", "plan", "time", "date"
            ]
            
            # Document/search keywords
            docs_keywords = [
                "search", "find", "lookup", "information", "explain", "what is",
                "how to", "help with", "documentation", "guide"
            ]
            
            # Memory-related keywords
            memory_keywords = [
                "remember", "forget", "recall", "you said", "we talked about",
                "last time", "before", "history"
            ]
            
            # Check for keyword matches
            if any(keyword in message_lower for keyword in schedule_keywords):
                return AgentType.SCHEDULER
            elif any(keyword in message_lower for keyword in docs_keywords):
                return AgentType.DOCS
            elif any(keyword in message_lower for keyword in memory_keywords):
                return AgentType.MEMORY
            else:
                # Default to chat for general conversation
                return AgentType.CHAT
                
        except Exception as e:
            print(f"Error in message routing: {e}")
            return AgentType.CHAT  # Default fallback

class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
    
    async def process(
        self, 
        message: str, 
        context: Optional[str] = None,
        memory: Optional[str] = None,
        user_id: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process message - to be implemented by subclasses"""
        raise NotImplementedError

class ChatAgent(BaseAgent):
    """General conversation agent"""
    
    def __init__(self):
        super().__init__(AgentType.CHAT)
    
    async def process(
        self, 
        message: str, 
        context: Optional[str] = None,
        memory: Optional[str] = None,
        user_id: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate conversational response"""
        try:
            start_time = datetime.utcnow()
            
            # Use the existing AI service for response generation
            response = await ai_service.generate_chat_response(
                message=message,
                context=context,
                memory=memory
            )
            
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            return {
                "content": response,
                "confidence": 0.9,
                "processing_time": processing_time
            }
            
        except Exception as e:
            print(f"Error in ChatAgent: {e}")
            return {
                "content": f"I understand you're saying: '{message}'. I'm here to chat with you!",
                "confidence": 0.5,
                "processing_time": 0.1
            }

class EmotionAgent(BaseAgent):
    """Emotion detection and analysis agent"""
    
    def __init__(self):
        super().__init__(AgentType.EMOTION)
    
    async def analyze_emotion(self, text: str) -> str:
        """Analyze emotion in text"""
        try:
            # Use AI service emotion analysis if available
            if hasattr(ai_service, 'analyze_emotion'):
                return await ai_service.analyze_emotion(text)
            else:
                # Simple keyword-based emotion detection
                text_lower = text.lower()
                
                if any(word in text_lower for word in ["happy", "great", "awesome", "wonderful", "excellent"]):
                    return "happy"
                elif any(word in text_lower for word in ["sad", "sorry", "disappointed", "upset"]):
                    return "sad"
                elif any(word in text_lower for word in ["excited", "amazing", "fantastic", "thrilled"]):
                    return "excited"
                elif any(word in text_lower for word in ["concerned", "worried", "trouble", "problem"]):
                    return "concerned"
                else:
                    return "neutral"
                    
        except Exception as e:
            print(f"Error in emotion analysis: {e}")
            return "neutral"

class MemoryAgent(BaseAgent):
    """Memory management agent"""
    
    def __init__(self):
        super().__init__(AgentType.MEMORY)
    
    async def should_update_memory(self, user_message: str, ai_response: str) -> Optional[Dict[str, Any]]:
        """Determine if conversation should be stored in memory"""
        try:
            # Simple heuristics for memory importance
            important_keywords = [
                "important", "remember", "don't forget", "my name", "birthday",
                "favorite", "prefer", "like", "dislike", "family", "work", "hobby"
            ]
            
            combined_text = f"{user_message} {ai_response}".lower()
            
            # Check for important keywords
            if any(keyword in combined_text for keyword in important_keywords):
                return {"importance": 7, "reason": "Contains important personal information"}
            
            # Long conversations might be worth remembering
            if len(user_message) > 100:
                return {"importance": 4, "reason": "Detailed conversation"}
            
            return None
            
        except Exception as e:
            print(f"Error in memory evaluation: {e}")
            return None
    
    async def update_memory(self, user_id: str, conversation_summary: str, importance_score: int):
        """Update user memory storage"""
        try:
            # Import here to avoid circular imports
            from app.core.database import supabase
            
            if supabase is None:
                print("Supabase not available for memory storage")
                return
            
            memory_data = {
                "user_id": user_id,
                "summary": conversation_summary[:500],  # Limit summary length
                "importance_score": importance_score,
                "context": "agent_orchestrator",
                "created_at": datetime.utcnow().isoformat()
            }
            
            supabase.table("memory").insert(memory_data).execute()
            print(f"Memory updated for user {user_id}")
            
        except Exception as e:
            print(f"Error updating memory: {e}")

class SchedulerAgent(BaseAgent):
    """Scheduling and time-related agent"""
    
    def __init__(self):
        super().__init__(AgentType.SCHEDULER)
    
    async def process(
        self, 
        message: str, 
        context: Optional[str] = None,
        memory: Optional[str] = None,
        user_id: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle scheduling requests"""
        try:
            # Enhanced prompt for scheduling
            scheduling_prompt = f"""You are a helpful scheduling assistant. The user is asking about: "{message}"

Provide helpful responses for scheduling, time management, or calendar-related requests. Be specific and actionable.

Context: {context or 'No previous context'}
User message: {message}

Response:"""
            
            response = await ai_service.generate_chat_response(
                message=scheduling_prompt,
                context=context,
                memory=memory
            )
            
            return {
                "content": response,
                "confidence": 0.8,
                "processing_time": 0.5
            }
            
        except Exception as e:
            print(f"Error in SchedulerAgent: {e}")
            return {
                "content": f"I'd be happy to help you with scheduling! You mentioned: '{message}'. What specific help do you need with your schedule?",
                "confidence": 0.6,
                "processing_time": 0.1
            }

class DocsAgent(BaseAgent):
    """Documentation and information retrieval agent"""
    
    def __init__(self):
        super().__init__(AgentType.DOCS)
    
    async def process(
        self, 
        message: str, 
        context: Optional[str] = None,
        memory: Optional[str] = None,
        user_id: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle information and documentation requests"""
        try:
            # Enhanced prompt for information retrieval
            docs_prompt = f"""You are a knowledgeable assistant helping with information requests. The user is asking: "{message}"

Provide accurate, helpful information. If you're not certain about specific facts, be honest about limitations.

Context: {context or 'No previous context'}
User question: {message}

Helpful response:"""
            
            response = await ai_service.generate_chat_response(
                message=docs_prompt,
                context=context,
                memory=memory
            )
            
            return {
                "content": response,
                "confidence": 0.8,
                "processing_time": 0.6
            }
            
        except Exception as e:
            print(f"Error in DocsAgent: {e}")
            return {
                "content": f"I'd be happy to help you find information about: '{message}'. Let me provide what I can help with!",
                "confidence": 0.6,
                "processing_time": 0.1
            }

# Global orchestrator instance
agent_orchestrator = SimpleAgentOrchestrator()