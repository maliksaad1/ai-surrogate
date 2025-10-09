from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
import asyncio
from datetime import datetime

from app.services.ai_service import ai_service

class AgentState(TypedDict):
    message: str
    user_id: str
    thread_id: str
    context: Optional[str]
    memory: Optional[str]
    agent_type: str
    response: Optional[str]
    emotion: Optional[str]
    metadata: Dict[str, Any]

class AgentOrchestrator:
    def __init__(self):
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the agent workflow graph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("router", self._route_message)
        workflow.add_node("chat_agent", self._chat_agent)
        workflow.add_node("emotion_agent", self._emotion_agent)
        workflow.add_node("docs_agent", self._docs_agent)
        workflow.add_node("schedule_agent", self._schedule_agent)
        workflow.add_node("finalizer", self._finalize_response)
        
        # Add edges
        workflow.set_entry_point("router")
        
        # Router decides which agent to use
        workflow.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "chat": "chat_agent",
                "emotion": "emotion_agent", 
                "docs": "docs_agent",
                "schedule": "schedule_agent"
            }
        )
        
        # All agents go to emotion analysis
        workflow.add_edge("chat_agent", "emotion_agent")
        workflow.add_edge("docs_agent", "emotion_agent")
        workflow.add_edge("schedule_agent", "emotion_agent")
        
        # Emotion agent goes to finalizer
        workflow.add_edge("emotion_agent", "finalizer")
        workflow.add_edge("finalizer", END)
        
        return workflow.compile()

    async def _route_message(self, state: AgentState) -> AgentState:
        """Route message to appropriate agent"""
        message = state["message"].lower()
        
        # Simple keyword-based routing (can be enhanced with ML classification)
        if any(word in message for word in ["document", "file", "pdf", "write", "create", "summary"]):
            agent_type = "docs"
        elif any(word in message for word in ["schedule", "reminder", "task", "todo", "calendar", "appointment"]):
            agent_type = "schedule"
        elif any(word in message for word in ["sad", "happy", "angry", "frustrated", "excited", "worried", "anxious"]):
            agent_type = "emotion"
        else:
            agent_type = "chat"
            
        state["agent_type"] = agent_type
        return state

    def _route_decision(self, state: AgentState) -> str:
        """Decision function for routing"""
        return state["agent_type"]

    async def _chat_agent(self, state: AgentState) -> AgentState:
        """Handle general chat conversations"""
        try:
            response_data = await ai_service.generate_response(
                message=state["message"],
                context=state.get("context"),
                user_memory=state.get("memory")
            )
            
            state["response"] = response_data["content"]
            state["emotion"] = response_data["emotion"]
            state["metadata"]["agent"] = "chat"
            
        except Exception as e:
            state["response"] = "I'm sorry, I encountered an error processing your message. Please try again."
            state["emotion"] = "neutral"
            
        return state

    async def _emotion_agent(self, state: AgentState) -> AgentState:
        """Analyze and respond to emotional content"""
        try:
            if state.get("response"):
                # If we already have a response, just analyze its emotion
                emotion = await ai_service.analyze_emotion(state["response"])
                state["emotion"] = emotion
            else:
                # Generate emotionally aware response
                emotion_prompt = f"""The user seems to be expressing emotion in their message. 
                Respond with empathy and emotional intelligence. 
                
                User message: {state['message']}
                
                Provide a compassionate, supportive response that acknowledges their feelings."""
                
                response_data = await ai_service.generate_response(
                    message=emotion_prompt,
                    context=state.get("context"),
                    user_memory=state.get("memory")
                )
                
                state["response"] = response_data["content"]
                state["emotion"] = response_data["emotion"]
                
            state["metadata"]["emotional_support"] = True
            
        except Exception as e:
            if not state.get("response"):
                state["response"] = "I understand you're going through something. I'm here to listen and support you."
                state["emotion"] = "supportive"
                
        return state

    async def _docs_agent(self, state: AgentState) -> AgentState:
        """Handle document-related tasks"""
        try:
            docs_prompt = f"""The user is asking about documents or wants help with document-related tasks.
            
            User message: {state['message']}
            
            Provide helpful guidance about document management, creation, or summarization. 
            If they want to create something, guide them through the process."""
            
            response_data = await ai_service.generate_response(
                message=docs_prompt,
                context=state.get("context"),
                user_memory=state.get("memory")
            )
            
            state["response"] = response_data["content"]
            state["metadata"]["agent"] = "docs"
            state["metadata"]["document_task"] = True
            
        except Exception as e:
            state["response"] = "I can help you with document-related tasks. Could you please be more specific about what you'd like to do?"
            
        return state

    async def _schedule_agent(self, state: AgentState) -> AgentState:
        """Handle scheduling and task management"""
        try:
            schedule_prompt = f"""The user is asking about scheduling, tasks, or time management.
            
            User message: {state['message']}
            
            Provide helpful guidance about organization, scheduling, or task management. 
            If they want to set reminders or create tasks, guide them through the process."""
            
            response_data = await ai_service.generate_response(
                message=schedule_prompt,
                context=state.get("context"),
                user_memory=state.get("memory")
            )
            
            state["response"] = response_data["content"]
            state["metadata"]["agent"] = "schedule"
            state["metadata"]["schedule_task"] = True
            
        except Exception as e:
            state["response"] = "I can help you with scheduling and task management. What would you like to organize?"
            
        return state

    async def _finalize_response(self, state: AgentState) -> AgentState:
        """Finalize the response and add metadata"""
        state["metadata"]["processed_at"] = datetime.utcnow().isoformat()
        state["metadata"]["final_emotion"] = state.get("emotion", "neutral")
        
        return state

    async def process_message(self, message: str, user_id: str, thread_id: str, context: Optional[str] = None, memory: Optional[str] = None) -> Dict[str, Any]:
        """Process a message through the agent system"""
        try:
            initial_state = AgentState(
                message=message,
                user_id=user_id,
                thread_id=thread_id,
                context=context,
                memory=memory,
                agent_type="",
                response=None,
                emotion=None,
                metadata={}
            )
            
            # Run the workflow
            final_state = await self.graph.ainvoke(initial_state)
            
            return {
                "response": final_state["response"],
                "emotion": final_state["emotion"],
                "metadata": final_state["metadata"]
            }
            
        except Exception as e:
            print(f"Error in agent orchestrator: {e}")
            return {
                "response": "I apologize, but I'm experiencing some technical difficulties. Please try again in a moment.",
                "emotion": "neutral",
                "metadata": {"error": True, "agent": "fallback"}
            }

# Global orchestrator instance
agent_orchestrator = AgentOrchestrator()