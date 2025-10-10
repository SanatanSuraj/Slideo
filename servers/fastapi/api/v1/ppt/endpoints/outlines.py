import asyncio
import json
import math
import traceback
import uuid
import dirtyjson
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from models.presentation_outline_model import PresentationOutlineModel
from models.mongo.presentation import Presentation, PresentationUpdate
from models.sse_response import (
    SSECompleteResponse,
    SSEErrorResponse,
    SSEResponse,
    SSEStatusResponse,
)
from services.temp_file_service import TEMP_FILE_SERVICE
from crud.presentation_crud import presentation_crud
from services.documents_loader import DocumentsLoader
from utils.llm_calls.generate_presentation_outlines import generate_ppt_outline
from utils.ppt_utils import get_presentation_title_from_outlines
from auth.dependencies import get_current_active_user, get_current_active_user_with_query_fallback
from models.mongo.user import User

OUTLINES_ROUTER = APIRouter(prefix="/outlines", tags=["Outlines"])


@OUTLINES_ROUTER.get("/stream/{id}")
async def stream_outlines(
    id: str, 
    current_user: User = Depends(get_current_active_user_with_query_fallback)
):
    presentation = await presentation_crud.get_presentation_by_id(id)

    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Check if user owns the presentation
    if presentation.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this presentation")

    temp_dir = TEMP_FILE_SERVICE.create_temp_dir()

    async def inner():
        yield SSEStatusResponse(
            status="Generating presentation outlines..."
        ).to_string()

        additional_context = ""
        if presentation.file_paths:
            documents_loader = DocumentsLoader(file_paths=presentation.file_paths)
            await documents_loader.load_documents(temp_dir)
            documents = documents_loader.documents
            if documents:
                additional_context = "\n\n".join(documents)

        presentation_outlines_text = ""

        n_slides_to_generate = presentation.n_slides
        if presentation.include_table_of_contents:
            needed_toc_count = math.ceil((presentation.n_slides - 1) / 10)
            n_slides_to_generate -= math.ceil(
                (presentation.n_slides - needed_toc_count) / 10
            )

        async for chunk in generate_ppt_outline(
            presentation.content,
            n_slides_to_generate,
            presentation.language,
            additional_context,
            presentation.tone,
            presentation.verbosity,
            presentation.instructions,
            presentation.include_title_slide,
            presentation.web_search,
        ):
            # Give control to the event loop
            await asyncio.sleep(0)

            if isinstance(chunk, HTTPException):
                yield SSEErrorResponse(detail=chunk.detail).to_string()
                return

            yield SSEResponse(
                event="response",
                data=json.dumps({"type": "chunk", "chunk": chunk}),
            ).to_string()

            presentation_outlines_text += chunk

        try:
            # Add defensive logging
            print("🧠 Raw Gemini output:", presentation_outlines_text[:200] + "..." if len(presentation_outlines_text) > 200 else presentation_outlines_text)
            
            # Try to parse as JSON first
            try:
                presentation_outlines_json = dict(
                    dirtyjson.loads(presentation_outlines_text)
                )
                
                # Check if the JSON has the expected structure
                if "slides" not in presentation_outlines_json:
                    print("⚠️ JSON missing 'slides' field, attempting to transform structure")
                    
                    # Try to transform different possible structures
                    if "presentation" in presentation_outlines_json:
                        # Handle case where LLM returns {"presentation": {...}}
                        presentation_data = presentation_outlines_json["presentation"]
                        if isinstance(presentation_data, dict) and "content" in presentation_data:
                            presentation_outlines_json = {
                                "slides": [
                                    {
                                        "content": presentation_data["content"]
                                    }
                                ]
                            }
                        else:
                            # Wrap the entire presentation data as a single slide
                            presentation_outlines_json = {
                                "slides": [
                                    {
                                        "content": str(presentation_data)
                                    }
                                ]
                            }
                    elif "content" in presentation_outlines_json:
                        # Handle case where LLM returns {"content": "..."}
                        presentation_outlines_json = {
                            "slides": [
                                {
                                    "content": presentation_outlines_json["content"]
                                }
                            ]
                        }
                    else:
                        # If we can't find expected fields, wrap the entire JSON as a single slide
                        presentation_outlines_json = {
                            "slides": [
                                {
                                    "content": str(presentation_outlines_json)
                                }
                            ]
                        }
                    print("✅ Transformed JSON structure to expected format")
                
            except Exception as json_error:
                print("⚠️ JSON parsing failed, attempting to wrap as plain text outline")
                # If JSON parsing fails, wrap the text as a basic outline structure
                presentation_outlines_json = {
                    "slides": [
                        {
                            "content": presentation_outlines_text
                        }
                    ]
                }
                print("✅ Wrapped plain text as outline structure")
                
        except Exception as e:
            traceback.print_exc()
            yield SSEErrorResponse(
                detail=f"Failed to generate presentation outlines. Please try again. {str(e)}",
            ).to_string()
            return

        try:
            presentation_outlines = PresentationOutlineModel(**presentation_outlines_json)
        except Exception as model_error:
            print(f"❌ Failed to create PresentationOutlineModel: {model_error}")
            print(f"📋 JSON structure: {presentation_outlines_json}")
            # Try to create a fallback structure
            if isinstance(presentation_outlines_json, dict) and "slides" in presentation_outlines_json:
                # If slides exist but validation fails, try to fix the structure
                slides = presentation_outlines_json["slides"]
                if isinstance(slides, list) and len(slides) > 0:
                    # Ensure each slide has the required content field
                    fixed_slides = []
                    for slide in slides:
                        if isinstance(slide, dict):
                            if "content" in slide:
                                fixed_slides.append({"content": slide["content"]})
                            elif "slideContent" in slide:
                                # Map slideContent to content
                                fixed_slides.append({"content": slide["slideContent"]})
                            else:
                                # If no content field, use the entire slide as content
                                fixed_slides.append({"content": str(slide)})
                        else:
                            # If slide is not a dict, convert to string
                            fixed_slides.append({"content": str(slide)})
                    
                    presentation_outlines_json = {"slides": fixed_slides}
                    print("🔧 Attempting to fix slide structure")
                    presentation_outlines = PresentationOutlineModel(**presentation_outlines_json)
                else:
                    raise model_error
            else:
                raise model_error

        presentation_outlines.slides = presentation_outlines.slides[
            :n_slides_to_generate
        ]

        # Update presentation with outlines and title
        presentation_update = PresentationUpdate(
            outlines=presentation_outlines.model_dump(),
            title=get_presentation_title_from_outlines(presentation_outlines)
        )
        await presentation_crud.update_presentation(id, presentation_update)

        yield SSECompleteResponse(
            key="presentation", value=presentation.model_dump(mode="json")
        ).to_string()

    return StreamingResponse(inner(), media_type="text/event-stream")
