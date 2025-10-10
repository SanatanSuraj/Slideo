from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Literal, Optional
from pydantic import BaseModel
import uuid
from models.mongo.user import User
from auth.dependencies import get_current_active_user
from utils.export_utils import export_presentation
from crud.presentation_crud import presentation_crud
from crud.slide_crud import slide_crud
from crud.presentation_final_edit_crud import presentation_final_edit_crud
from models.mongo.presentation_final_edit import PresentationFinalEditCreate
from models.presentation_and_path import PresentationAndPath
import logging

logger = logging.getLogger(__name__)

EXPORT_ROUTER = APIRouter(prefix="/export", tags=["Export"])

class ExportRequest(BaseModel):
    presentation_id: str  # Changed from uuid.UUID to str to support MongoDB ObjectIds
    title: Optional[str] = None
    export_as: Literal["pptx", "pdf"] = "pptx"
    template_id: Optional[str] = None
    save_final_edit: bool = True

class ExportResponse(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    s3_url: Optional[str] = None
    final_edit_id: Optional[str] = None
    presentation_and_path: Optional[PresentationAndPath] = None

@EXPORT_ROUTER.post("/presentation", response_model=ExportResponse)
async def export_presentation_final(
    request: ExportRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Export presentation and automatically save to presentation_final_edits collection
    This is the final step after template editing
    """
    try:
        # Get the presentation
        presentation = await presentation_crud.get_presentation_by_id(str(request.presentation_id))
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Check if user owns the presentation
        if presentation.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all slides for the presentation
        slides = await slide_crud.get_slides_by_presentation(str(request.presentation_id))
        
        # Export the presentation
        logger.info(f"Exporting presentation {request.presentation_id} as {request.export_as}")
        presentation_and_path = await export_presentation(
            presentation_id=request.presentation_id,
            title=request.title or presentation.title or "Untitled Presentation",
            export_as=request.export_as,
            user_id=current_user.id,
            save_to_mongodb=True
        )
        
        # Save to presentation_final_edits if requested
        final_edit_id = None
        if request.save_final_edit:
            logger.info(f"Saving final edit for presentation {request.presentation_id}")
            
            # Prepare slides data for storage
            slides_data = {
                "slides": [slide.model_dump() for slide in slides],
                "total_slides": len(slides),
                "export_format": request.export_as
            }
            
            # Create final edit record
            final_edit_data = PresentationFinalEditCreate(
                presentation_id=str(request.presentation_id),
                user_id=current_user.id,
                title=request.title or presentation.title or "Untitled Presentation",
                template_id=request.template_id,
                slides=slides_data,
                thumbnail_url=None,  # TODO: Generate thumbnail
                s3_pptx_url=presentation_and_path.s3_pptx_url if request.export_as == "pptx" else None,
                s3_pdf_url=presentation_and_path.s3_pdf_url if request.export_as == "pdf" else None,
                is_published=False
            )
            
            final_edit_id = await presentation_final_edit_crud.create_presentation_final_edit(final_edit_data)
            logger.info(f"Final edit saved with ID: {final_edit_id}")
        
        return ExportResponse(
            success=True,
            message=f"Presentation exported successfully as {request.export_as}",
            file_path=presentation_and_path.path,
            s3_url=presentation_and_path.s3_pptx_url if request.export_as == "pptx" else presentation_and_path.s3_pdf_url,
            final_edit_id=final_edit_id,
            presentation_and_path=presentation_and_path
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export presentation: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@EXPORT_ROUTER.post("/presentation/quick", response_model=ExportResponse)
async def quick_export_presentation(
    presentation_id: uuid.UUID = Body(...),
    export_as: Literal["pptx", "pdf"] = Body("pptx"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Quick export endpoint for simple export without additional options
    """
    request = ExportRequest(
        presentation_id=presentation_id,
        export_as=export_as,
        save_final_edit=True
    )
    return await export_presentation_final(request, current_user)

@EXPORT_ROUTER.get("/presentation/{presentation_id}/status")
async def get_export_status(
    presentation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Check if a presentation has been exported and saved to final edits
    """
    try:
        # Check if presentation exists and user owns it
        presentation = await presentation_crud.get_presentation_by_id(presentation_id)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        if presentation.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if final edit exists
        final_edit = await presentation_final_edit_crud.get_presentation_final_edit_by_presentation_id(presentation_id)
        
        return {
            "presentation_id": presentation_id,
            "has_final_edit": final_edit is not None,
            "final_edit_id": final_edit.id if final_edit else None,
            "exported_at": final_edit.edited_at if final_edit else None,
            "s3_pptx_url": final_edit.s3_pptx_url if final_edit else None,
            "s3_pdf_url": final_edit.s3_pdf_url if final_edit else None,
            "is_published": final_edit.is_published if final_edit else False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get export status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get export status: {str(e)}")
