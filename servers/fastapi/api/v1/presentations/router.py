from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from models.mongo.presentation import Presentation, PresentationCreate, PresentationUpdate
from models.mongo.user import User
from crud.presentation_crud import presentation_crud
from auth.dependencies import get_current_active_user

router = APIRouter(prefix="/presentations", tags=["presentations"])

@router.post("/", response_model=Presentation)
async def create_presentation(
    presentation: PresentationCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new presentation"""
    presentation.user_id = current_user.id
    presentation_id = await presentation_crud.create_presentation(presentation)
    return await presentation_crud.get_presentation_by_id(presentation_id)

@router.get("/", response_model=List[Presentation])
async def get_presentations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's presentations"""
    presentations = await presentation_crud.get_presentations_by_user(
        current_user.id, skip=skip, limit=limit
    )
    return presentations

@router.get("/{presentation_id}", response_model=Presentation)
async def get_presentation(
    presentation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific presentation"""
    presentation = await presentation_crud.get_presentation_by_id(presentation_id)
    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found"
        )
    
    # Check if user owns this presentation
    if presentation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return presentation

@router.put("/{presentation_id}", response_model=Presentation)
async def update_presentation(
    presentation_id: str,
    presentation_update: PresentationUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a presentation"""
    # Check if presentation exists and user owns it
    presentation = await presentation_crud.get_presentation_by_id(presentation_id)
    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found"
        )
    
    if presentation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_presentation = await presentation_crud.update_presentation(
        presentation_id, presentation_update
    )
    return updated_presentation

@router.delete("/{presentation_id}")
async def delete_presentation(
    presentation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a presentation"""
    # Check if presentation exists and user owns it
    presentation = await presentation_crud.get_presentation_by_id(presentation_id)
    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found"
        )
    
    if presentation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = await presentation_crud.delete_presentation(presentation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete presentation"
        )
    
    return {"message": "Presentation deleted successfully"}

@router.get("/search/", response_model=List[Presentation])
async def search_presentations(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    """Search presentations"""
    presentations = await presentation_crud.search_presentations(
        current_user.id, query, skip=skip, limit=limit
    )
    return presentations
