from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class EventType(str, Enum):
    WORKSHOP = "workshop"
    CONFERENCE = "conference"
    SOCIAL = "social"
    SPORTS = "sports"
    CULTURAL = "cultural"
    TECH = "tech"
    SEMINAR = "seminar"
    COMPETITION = "competition"

class Tone(str, Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    ENTHUSIASTIC = "enthusiastic"
    INFORMATIVE = "informative"
    FUN = "fun"

class Theme(str, Enum):
    CYBERPUNK = "cyberpunk"
    ELEGANT = "elegant"
    MINIMALISTIC = "minimalistic"
    VIBRANT = "vibrant"
    PROFESSIONAL = "professional"
    NATURE = "nature"
    ARTISTIC = "artistic"

# Request Schemas
class EmailGenerationRequest(BaseModel):
    event_name: str = Field(..., min_length=1, description="Name of the event")
    event_type: EventType = Field(..., description="Type of event")
    date: str = Field(..., description="Event date")
    time: str = Field(..., description="Event time")
    venue: str = Field(..., description="Event venue")
    target_audience: str = Field(..., description="Target audience")
    tone: Tone = Field(Tone.FORMAL, description="Tone of the email")
    key_points: List[str] = Field(default_factory=list, description="Key points to highlight")
    contact_info: Optional[str] = Field(None, description="Contact information")
    organizer_name: Optional[str] = Field(None, description="Organizer name")

class PosterGenerationRequest(BaseModel):
    event_name: str = Field(..., min_length=1, description="Name of the event")
    event_type: EventType = Field(..., description="Type of event")
    date: str = Field(..., description="Event date")
    time: str = Field(..., description="Event time")
    venue: str = Field(..., description="Event venue")
    theme: Theme = Field(Theme.PROFESSIONAL, description="Design theme")
    color_scheme: Optional[str] = Field(None, description="Preferred color scheme")
    additional_instructions: Optional[str] = Field(None, description="Additional design instructions")

class InvitationGenerationRequest(BaseModel):
    event_name: str = Field(..., min_length=1, description="Name of the event")
    event_type: EventType = Field(..., description="Type of event")
    date: str = Field(..., description="Event date")
    time: str = Field(..., description="Event time")
    venue: str = Field(..., description="Event venue")
    rsvp_deadline: Optional[str] = Field(None, description="RSVP deadline")
    rsvp_email: Optional[str] = Field(None, description="RSVP email address")
    dress_code: Optional[str] = Field(None, description="Dress code")
    special_instructions: Optional[str] = Field(None, description="Special instructions")

# Response Schemas
class EmailGenerationResponse(BaseModel):
    subject: str
    body: str
    status: str = "success"
    model_used: str = "llama-3.1-70b"

class PosterGenerationResponse(BaseModel):
    image_url: str
    prompt_used: str
    status: str = "success"
    model_used: str = "stable-diffusion"

class InvitationGenerationResponse(BaseModel):
    invitation_text: str
    qr_code_url: Optional[str] = None
    status: str = "success"
    model_used: str = "llama-3.1-70b"

class ErrorResponse(BaseModel):
    detail: str
    status: str = "error"

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str