from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi import APIRouter, HTTPException, Depends
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
        if supabase is None:
            # Mock user for deployment testing
            return {"id": "test-user", "email": "test@example.com"}
        
        token = credentials.credentials
        user_response = supabase.auth.get_user(token)
        if user_response.user:
            # Convert User object to dict
            return {
                "id": user_response.user.id,
                "email": user_response.user.email,
                "aud": getattr(user_response.user, 'aud', None),
                "role": getattr(user_response.user, 'role', None),
                "created_at": getattr(user_response.user, 'created_at', None),
            }
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
        if supabase is None:
            # Mock registration for deployment testing
            return {
                "message": "User registered successfully (mock)",
                "user_id": "test-user-id",
                "email_confirmation_sent": True
            }
        
        # Sign up user
        response = supabase.auth.sign_up({
            "email": auth_data.email,
            "password": auth_data.password
        })
        
        if response.user:
            # Try to create user profile, but don't fail if RLS blocks it
            try:
                user_data = {
                    "id": response.user.id,
                    "email": auth_data.email,
                    "preferences": {}
                }
                
                profile_response = supabase.table("users").insert(user_data).execute()
            except Exception as profile_error:
                print(f"Profile creation failed (will retry later): {profile_error}")
                # Don't fail registration if profile creation fails due to RLS
                pass
            
            return {
                "message": "User registered successfully",
                "user_id": response.user.id,
                "email_confirmation_sent": True
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create user")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/confirm")
async def confirm_email(token: str = None, type: str = None):
    """Handle email confirmation"""
    try:
        if not token:
            return {"message": "Email confirmation token is required"}
        
        if supabase is None:
            return {"message": "Email confirmed successfully (mock)"}
        
        # Verify the email confirmation token
        response = supabase.auth.verify_otp({
            "token_hash": token,
            "type": "email"
        })
        
        if response.user:
            # Try to create user profile if it doesn't exist
            try:
                user_data = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "preferences": {}
                }
                
                # Check if profile exists
                existing_profile = supabase.table("users").select("id").eq("id", response.user.id).execute()
                
                if not existing_profile.data:
                    # Create profile if it doesn't exist
                    profile_response = supabase.table("users").insert(user_data).execute()
                    
            except Exception as profile_error:
                print(f"Profile creation during confirmation failed: {profile_error}")
                # Don't fail confirmation if profile creation fails
                pass
            
            return {
                "message": "Email confirmed successfully!",
                "user_id": response.user.id,
                "redirect": "Please return to the app to continue"
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid confirmation token")
            
    except Exception as e:
        print(f"Email confirmation error: {e}")
        return {
            "message": "Email confirmation failed. Please try again or contact support.",
            "error": str(e)
        }

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
        user_profile = supabase.table("users").select("*").eq("id", current_user["id"]).execute()
        
        if user_profile.data and len(user_profile.data) > 0:
            return user_profile.data[0]
        else:
            # Create profile if it doesn't exist
            user_data = {
                "id": current_user["id"],
                "email": current_user["email"],
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
        
        response = supabase.table("users").update(update_data).eq("id", current_user["id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))