from supabase import create_client, Client
from app.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
import os

# Create Supabase client with error handling for deployment
try:
    # Try to create client for production
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
except Exception as e:
    print(f"Warning: Supabase client initialization failed: {e}")
    # Create a mock client for deployment testing
    supabase = None

async def get_user_from_token(token: str):
    """Get user from JWT token"""
    try:
        user = supabase.auth.get_user(token)
        return user
    except Exception as e:
        print(f"Error getting user from token: {e}")
        return None

async def verify_user_access(user_id: str, resource_user_id: str) -> bool:
    """Verify user has access to resource"""
    return user_id == resource_user_id