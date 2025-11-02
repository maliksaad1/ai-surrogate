import os
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY") 
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Gemini AI configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gmail configuration for Communication Agent
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")  # Your Gmail address
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # Gmail app password (not regular password)

# Google Calendar configuration
GOOGLE_CALENDAR_CREDENTIALS = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")  # Path to credentials JSON

# Backend configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# File upload settings
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/wav", "audio/m4a", "audio/mp3"]

# AI settings
DEFAULT_MODEL_TEMPERATURE = 0.7
MAX_CONTEXT_LENGTH = 4000
MAX_RESPONSE_LENGTH = 1000