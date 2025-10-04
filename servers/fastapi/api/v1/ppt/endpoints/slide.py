from typing import Annotated, Optional
from fastapi import APIRouter, Body, Depends, HTTPException
import uuid

from models.mongo.presentation import Presentation
from models.mongo.slide import Slide, SlideUpdate
from crud.presentation_crud import presentation_crud
from crud.slide_crud import slide_crud
from services.image_generation_service import ImageGenerationService
from utils.asset_directory_utils import get_images_directory
from utils.llm_calls.edit_slide import get_edited_slide_content
from utils.llm_calls.edit_slide_html import get_edited_slide_html
from utils.llm_calls.select_slide_type_on_edit import get_slide_layout_from_prompt
from utils.process_slides import process_old_and_new_slides_and_fetch_assets
from auth.dependencies import get_current_active_user
from models.mongo.user import User


SLIDE_ROUTER = APIRouter(prefix="/slide", tags=["Slide"])


@SLIDE_ROUTER.post("/edit")
async def edit_slide(
    id: Annotated[uuid.UUID, Body()],
    prompt: Annotated[str, Body()],
    current_user: User = Depends(get_current_active_user)
):
    slide = await slide_crud.get_slide_by_id(str(id))
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    presentation = await presentation_crud.get_presentation_by_id(slide.presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    presentation_layout = presentation.get_layout()
    slide_layout = await get_slide_layout_from_prompt(
        prompt, presentation_layout, slide
    )

    edited_slide_content = await get_edited_slide_content(
        prompt, slide, presentation.language, slide_layout
    )

    image_generation_service = ImageGenerationService(get_images_directory())

    # This will mutate edited_slide_content
    new_assets = await process_old_and_new_slides_and_fetch_assets(
        image_generation_service,
        slide.content,
        edited_slide_content,
    )

    # Update slide with new content
    slide_update = SlideUpdate(
        content=edited_slide_content,
        layout=slide_layout.id,
        notes=edited_slide_content.get("__speaker_note__", "")
    )
    
    updated_slide = await slide_crud.update_slide(slide.id, slide_update)
    
    # TODO: Handle new assets in MongoDB
    # For now, we'll skip the assets part as it requires more complex migration

    return updated_slide


@SLIDE_ROUTER.post("/edit-html", response_model=Slide)
async def edit_slide_html(
    id: Annotated[uuid.UUID, Body()],
    prompt: Annotated[str, Body()],
    html: Annotated[Optional[str], Body()] = None,
    current_user: User = Depends(get_current_active_user)
):
    slide = await slide_crud.get_slide_by_id(str(id))
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")

    html_to_edit = html or slide.html_content
    if not html_to_edit:
        raise HTTPException(status_code=400, detail="No HTML to edit")

    edited_slide_html = await get_edited_slide_html(prompt, html_to_edit)

    # Update slide with new HTML content
    slide_update = SlideUpdate(
        content={"html_content": edited_slide_html}
    )
    
    updated_slide = await slide_crud.update_slide(slide.id, slide_update)

    return updated_slide
