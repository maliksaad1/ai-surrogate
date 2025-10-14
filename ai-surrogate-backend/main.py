from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import route modules
from app.api import auth, chat, voice, threads, memory

# Create FastAPI instance
app = FastAPI(
    title="AI Surrogate Backend",
    description="Backend API for AI Surrogate mobile app",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(voice.router, prefix="/voice", tags=["voice"])
app.include_router(threads.router, prefix="/threads", tags=["threads"])
app.include_router(memory.router, prefix="/memory", tags=["memory"])

@app.get("/")
async def root():
    return {"message": "AI Surrogate Backend API", "version": "1.0.3", "status": "ready for AI responses", "timestamp": "2025-01-09"}

@app.get("/test-ai")
async def test_ai():
    """Test endpoint to verify AI functionality"""
    try:
        from app.agents.simple_orchestrator import agent_orchestrator
        
        result = await agent_orchestrator.process_message(
            message="Hello, test message",
            user_id="test-user",
            thread_id="test-thread",
            context=None,
            memory=None
        )
        
        return {
            "status": "AI system working",
            "test_response": result["response"][:100] + "...",
            "emotion": result["emotion"],
            "agent_used": result.get("agent_used", "unknown")
        }
    except Exception as e:
        return {
            "status": "AI system error",
            "error": str(e),
            "fallback": "Using basic responses"
        }

@app.get("/health")
async def health_check():
    """Health check with configuration status"""
    import os
    
    config_status = {
        "supabase_url": "set" if os.getenv("SUPABASE_URL") else "missing",
        "supabase_anon_key": "set" if os.getenv("SUPABASE_ANON_KEY") else "missing",
        "gemini_api_key": "set" if os.getenv("GEMINI_API_KEY") else "missing",
    }
    
    all_configured = all(status == "set" for status in config_status.values())
    
    return {
        "status": "healthy",
        "message": "API is running",
        "configuration": config_status,
        "fully_configured": all_configured
    }

@app.get("/debug-ai")
async def debug_ai():
    """Detailed AI service diagnostic"""
    import os
    from app.services.ai_service import ai_service
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    diagnostic = {
        "gemini_key_present": bool(gemini_key),
        "gemini_key_length": len(gemini_key) if gemini_key else 0,
        "gemini_key_first_10": gemini_key[:10] if gemini_key else "None",
        "gemini_key_is_placeholder": gemini_key == "your-gemini-api-key-here" if gemini_key else False,
        "ai_service_configured": ai_service.configured if hasattr(ai_service, 'configured') else False,
        "ai_service_has_model": bool(ai_service.model) if hasattr(ai_service, 'model') else False,
    }
    
    return diagnostic

@app.get("/list-models")
async def list_models():
    """List available Gemini models"""
    import os
    import google.generativeai as genai
    
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            return {"error": "GEMINI_API_KEY not set"}
        
        # Configure
        genai.configure(api_key=api_key)
        
        # List all available models
        models = []
        for m in genai.list_models():
            models.append({
                "name": m.name,
                "display_name": m.display_name,
                "description": m.description[:100] if m.description else "",
                "supported_methods": m.supported_generation_methods
            })
        
        return {
            "status": "success",
            "models": models
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/test-gemini-direct")
async def test_gemini_direct():
    """Direct Gemini API test"""
    import os
    import google.generativeai as genai
    
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            return {"error": "GEMINI_API_KEY not set"}
        
        # Configure and test
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Simple test prompt
        response = model.generate_content("Say hello in one sentence")
        
        return {
            "status": "success",
            "response": response.text,
            "api_key_length": len(api_key),
            "model": "gemini-flash-latest"
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Disable reload in production
    )