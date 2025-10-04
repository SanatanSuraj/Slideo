from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models.mongo.slide import Slide, SlideCreate, SlideUpdate
from models.mongo.user import User
from crud.slide_crud import slide_crud
from crud.presentation_crud import presentation_crud
from auth.dependencies import get_current_active_user

router = APIRouter(prefix="/slides", tags=["slides"])

@router.post("/", response_model=Slide)
async def create_slide(
    slide: SlideCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new slide"""
    # Check if user owns the presentation
    presentation = await presentation_crud.get_presentation_by_id(slide.presentation_id)
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
    
    slide_id = await slide_crud.create_slide(slide)
    return await slide_crud.get_slide_by_id(slide_id)

@router.get("/presentation/{presentation_id}", response_model=List[Slide])
async def get_slides_by_presentation(
    presentation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get all slides for a presentation"""
    # Check if user owns the presentation
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
    
    slides = await slide_crud.get_slides_by_presentation(presentation_id)
    return slides

@router.get("/{slide_id}", response_model=Slide)
async def get_slide(
    slide_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific slide"""
    slide = await slide_crud.get_slide_by_id(slide_id)
    if not slide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slide not found"
        )
    
    # Check if user owns the presentation
    presentation = await presentation_crud.get_presentation_by_id(slide.presentation_id)
    if not presentation or presentation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return slide

@router.put("/{slide_id}", response_model=Slide)
async def update_slide(
    slide_id: str,
    slide_update: SlideUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a slide"""
    # Check if slide exists and user owns the presentation
    slide = await slide_crud.get_slide_by_id(slide_id)
    if not slide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slide not found"
        )
    
    presentation = await presentation_crud.get_presentation_by_id(slide.presentation_id)
    if not presentation or presentation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_slide = await slide_crud.update_slide(slide_id, slide_update)
    return updated_slide

@router.delete("/{slide_id}")
async def delete_slide(
    slide_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a slide"""
    # Check if slide exists and user owns the presentation
    slide = await slide_crud.get_slide_by_id(slide_id)
    if not slide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slide not found"
        )
    
    presentation = await presentation_crud.get_presentation_by_id(slide.presentation_id)
    if not presentation or presentation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = await slide_crud.delete_slide(slide_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete slide"
        )
    
    return {"message": "Slide deleted successfully"}
