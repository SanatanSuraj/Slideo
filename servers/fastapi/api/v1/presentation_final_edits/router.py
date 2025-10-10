from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from models.mongo.presentation_final_edit import (
    PresentationFinalEdit, 
    PresentationFinalEditCreate, 
    PresentationFinalEditUpdate
)
from crud.presentation_final_edit_crud import presentation_final_edit_crud
from crud.presentation_crud import presentation_crud
from crud.slide_crud import slide_crud
from models.mongo.user import User
from auth.dependencies import get_current_active_user

PRESENTATION_FINAL_EDIT_ROUTER = APIRouter()

@PRESENTATION_FINAL_EDIT_ROUTER.post("/", response_model=PresentationFinalEdit)
async def create_presentation_final_edit(
    presentation_final_edit: PresentationFinalEditCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new presentation final edit"""
    # Ensure the user_id matches the current user
    presentation_final_edit.user_id = current_user.id
    
    presentation_final_edit_id = await presentation_final_edit_crud.create_presentation_final_edit(presentation_final_edit)
    return await presentation_final_edit_crud.get_presentation_final_edit_by_id(presentation_final_edit_id)

@PRESENTATION_FINAL_EDIT_ROUTER.get("/", response_model=List[PresentationFinalEdit])
async def get_presentation_final_edits(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    """Get presentation final edits for the current user"""
    return await presentation_final_edit_crud.get_presentation_final_edits_by_user(
        current_user.id, skip=skip, limit=limit
    )

@PRESENTATION_FINAL_EDIT_ROUTER.get("/published", response_model=List[PresentationFinalEdit])
async def get_published_presentation_final_edits(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all published presentation final edits (public endpoint)"""
    return await presentation_final_edit_crud.get_published_presentation_final_edits(
        skip=skip, limit=limit
    )

@PRESENTATION_FINAL_EDIT_ROUTER.get("/{presentation_final_edit_id}", response_model=PresentationFinalEdit)
async def get_presentation_final_edit(
    presentation_final_edit_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific presentation final edit by ID"""
    presentation_final_edit = await presentation_final_edit_crud.get_presentation_final_edit_by_id(presentation_final_edit_id)
    if not presentation_final_edit:
        raise HTTPException(status_code=404, detail="Presentation final edit not found")
    
    # Check if user owns this presentation final edit
    if presentation_final_edit.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return presentation_final_edit

@PRESENTATION_FINAL_EDIT_ROUTER.get("/by-presentation/{presentation_id}", response_model=PresentationFinalEdit)
async def get_presentation_final_edit_by_presentation_id(
    presentation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get presentation final edit by presentation ID"""
    presentation_final_edit = await presentation_final_edit_crud.get_presentation_final_edit_by_presentation_id(presentation_id)
    if not presentation_final_edit:
        raise HTTPException(status_code=404, detail="Presentation final edit not found")
    
    # Check if user owns this presentation final edit
    if presentation_final_edit.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return presentation_final_edit

@PRESENTATION_FINAL_EDIT_ROUTER.put("/{presentation_final_edit_id}", response_model=PresentationFinalEdit)
async def update_presentation_final_edit(
    presentation_final_edit_id: str,
    presentation_final_edit_update: PresentationFinalEditUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a presentation final edit"""
    # Check if the presentation final edit exists and user owns it
    existing_presentation_final_edit = await presentation_final_edit_crud.get_presentation_final_edit_by_id(presentation_final_edit_id)
    if not existing_presentation_final_edit:
        raise HTTPException(status_code=404, detail="Presentation final edit not found")
    
    if existing_presentation_final_edit.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    updated_presentation_final_edit = await presentation_final_edit_crud.update_presentation_final_edit(
        presentation_final_edit_id, presentation_final_edit_update
    )
    return updated_presentation_final_edit

@PRESENTATION_FINAL_EDIT_ROUTER.delete("/{presentation_final_edit_id}")
async def delete_presentation_final_edit(
    presentation_final_edit_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a presentation final edit"""
    # Check if the presentation final edit exists and user owns it
    existing_presentation_final_edit = await presentation_final_edit_crud.get_presentation_final_edit_by_id(presentation_final_edit_id)
    if not existing_presentation_final_edit:
        raise HTTPException(status_code=404, detail="Presentation final edit not found")
    
    if existing_presentation_final_edit.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    success = await presentation_final_edit_crud.delete_presentation_final_edit(presentation_final_edit_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete presentation final edit")
    
    return {"message": "Presentation final edit deleted successfully"}

@PRESENTATION_FINAL_EDIT_ROUTER.get("/search/", response_model=List[PresentationFinalEdit])
async def search_presentation_final_edits(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    """Search presentation final edits by title or presentation ID"""
    return await presentation_final_edit_crud.search_presentation_final_edits(
        current_user.id, query, skip=skip, limit=limit
    )

@PRESENTATION_FINAL_EDIT_ROUTER.get("/check/{presentation_id}", response_model=bool)
async def check_presentation_saved(
    presentation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Check if a presentation is already saved as final edit"""
    try:
        existing_final_edit = await presentation_final_edit_crud.get_presentation_final_edit_by_presentation_id(
            presentation_id
        )
        # Check if the final edit exists and belongs to the current user
        return existing_final_edit is not None and existing_final_edit.user_id == current_user.id
    except Exception as e:
        return False

@PRESENTATION_FINAL_EDIT_ROUTER.get("/get/{presentation_id}", response_model=PresentationFinalEdit)
async def get_presentation_final_edit_data(
    presentation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get the final edit data for a presentation"""
    try:
        existing_final_edit = await presentation_final_edit_crud.get_presentation_final_edit_by_presentation_id(
            presentation_id
        )
        if not existing_final_edit:
            raise HTTPException(status_code=404, detail="Final edit not found")
        if existing_final_edit.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        return existing_final_edit
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get final edit: {str(e)}")

@PRESENTATION_FINAL_EDIT_ROUTER.get("/test/{presentation_id}")
async def test_get_presentation_final_edit_data(presentation_id: str):
    """Test endpoint to get final edit data without authentication"""
    try:
        existing_final_edit = await presentation_final_edit_crud.get_presentation_final_edit_by_presentation_id(
            presentation_id
        )
        if not existing_final_edit:
            return {"found": False, "message": "No final edit found"}
        return {"found": True, "data": existing_final_edit}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@PRESENTATION_FINAL_EDIT_ROUTER.post("/manual-save/{presentation_id}")
async def manual_save_presentation_to_final_edits(presentation_id: str):
    """Manually save a presentation to final_edits collection (for testing/debugging)"""
    try:
        from crud.presentation_crud import presentation_crud
        from crud.slide_crud import slide_crud
        from models.mongo.presentation_final_edit import PresentationFinalEditCreate
        from bson import ObjectId
        
        # Get the presentation
        presentation = await presentation_crud.get_presentation_by_id(presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Check if already saved
        existing_final_edit = await presentation_final_edit_crud.get_presentation_final_edit_by_presentation_id(
            presentation_id
        )
        if existing_final_edit:
            return {"message": "Presentation already saved as final edit", "final_edit_id": existing_final_edit.id}
        
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
        
        # Create final edit record
        final_edit_data = PresentationFinalEditCreate(
            presentation_id=presentation_id,
            user_id=presentation.user_id,
            title=presentation.title or "Untitled Presentation",
            template_id=presentation.layout.get("id") if presentation.layout else None,
            slides=slides_data,
            thumbnail_url=None,
            s3_pptx_url=None,
            s3_pdf_url=None,
            is_published=False
        )
        
        final_edit_id = await presentation_final_edit_crud.create_presentation_final_edit(final_edit_data)
        
        return {
            "message": "Presentation successfully saved to final_edits",
            "presentation_id": presentation_id,
            "final_edit_id": final_edit_id,
            "slides_count": len(slides)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save presentation: {str(e)}")

@PRESENTATION_FINAL_EDIT_ROUTER.post("/save", response_model=PresentationFinalEdit)
async def save_presentation_final_edit(
    presentation_id: str = Body(..., description="Presentation ID to save as final edit"),
    current_user: User = Depends(get_current_active_user)
):
    """Save a fully generated presentation to presentation_final_edits collection"""
    try:
        # Get the presentation
        presentation = await presentation_crud.get_presentation_by_id(presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Check if user owns the presentation
        if presentation.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all slides for the presentation
        slides = await slide_crud.get_slides_by_presentation(presentation_id)
        
        if not slides or len(slides) == 0:
            raise HTTPException(status_code=400, detail="No slides found for this presentation")
        
        # Check if presentation is already saved as final edit
        existing_final_edit = await presentation_final_edit_crud.get_presentation_final_edit_by_presentation_id(
            presentation_id
        )
        
        if existing_final_edit:
            # Check if user owns the existing final edit
            if existing_final_edit.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
                
            # Update existing final edit
            slides_data = {
                "slides": [slide.model_dump() for slide in slides],
                "total_slides": len(slides),
                "export_format": "pptx"  # Default format
            }
            
            # Ensure all slides have proper IDs
            for slide_data in slides_data["slides"]:
                if not slide_data.get("id"):
                    # Generate a valid MongoDB ObjectId if none exists
                    from bson import ObjectId
                    slide_data["id"] = str(ObjectId())
            
            update_data = PresentationFinalEditUpdate(
                title=presentation.title or "Untitled Presentation",
                slides=slides_data,
                updated_at=None  # Will be set by CRUD
            )
            
            updated_final_edit = await presentation_final_edit_crud.update_presentation_final_edit(
                existing_final_edit.id, update_data
            )
            return updated_final_edit
        else:
            # Create new final edit
            slides_data = {
                "slides": [slide.model_dump() for slide in slides],
                "total_slides": len(slides),
                "export_format": "pptx"  # Default format
            }
            
            # Ensure all slides have proper IDs
            for slide_data in slides_data["slides"]:
                if not slide_data.get("id"):
                    # Generate a valid MongoDB ObjectId if none exists
                    from bson import ObjectId
                    slide_data["id"] = str(ObjectId())
            
            final_edit_data = PresentationFinalEditCreate(
                presentation_id=presentation_id,
                user_id=current_user.id,
                title=presentation.title or "Untitled Presentation",
                template_id=presentation.layout.get("id") if presentation.layout else None,
                slides=slides_data,
                thumbnail_url=None,  # TODO: Generate thumbnail
                s3_pptx_url=None,  # Will be set when exported
                s3_pdf_url=None,   # Will be set when exported
                is_published=False
            )
            
            final_edit_id = await presentation_final_edit_crud.create_presentation_final_edit(final_edit_data)
            return await presentation_final_edit_crud.get_presentation_final_edit_by_id(final_edit_id)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save presentation: {str(e)}")
