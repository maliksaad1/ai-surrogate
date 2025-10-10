import google.generativeai as genai
from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime
import google.generativeai as genai

from app.core.config import GEMINI_API_KEY, DEFAULT_MODEL_TEMPERATURE, MAX_RESPONSE_LENGTH

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.temperature = DEFAULT_MODEL_TEMPERATURE

    async def generate_chat_response(self, message: str, context: Optional[str] = None, memory: Optional[str] = None) -> str:
        """Generate a chat response using Gemini AI"""
        try:
            result = await self.generate_response(message, context, memory)
            return result["content"]
        except Exception as e:
            print(f"Error generating chat response: {e}")
            return "I'm sorry, I'm having trouble processing your message right now. Could you please try again?"

    async def generate_response(self, message: str, context: Optional[str] = None, user_memory: Optional[str] = None) -> Dict[str, Any]:
        """Generate AI response using Gemini"""
        try:
            # Build context prompt
            system_prompt = """You are an AI Surrogate - a compassionate, intelligent companion designed to provide emotional support, engaging conversation, and helpful assistance. 

Your personality traits:
- Empathetic and understanding
- Supportive but not overly sentimental
- Curious and engaging
- Helpful and informative
- Maintains appropriate boundaries

Guidelines:
- Keep responses conversational and natural
- Show genuine interest in the user's wellbeing
- Provide helpful information when requested
- Be emotionally supportive during difficult times
- Maintain a positive, encouraging tone
- Keep responses under 150 words unless specifically asked for more detail

"""

            prompt_parts = [system_prompt]
            
            if user_memory:
                prompt_parts.append(f"User context and memory: {user_memory}")
            
            if context:
                prompt_parts.append(f"Recent conversation context: {context}")
            
            prompt_parts.append(f"User message: {message}")
            prompt_parts.append("Respond as the AI Surrogate:")

            full_prompt = "\n\n".join(prompt_parts)

            # Generate response
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=MAX_RESPONSE_LENGTH
                )
            )

            if response.text:
                # Analyze emotion/sentiment of the response
                emotion = await self.analyze_emotion(response.text)
                
                return {
                    "content": response.text.strip(),
                    "emotion": emotion,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                raise Exception("No response generated")

        except Exception as e:
            print(f"Error generating AI response: {e}")
            return {
                "content": "I'm sorry, I'm having trouble processing your message right now. Could you please try again?",
                "emotion": "neutral",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def analyze_emotion(self, text: str) -> str:
        """Analyze emotion/sentiment of text"""
        try:
            emotion_prompt = f"""Analyze the emotional tone of this message and return only one word from this list: happy, sad, neutral, excited, concerned, supportive, curious, thoughtful.

Message: "{text}"

Emotion:"""

            response = await asyncio.to_thread(
                self.model.generate_content,
                emotion_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=10
                )
            )

            if response.text:
                emotion = response.text.strip().lower()
                valid_emotions = ["happy", "sad", "neutral", "excited", "concerned", "supportive", "curious", "thoughtful"]
                return emotion if emotion in valid_emotions else "neutral"
            
            return "neutral"

        except Exception as e:
            print(f"Error analyzing emotion: {e}")
            return "neutral"

    async def summarize_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Summarize conversation for memory storage"""
        try:
            if not messages:
                return ""

            # Format messages for summarization
            conversation_text = []
            for msg in messages[-10:]:  # Last 10 messages
                role = "User" if msg.get("role") == "user" else "AI"
                content = msg.get("content", "")
                conversation_text.append(f"{role}: {content}")

            conversation = "\n".join(conversation_text)

            summary_prompt = f"""Summarize this conversation focusing on:
1. Key topics discussed
2. User's interests, preferences, or concerns mentioned
3. Important context for future conversations
4. User's emotional state or mood

Keep the summary concise but informative (under 200 words).

Conversation:
{conversation}

Summary:"""

            response = await asyncio.to_thread(
                self.model.generate_content,
                summary_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=250
                )
            )

            return response.text.strip() if response.text else ""

        except Exception as e:
            print(f"Error summarizing conversation: {e}")
            return ""

# Global AI service instance
ai_service = AIService()