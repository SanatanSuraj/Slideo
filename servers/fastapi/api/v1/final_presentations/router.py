from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from models.mongo.final_presentation import FinalPresentation, FinalPresentationCreate, FinalPresentationUpdate
from crud.final_presentation_crud import final_presentation_crud
from auth.dependencies import get_current_active_user
from models.mongo.user import User

FINAL_PRESENTATION_ROUTER = APIRouter()

@FINAL_PRESENTATION_ROUTER.post("/create", response_model=FinalPresentation)
async def create_final_presentation(
    final_presentation: FinalPresentationCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new final presentation"""
    try:
        # Set user ID to current user
        final_presentation.user_id = current_user.id
        
        final_presentation_id = await final_presentation_crud.create_final_presentation(final_presentation)
        created_final_presentation = await final_presentation_crud.get_final_presentation_by_id(final_presentation_id)
        
        if not created_final_presentation:
            raise HTTPException(status_code=500, detail="Failed to create final presentation")
        
        return created_final_presentation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create final presentation: {str(e)}")

@FINAL_PRESENTATION_ROUTER.get("/{final_presentation_id}", response_model=FinalPresentation)
async def get_final_presentation(
    final_presentation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a final presentation by ID"""
    final_presentation = await final_presentation_crud.get_final_presentation_by_id(final_presentation_id)
    if not final_presentation:
        raise HTTPException(status_code=404, detail="Final presentation not found")
    
    if final_presentation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return final_presentation

@FINAL_PRESENTATION_ROUTER.get("/by-presentation/{presentation_id}", response_model=FinalPresentation)
async def get_final_presentation_by_presentation_id(
    presentation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get final presentation by original presentation ID"""
    final_presentation = await final_presentation_crud.get_final_presentation_by_presentation_id(presentation_id)
    if not final_presentation:
        raise HTTPException(status_code=404, detail="Final presentation not found")
    
    if final_presentation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return final_presentation

@FINAL_PRESENTATION_ROUTER.get("/", response_model=List[FinalPresentation])
async def list_final_presentations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    """List final presentations for the current user"""
    return await final_presentation_crud.get_final_presentations_by_user(
        current_user.id, skip=skip, limit=limit
    )

@FINAL_PRESENTATION_ROUTER.put("/{final_presentation_id}", response_model=FinalPresentation)
async def update_final_presentation(
    final_presentation_id: str,
    final_presentation_update: FinalPresentationUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a final presentation"""
    # Check if the final presentation exists and user owns it
    existing_final_presentation = await final_presentation_crud.get_final_presentation_by_id(final_presentation_id)
    if not existing_final_presentation:
        raise HTTPException(status_code=404, detail="Final presentation not found")
    
    if existing_final_presentation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    updated_final_presentation = await final_presentation_crud.update_final_presentation(
        final_presentation_id, final_presentation_update
    )
    return updated_final_presentation

@FINAL_PRESENTATION_ROUTER.delete("/{final_presentation_id}")
async def delete_final_presentation(
    final_presentation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a final presentation"""
    # Check if the final presentation exists and user owns it
    existing_final_presentation = await final_presentation_crud.get_final_presentation_by_id(final_presentation_id)
    if not existing_final_presentation:
        raise HTTPException(status_code=404, detail="Final presentation not found")
    
    if existing_final_presentation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = await final_presentation_crud.delete_final_presentation(final_presentation_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete final presentation")
    
    return {"message": "Final presentation deleted successfully"}

@FINAL_PRESENTATION_ROUTER.get("/search/", response_model=List[FinalPresentation])
async def search_final_presentations(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    """Search final presentations by title or description"""
    return await final_presentation_crud.search_final_presentations(
        current_user.id, query, skip=skip, limit=limit
    )

@FINAL_PRESENTATION_ROUTER.get("/published/", response_model=List[FinalPresentation])
async def get_published_final_presentations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get published final presentations (public endpoint)"""
    return await final_presentation_crud.get_published_final_presentations(skip=skip, limit=limit)

# Test endpoints without authentication
@FINAL_PRESENTATION_ROUTER.get("/test/by-presentation/{presentation_id}")
async def test_get_final_presentation_by_presentation_id(presentation_id: str):
    """Test endpoint to get final presentation by original presentation ID without authentication"""
    try:
        final_presentation = await final_presentation_crud.get_final_presentation_by_presentation_id(presentation_id)
        if not final_presentation:
            return {"found": False, "message": "No final presentation found"}
        return {"found": True, "data": final_presentation}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@FINAL_PRESENTATION_ROUTER.post("/test/manual-save/{presentation_id}")
async def test_manual_save_presentation_to_final_presentations(presentation_id: str):
    """Test endpoint to manually save a presentation to final_presentations collection"""
    try:
        from crud.presentation_crud import presentation_crud
        from crud.slide_crud import slide_crud
        from models.mongo.final_presentation import FinalPresentationCreate
        from bson import ObjectId
        
        # Get the presentation
        presentation = await presentation_crud.get_presentation_by_id(presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Check if already saved
        existing_final_presentation = await final_presentation_crud.get_final_presentation_by_presentation_id(presentation_id)
        if existing_final_presentation:
            return {"message": "Presentation already saved as final presentation", "final_presentation_id": existing_final_presentation.id}
        
        # Get all slides for this presentation
        slides = await slide_crud.get_slides_by_presentation(presentation_id)
        if not slides:
            raise HTTPException(status_code=400, detail="No slides found for this presentation")
        
        # Prepare slides data for storage
        slides_data = {
            "slides": [slide.model_dump() for slide in slides],
            "total_slides": len(slides),
            "export_format": "pptx"
        }
        
        # Ensure all slides have proper IDs
        for slide_data in slides_data["slides"]:
            if not slide_data.get("id"):
                slide_data["id"] = str(ObjectId())
        
        # Create final presentation record
        final_presentation_data = FinalPresentationCreate(
            presentation_id=presentation_id,
            user_id=presentation.user_id,
            title=presentation.title or "Untitled Presentation",
            description=f"Final presentation generated from {presentation_id}",
            template_id=presentation.layout.get("id") if presentation.layout else None,
            slides=slides_data,
            layout=presentation.layout or {},
            structure=presentation.structure or {},
            outlines=presentation.outlines or {},
            total_slides=len(slides),
            language=presentation.language or "en",
            export_format="pptx",
            thumbnail_url=None,
            s3_pptx_url=None,
            s3_pdf_url=None,
            is_published=False,
            is_complete=True
        )
        
        final_presentation_id = await final_presentation_crud.create_final_presentation(final_presentation_data)
        
        return {
            "message": "Presentation successfully saved to final_presentations",
            "presentation_id": presentation_id,
            "final_presentation_id": final_presentation_id,
            "slides_count": len(slides)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save presentation: {str(e)}")
