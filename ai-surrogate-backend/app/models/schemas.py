from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    email: str
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = {}
    created_at: datetime
    updated_at: datetime

class ThreadBase(BaseModel):
    title: str

class ThreadCreate(ThreadBase):
    user_id: str

class Thread(ThreadBase):
    id: str
    user_id: str
    last_message_at: datetime
    created_at: datetime
    updated_at: datetime

class MessageBase(BaseModel):
    content: str
    role: str  # 'user' or 'assistant'

class MessageCreate(MessageBase):
    thread_id: str
    emotion: Optional[str] = None
    audio_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class Message(MessageBase):
    id: str
    thread_id: str
    emotion: Optional[str] = None
    audio_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    created_at: datetime

class ChatRequest(BaseModel):
    thread_id: str
    message: str
    user_id: str
    voice_mode: Optional[bool] = False

class ChatResponse(BaseModel):
    message: str
    emotion: Optional[str] = None
    audio_url: Optional[str] = None
    thread_id: str

class VoiceRequest(BaseModel):
    thread_id: str
    user_id: str

class MemoryBase(BaseModel):
    summary: str
    context: Optional[str] = None
    importance_score: Optional[int] = 1

class MemoryCreate(MemoryBase):
    user_id: str

class Memory(MemoryBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

class AuthRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: User