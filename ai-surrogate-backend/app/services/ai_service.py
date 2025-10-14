import google.generativeai as genai
from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime
import google.generativeai as genai

from app.core.config import GEMINI_API_KEY, DEFAULT_MODEL_TEMPERATURE, MAX_RESPONSE_LENGTH

# Configure Gemini AI with error handling
try:
    if GEMINI_API_KEY and GEMINI_API_KEY != "your-gemini-api-key-here":
        genai.configure(api_key=GEMINI_API_KEY)
        print(f"✓ Gemini AI configured successfully")
    else:
        print(f"⚠ Warning: GEMINI_API_KEY not set or invalid")
except Exception as e:
    print(f"⚠ Warning: Gemini AI configuration failed: {e}")

class AIService:
    def __init__(self):
        try:
            print(f"Initializing AI Service...")
            print(f"GEMINI_API_KEY present: {bool(GEMINI_API_KEY)}")
            print(f"GEMINI_API_KEY length: {len(GEMINI_API_KEY) if GEMINI_API_KEY else 0}")
            
            if GEMINI_API_KEY and GEMINI_API_KEY != "your-gemini-api-key-here" and len(GEMINI_API_KEY) > 20:
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.temperature = DEFAULT_MODEL_TEMPERATURE
                self.configured = True
                print(f"✓ AI Service initialized successfully with Gemini 1.5 Flash")
            else:
                print(f"⚠ AI Service initializing in fallback mode - API key invalid or missing")
                self.model = None
                self.configured = False
        except Exception as e:
            print(f"❌ Warning: AI model initialization failed: {e}")
            import traceback
            traceback.print_exc()
            self.model = None
            self.configured = False

    async def generate_chat_response(self, message: str, context: Optional[str] = None, memory: Optional[str] = None) -> str:
        """Generate a chat response using Gemini AI"""
        try:
            # Check if we have a valid API key
            if not GEMINI_API_KEY or GEMINI_API_KEY == "your-gemini-api-key-here":
                return "Hello! I'm your AI Surrogate companion. I'm currently setting up my AI capabilities. How can I help you today?"
            
            print(f"Generating chat response for: {message[:50]}...")
            result = await self.generate_response(message, context, memory)
            print(f"Got response from generate_response: {result['content'][:50]}...")
            return result["content"]
        except Exception as e:
            print(f"❌ Error in generate_chat_response: {e}")
            import traceback
            traceback.print_exc()
            # Provide a helpful fallback response
            return f"I understand you said: '{message}'. I'm having some technical difficulties right now, but I'm here to listen and help however I can!"

    async def generate_response(self, message: str, context: Optional[str] = None, user_memory: Optional[str] = None) -> Dict[str, Any]:
        """Generate AI response using Gemini"""
        try:
            # Check if AI is properly configured
            if not self.configured or not self.model:
                # Provide intelligent fallback responses
                message_lower = message.lower()
                
                # Greeting responses
                if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
                    return {
                        "content": "Hello! I'm your AI Surrogate companion. I'm here to chat, help you plan your day, answer questions, and provide support. How can I assist you today?",
                        "emotion": "friendly",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                
                # Help/capability questions
                elif any(word in message_lower for word in ["what can you", "help me", "what do you do", "capabilities"]):
                    return {
                        "content": "I'm your AI companion! I can help you with:\n\n• Casual conversation and emotional support\n• Scheduling and time management\n• Answering questions and providing information\n• Remembering important details about our conversations\n• Planning your day\n\nWhat would you like to talk about?",
                        "emotion": "helpful",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                
                # How are you questions
                elif any(word in message_lower for word in ["how are you", "how's it going", "how do you feel"]):
                    return {
                        "content": "I'm doing well, thank you for asking! I'm here and ready to help you with whatever you need. How are you doing today?",
                        "emotion": "friendly",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                
                # Schedule/time related
                elif any(word in message_lower for word in ["schedule", "plan", "today", "tomorrow", "calendar"]):
                    return {
                        "content": f"I'd be happy to help you with your schedule! You mentioned: '{message}'. While my full AI capabilities are being set up, I can still help you think through your planning. What specific scheduling help do you need?",
                        "emotion": "helpful",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                
                # Default friendly response
                else:
                    return {
                        "content": f"I hear you! You said: '{message}'. I'm your AI companion and I'm here to help. While my full AI capabilities are being configured, I can still chat with you! What would you like to talk about?",
                        "emotion": "friendly",
                        "timestamp": datetime.utcnow().isoformat()
                    }

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
            print(f"❌ Error generating AI response: {e}")
            import traceback
            print(f"Full traceback:")
            traceback.print_exc()
            print(f"Model configured: {self.configured}")
            print(f"Model object: {self.model}")
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