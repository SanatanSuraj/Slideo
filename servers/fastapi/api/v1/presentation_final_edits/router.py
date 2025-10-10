from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from models.mongo.presentation_final_edit import (
    PresentationFinalEdit, 
    PresentationFinalEditCreate, 
    PresentationFinalEditUpdate
)
from crud.presentation_final_edit_crud import presentation_final_edit_crud
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
