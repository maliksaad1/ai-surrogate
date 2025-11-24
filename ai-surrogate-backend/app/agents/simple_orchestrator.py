from typing import Dict, Any, List, Optional, Callable
import json
import asyncio
from datetime import datetime
import google.generativeai as genai
from enum import Enum

from app.core.config import GEMINI_API_KEY
from app.services.ai_service import ai_service
from app.agents.tool_agent import communication_agent, scheduler_agent_enhanced

class AgentStatus(Enum):
    """Agent execution status for visual feedback"""
    IDLE = "idle"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    COMPLETING = "completing"
    COMPLETE = "complete"
    ERROR = "error"

class AgentType:
    CHAT = "chat"
from typing import Dict, Any, List, Optional, Callable
import json
import asyncio
from datetime import datetime
import google.generativeai as genai
from enum import Enum

from app.core.config import GEMINI_API_KEY
from app.services.ai_service import ai_service
from app.agents.tool_agent import communication_agent, scheduler_agent_enhanced

class AgentStatus(Enum):
    """Agent execution status for visual feedback"""
    IDLE = "idle"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    COMPLETING = "completing"
    COMPLETE = "complete"
    ERROR = "error"

class AgentType:
    CHAT = "chat"
    EMOTION = "emotion"
    MEMORY = "memory"
    SCHEDULER = "scheduler"
    DOCS = "docs"
    COMMUNICATION = "communication"  # New tool-enabled agent

from app.services.mcp_service import mcp_service

class SimpleAgentOrchestrator:
    """
    Enhanced agent orchestrator with visual status tracking and MCP-like concepts.
    Shows which agent is working and provides real-time execution feedback.
    """
    
    def __init__(self):
        self.agents = {
            AgentType.CHAT: ChatAgent(),
            AgentType.EMOTION: EmotionAgent(),
            AgentType.MEMORY: MemoryAgent(),
            AgentType.SCHEDULER: scheduler_agent_enhanced,  # Use enhanced scheduler with tools
            AgentType.DOCS: DocsAgent(),
            AgentType.COMMUNICATION: communication_agent,  # New communication agent with tools
        }
        self.status_callback = None  # For real-time status updates
        self.execution_log = []  # Track agent execution history
        
        # Initialize MCP service
        # Note: In a real app, this should be awaited in startup event
        # For this script, we'll initialize lazily or rely on service self-initialization
    
    async def process_message(
        self, 
        message: str, 
        user_id: str, 
        thread_id: str, 
        context: Optional[str] = None,
        memory: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user message with enhanced visibility and MCP-like tool calling
        """
        # Ensure MCP service is initialized
        await mcp_service.initialize()
        
        execution_trace = []  # Track all agent executions
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Analyze message intent and route to primary agent
            self._log_status("orchestrator", AgentStatus.ANALYZING, "Routing message to appropriate agent")
            execution_trace.append({"step": "routing", "status": "started", "time": datetime.utcnow().isoformat()})
            
            primary_agent = await self._route_message(message)
            
            execution_trace.append({
                "step": "routing", 
                "status": "complete", 
                "agent_selected": primary_agent,
                "time": datetime.utcnow().isoformat()
            })
            
            # Step 2: Execute primary agent with status tracking
            self._log_status(primary_agent, AgentStatus.PROCESSING, f"{primary_agent.title()} agent is processing your request")
            execution_trace.append({
                "step": "primary_agent", 
                "agent": primary_agent,
                "status": "processing",
                "time": datetime.utcnow().isoformat()
            })
            
            primary_response = await self.agents[primary_agent].process(
                message=message,
                context=context,
                memory=memory,
                user_id=user_id,
                thread_id=thread_id
            )
            
            execution_trace.append({
                "step": "primary_agent",
                "agent": primary_agent,
                "status": "complete",
                "confidence": primary_response.get("confidence", 0.8),
                "time": datetime.utcnow().isoformat()
            })
            
            # Step 3: Parallel agent execution (MCP-like tool calling)
            self._log_status("orchestrator", AgentStatus.PROCESSING, "Running emotion and memory agents")
            
            # Execute emotion and memory agents in parallel
            emotion_task = asyncio.create_task(
                self._execute_with_tracking(AgentType.EMOTION, "analyze_emotion", primary_response["content"])
            )
            
            memory_task = asyncio.create_task(
                self._execute_with_tracking(
                    AgentType.MEMORY, 
                    "should_update_memory", 
                    message, 
                    primary_response["content"]
                )
            )
            
            # Wait for parallel tasks
            emotion_result, memory_result = await asyncio.gather(emotion_task, memory_task)
            
            emotion = emotion_result["result"]
            memory_update = memory_result["result"]
            
            execution_trace.extend([emotion_result["trace"], memory_result["trace"]])
            
            # Step 4: Update memory if needed
            if memory_update:
                self._log_status(AgentType.MEMORY, AgentStatus.PROCESSING, "Updating memory")
                execution_trace.append({
                    "step": "memory_update",
                    "status": "processing",
                    "importance": memory_update.get("importance", 3),
                    "time": datetime.utcnow().isoformat()
                })
                
                await self.agents[AgentType.MEMORY].update_memory(
                    user_id=user_id,
                    conversation_summary=f"User: {message}\nAI: {primary_response['content']}",
                    importance_score=memory_update.get("importance", 3)
                )
                
                execution_trace.append({
                    "step": "memory_update",
                    "status": "complete",
                    "time": datetime.utcnow().isoformat()
                })
            
            # Calculate total processing time
            end_time = datetime.utcnow()
            total_time = (end_time - start_time).total_seconds()
            
            self._log_status("orchestrator", AgentStatus.COMPLETE, "Response generated successfully")
            
            # Return enhanced response with full execution trace
            return {
                "response": primary_response["content"],
                "emotion": emotion,
                "agent_used": primary_agent,
                "agent_display_name": self._get_agent_display_name(primary_agent),
                "agent_icon": self._get_agent_icon(primary_agent),
                "metadata": {
                    "memory_updated": bool(memory_update),
                    "processing_time": total_time,
                    "primary_agent_time": primary_response.get("processing_time"),
                    "confidence": primary_response.get("confidence", 0.8),
                    "execution_trace": execution_trace,
                    "agents_involved": self._get_agents_involved(execution_trace)
                }
            }
            
        except Exception as e:
            print(f"Error in agent orchestration: {e}")
            self._log_status("orchestrator", AgentStatus.ERROR, f"Error: {str(e)}")
            
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
                "agent_display_name": "Fallback Agent",
                "agent_icon": "⚠️",
                "metadata": {
                    "error": str(e),
                    "execution_trace": execution_trace
                }
            }
    
    async def shutdown(self):
        """Cleanup resources"""
        await mcp_service.shutdown()

    async def _route_message(self, message: str) -> str:
        """
        Analyze message content to determine which agent should handle it.
        Now includes Communication agent for email/messaging.
        """
        try:
            # Use simple keyword-based routing with optional AI enhancement
            message_lower = message.lower()
            
            # Communication keywords (NEW - highest priority for tool usage)
            communication_keywords = [
                "send email", "email", "send message to", "write email", "compose email",
                "check email", "inbox", "message", "notify", "tell"
            ]
            
            # Schedule-related keywords  
            schedule_keywords = [
                "schedule", "calendar", "appointment", "meeting", "reminder",
                "tomorrow", "today", "next week", "plan", "time", "date", "book",
                "what do i have", "upcoming"
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
            
            # Check for keyword matches (priority order matters!)
            if any(keyword in message_lower for keyword in communication_keywords):
                return AgentType.COMMUNICATION  # Use tool-enabled communication agent
            elif any(keyword in message_lower for keyword in schedule_keywords):
                return AgentType.SCHEDULER  # Use tool-enabled scheduler agent
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
    
    async def _execute_with_tracking(self, agent_type: str, method_name: str, *args) -> Dict[str, Any]:
        """Execute agent method with execution tracking"""
        start_time = datetime.utcnow()
        self._log_status(agent_type, AgentStatus.PROCESSING, f"Executing {method_name}")
        
        try:
            agent = self.agents[agent_type]
            method = getattr(agent, method_name)
            result = await method(*args)
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self._log_status(agent_type, AgentStatus.COMPLETE, f"{method_name} complete")
            
            return {
                "result": result,
                "trace": {
                    "agent": agent_type,
                    "method": method_name,
                    "status": "complete",
                    "execution_time": execution_time,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                }
            }
        except Exception as e:
            self._log_status(agent_type, AgentStatus.ERROR, f"Error in {method_name}: {str(e)}")
            return {
                "result": None,
                "trace": {
                    "agent": agent_type,
                    "method": method_name,
                    "status": "error",
                    "error": str(e),
                    "time": datetime.utcnow().isoformat()
                }
            }
    
    def _log_status(self, agent: str, status: AgentStatus, message: str):
        """Log agent status for tracking and debugging"""
        log_entry = {
            "agent": agent,
            "status": status.value,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.execution_log.append(log_entry)
        print(f"[{agent.upper()}] {status.value}: {message}")
        
        # Call status callback if registered (for real-time updates)
        if self.status_callback:
            self.status_callback(log_entry)
    
    def _get_agent_display_name(self, agent_type: str) -> str:
        """Get human-readable agent name"""
        names = {
            AgentType.CHAT: "Chat Assistant",
            AgentType.EMOTION: "Emotion Analyzer",
            AgentType.MEMORY: "Memory Manager",
            AgentType.SCHEDULER: "Schedule Assistant",
            AgentType.DOCS: "Knowledge Assistant",
            AgentType.COMMUNICATION: "Communication Agent"  # NEW
        }
        return names.get(agent_type, "Unknown Agent")
    
    def _get_agent_icon(self, agent_type: str) -> str:
        """Get emoji icon for agent type"""
        icons = {
            AgentType.CHAT: "💬",
            AgentType.EMOTION: "😊",
            AgentType.MEMORY: "🧠",
            AgentType.SCHEDULER: "📅",
            AgentType.DOCS: "📚",
            AgentType.COMMUNICATION: "📧"  # NEW
        }
        return icons.get(agent_type, "🤖")
    
    def _get_agents_involved(self, execution_trace: List[Dict[str, Any]]) -> List[str]:
        """Extract list of all agents involved in execution"""
        agents = set()
        for trace in execution_trace:
            if "agent" in trace:
                agents.add(trace["agent"])
        return list(agents)
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get full execution log for debugging"""
        return self.execution_log.copy()
    
    def clear_execution_log(self):
        """Clear execution log"""
        self.execution_log.clear()

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