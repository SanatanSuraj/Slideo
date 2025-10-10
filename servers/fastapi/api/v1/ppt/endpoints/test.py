from fastapi import APIRouter, HTTPException
from typing import Optional
from crud.presentation_crud import presentation_crud
from crud.slide_crud import slide_crud
from crud.presentation_final_edit_crud import presentation_final_edit_crud
import logging

logger = logging.getLogger(__name__)

TEST_ROUTER = APIRouter(prefix="/test", tags=["Test"])

@TEST_ROUTER.get("/presentation/{presentation_id}")
async def get_presentation_public(presentation_id: str):
    """
    Public endpoint to get presentation without authentication
    FOR TESTING PURPOSES ONLY
    """
    try:
        presentation = await presentation_crud.get_presentation_by_id(presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Get slides for this presentation
        slides = await slide_crud.get_slides_by_presentation(presentation_id)
        
        return {
            "presentation": presentation.model_dump(),
            "slides": [slide.model_dump() for slide in slides],
            "total_slides": len(slides)
        }
    except Exception as e:
        logger.error(f"Error getting presentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@TEST_ROUTER.get("/presentations")
async def get_all_presentations_public():
    """
    Public endpoint to get all presentations without authentication
    FOR TESTING PURPOSES ONLY
    """
    try:
        # Get all presentations (this is for testing, so we'll get all)
        presentations = []
        # Note: This is a simplified version - in production you'd want pagination
        return {
            "message": "This endpoint would return all presentations",
            "note": "Use /api/v1/presentations/ with authentication for production"
        }
    except Exception as e:
        logger.error(f"Error getting presentations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@TEST_ROUTER.get("/final-edits")
async def get_final_edits_public():
    """
    Public endpoint to get all final edits without authentication
    FOR TESTING PURPOSES ONLY
    """
    try:
        # Get all final edits
        final_edits = await presentation_final_edit_crud.get_published_presentation_final_edits()
        return {
            "final_edits": [edit.model_dump() for edit in final_edits],
            "total": len(final_edits)
        }
    except Exception as e:
        logger.error(f"Error getting final edits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@TEST_ROUTER.get("/auth-token")
async def get_test_auth_token():
    """
    Get a test authentication token for testing
    FOR TESTING PURPOSES ONLY
    """
    try:
        # This would normally require login, but for testing we'll return instructions
        return {
            "message": "To get an auth token, use:",
            "login_endpoint": "POST /api/v1/auth/login",
            "example_request": {
                "username": "suraj@webhhbuddy.agency",
                "password": "your-password",
                "remember_me": False
            },
            "note": "Use the 'access_token' from the response in Authorization header"
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
