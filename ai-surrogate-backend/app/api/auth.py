from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt

from app.models.schemas import AuthRequest, AuthResponse, User
from app.core.database import supabase

router = APIRouter()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        user_response = supabase.auth.get_user(token)
        if user_response.user:
            return user_response.user
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login")
async def login(auth_data: AuthRequest):
    """Login user with email and password"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": auth_data.email,
            "password": auth_data.password
        })
        
        if response.user and response.session:
            # Get user profile from users table
            user_profile = supabase.table("users").select("*").eq("id", response.user.id).single()
            
            return {
                "access_token": response.session.access_token,
                "token_type": "bearer",
                "user": user_profile.data if user_profile.data else response.user
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/register")
async def register(auth_data: AuthRequest):
    """Register new user"""
    try:
        # Sign up user
        response = supabase.auth.sign_up({
            "email": auth_data.email,
            "password": auth_data.password
        })
        
        if response.user:
            # Create user profile
            user_data = {
                "id": response.user.id,
                "email": auth_data.email,
                "preferences": {}
            }
            
            profile_response = supabase.table("users").insert(user_data).execute()
            
            return {
                "message": "User registered successfully",
                "user_id": response.user.id,
                "email_confirmation_sent": True
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create user")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user"""
    try:
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Logout failed")

@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    try:
        user_profile = supabase.table("users").select("*").eq("id", current_user.id).single()
        
        if user_profile.data:
            return user_profile.data
        else:
            # Create profile if it doesn't exist
            user_data = {
                "id": current_user.id,
                "email": current_user.email,
                "preferences": {}
            }
            
            profile_response = supabase.table("users").insert(user_data).execute()
            return profile_response.data[0] if profile_response.data else user_data
            
    except Exception as e:
        raise HTTPException(status_code=404, detail="User profile not found")

@router.put("/me")
async def update_user_profile(user_data: dict, current_user: dict = Depends(get_current_user)):
    """Update current user profile"""
    try:
        # Filter allowed fields
        allowed_fields = ["name", "preferences"]
        update_data = {k: v for k, v in user_data.items() if k in allowed_fields}
        
        response = supabase.table("users").update(update_data).eq("id", current_user.id).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))