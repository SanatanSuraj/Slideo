from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId

class FinalPresentationBase(BaseModel):
    """Base model for final presentation"""
    presentation_id: str = Field(..., description="Original presentation ID")
    user_id: str = Field(..., description="User ID who owns this presentation")
    title: str = Field(..., description="Presentation title")
    description: Optional[str] = Field(None, description="Presentation description")
    template_id: Optional[str] = Field(None, description="Template ID used")
    
    # Complete presentation data
    slides: Dict[str, Any] = Field(..., description="Complete slides data with all content")
    layout: Dict[str, Any] = Field(..., description="Layout configuration")
    structure: Dict[str, Any] = Field(..., description="Presentation structure")
    outlines: Dict[str, Any] = Field(..., description="Presentation outlines")
    
    # Metadata
    total_slides: int = Field(..., description="Total number of slides")
    language: str = Field(default="en", description="Presentation language")
    export_format: str = Field(default="pptx", description="Export format")
    
    # URLs and files
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail image URL")
    s3_pptx_url: Optional[str] = Field(None, description="S3 URL for PPTX file")
    s3_pdf_url: Optional[str] = Field(None, description="S3 URL for PDF file")
    
    # Status
    is_published: bool = Field(default=False, description="Whether presentation is published")
    is_complete: bool = Field(default=True, description="Whether presentation is fully generated")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class FinalPresentationCreate(FinalPresentationBase):
    """Model for creating a final presentation"""
    pass

class FinalPresentationUpdate(BaseModel):
    """Model for updating a final presentation"""
    title: Optional[str] = None
    description: Optional[str] = None
    slides: Optional[Dict[str, Any]] = None
    layout: Optional[Dict[str, Any]] = None
    structure: Optional[Dict[str, Any]] = None
    outlines: Optional[Dict[str, Any]] = None
    thumbnail_url: Optional[str] = None
    s3_pptx_url: Optional[str] = None
    s3_pdf_url: Optional[str] = None
    is_published: Optional[bool] = None
    is_complete: Optional[bool] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class FinalPresentationInDB(FinalPresentationBase):
    """Model for final presentation in database"""
    id: str = Field(..., alias="_id")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class FinalPresentation(FinalPresentationBase):
    """Model for final presentation response"""
    id: str
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
