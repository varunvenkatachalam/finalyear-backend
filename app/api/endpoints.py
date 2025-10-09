from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import json

from ..models.schemas import (
    EmailGenerationRequest, EmailGenerationResponse,
    PosterGenerationRequest, PosterGenerationResponse,
    InvitationGenerationRequest, InvitationGenerationResponse,
    HealthResponse, ErrorResponse
)
from .ai_services import ai_service
from ..models.database import get_db, GenerationHistory

router = APIRouter()

@router.post("/generate-email", response_model=EmailGenerationResponse)
async def generate_email(
    request: EmailGenerationRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate email content for event"""
    try:
        result = ai_service.generate_email_content(request.dict())
        
        # Store in history (in background)
        background_tasks.add_task(
            store_generation_history,
            db, 
            "email", 
            request.dict(), 
            result
        )
        
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email generation failed: {str(e)}")

@router.post("/generate-poster", response_model=PosterGenerationResponse)
async def generate_poster(
    request: PosterGenerationRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate event poster"""
    try:
        result = ai_service.generate_poster(request.dict())
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Poster generation failed"))
        
        # Store in history (in background)
        background_tasks.add_task(
            store_generation_history,
            db, 
            "poster", 
            request.dict(), 
            {"prompt_used": result["prompt_used"], "model_used": result["model_used"]}
        )
        
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Poster generation failed: {str(e)}")

@router.post("/generate-invitation", response_model=InvitationGenerationResponse)
async def generate_invitation(
    request: InvitationGenerationRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate invitation with QR code"""
    try:
        result = ai_service.generate_invitation(request.dict())
        
        # Store in history (in background)
        background_tasks.add_task(
            store_generation_history,
            db, 
            "invitation", 
            request.dict(), 
            {"invitation_text": result["invitation_text"], "has_qr": bool(result["qr_code_url"])}
        )
        
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invitation generation failed: {str(e)}")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "Event AI Generator",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/models/status")
async def models_status():
    """Check AI models status"""
    groq_status = "available" if ai_service.groq_client else "unavailable"
    
    return {
        "groq_llama": groq_status,
        "stable_diffusion": "huggingface-api",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/test/email")
async def test_email_generation():
    """Test endpoint for email generation"""
    test_data = {
        "event_name": "Annual Tech Fest 2024",
        "event_type": "conference",
        "date": "March 15, 2024",
        "time": "9:00 AM - 5:00 PM",
        "venue": "College Main Auditorium",
        "target_audience": "Students and Faculty",
        "tone": "enthusiastic",
        "key_points": ["AI Workshops", "Industry Expert Talks", "Hackathon", "Networking Session"],
        "contact_info": "techfest@college.edu",
        "organizer_name": "Computer Science Department"
    }
    
    try:
        result = ai_service.generate_email_content(test_data)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

def store_generation_history(db: Session, gen_type: str, input_data: dict, output_data: dict):
    """Store generation history in database"""
    try:
        # Convert output_data to JSON-serializable format
        if output_data is None:
            output_data_json = None
        else:
            # Remove image_url from poster output to avoid large data storage
            if gen_type == "poster" and "image_url" in output_data:
                output_data_copy = output_data.copy()
                output_data_copy["image_url"] = "[BASE64_IMAGE_DATA]"
                output_data_json = output_data_copy
            else:
                output_data_json = output_data
        
        history_entry = GenerationHistory(
            generation_type=gen_type,
            input_data=input_data,
            output_data=output_data_json
        )
        db.add(history_entry)
        db.commit()
        print(f"✅ Successfully stored {gen_type} generation history")
    except Exception as e:
        print(f"❌ Failed to store generation history: {e}")
        db.rollback()

@router.get("/history")
async def get_generation_history(db: Session = Depends(get_db)):
    """Get generation history (for debugging)"""
    try:
        history = db.query(GenerationHistory).order_by(GenerationHistory.created_at.desc()).limit(10).all()
        return {
            "count": len(history),
            "history": [
                {
                    "id": item.id,
                    "type": item.generation_type,
                    "input": item.input_data,
                    "output": item.output_data,
                    "created_at": item.created_at.isoformat()
                }
                for item in history
            ]
        }
    except Exception as e:
        return {"error": f"Failed to fetch history: {e}"}