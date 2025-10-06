import asyncio
from datetime import datetime
import json
import math
import os
import random
import traceback
import logging
from typing import Annotated, List, Literal, Optional, Tuple
import dirtyjson
from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Path
from fastapi.responses import StreamingResponse
from crud.presentation_crud import presentation_crud
from crud.slide_crud import slide_crud
from crud.template_crud import template_crud
from auth.dependencies import get_current_active_user, get_current_active_user_with_query_fallback
from models.mongo.user import User
from constants.presentation import DEFAULT_TEMPLATES
from enums.webhook_event import WebhookEvent
from models.api_error_model import APIErrorModel
from models.generate_presentation_request import GeneratePresentationRequest
from models.presentation_and_path import PresentationPathAndEditPath
from models.presentation_from_template import EditPresentationRequest
from models.presentation_outline_model import (
    PresentationOutlineModel,
    SlideOutlineModel,
)
from enums.tone import Tone
from enums.verbosity import Verbosity
from models.pptx_models import PptxPresentationModel
from models.presentation_layout import PresentationLayoutModel
from models.presentation_structure_model import PresentationStructureModel
from models.presentation_with_slides import (
    PresentationWithSlides,
)
from models.mongo.template import Template

from services.documents_loader import DocumentsLoader
from services.webhook_service import WebhookService
from utils.get_layout_by_name import get_layout_by_name
from services.image_generation_service import ImageGenerationService
from utils.dict_utils import deep_update
from utils.export_utils import export_presentation
from utils.llm_calls.generate_presentation_outlines import generate_ppt_outline
from models.mongo.slide import Slide
from models.sse_response import SSECompleteResponse, SSEErrorResponse, SSEResponse

from services.temp_file_service import TEMP_FILE_SERVICE
from services.concurrent_service import CONCURRENT_SERVICE
from models.mongo.presentation import Presentation, PresentationCreate, PresentationUpdate
from services.pptx_presentation_creator import PptxPresentationCreator
from models.mongo.task import Task
from utils.asset_directory_utils import get_exports_directory, get_images_directory
from utils.llm_calls.generate_presentation_structure import (
    generate_presentation_structure,
)
from utils.llm_calls.generate_slide_content import (
    get_slide_content_from_type_and_outline,
)
from utils.ppt_utils import (
    get_presentation_title_from_outlines,
    select_toc_or_list_slide_layout_index,
)
from utils.process_slides import (
    process_slide_add_placeholder_assets,
    process_slide_and_fetch_assets,
)
import uuid

# Set up logger
logger = logging.getLogger(__name__)

PRESENTATION_ROUTER = APIRouter(prefix="/presentation", tags=["Presentation"])


@PRESENTATION_ROUTER.get("/all", response_model=List[PresentationWithSlides])
async def get_all_presentations(current_user: User = Depends(get_current_active_user)):
    presentations = await presentation_crud.get_presentations_by_user(str(current_user.id))
    presentations_with_slides = []
    
    for presentation in presentations:
        # Get first slide for each presentation
        slides = await slide_crud.get_slides_by_presentation(presentation.id)
        first_slide = slides[0] if slides else None
        
        presentations_with_slides.append(
            PresentationWithSlides.from_dict({
                **presentation.dict(),
                "slides": [first_slide] if first_slide else [],
            })
        )
    
    return presentations_with_slides


@PRESENTATION_ROUTER.get("/{id}", response_model=PresentationWithSlides)
async def get_presentation(
    id: str, 
    current_user: User = Depends(get_current_active_user)
):
    presentation = await presentation_crud.get_presentation_by_id(id)
    if not presentation:
        raise HTTPException(404, "Presentation not found")
    
    # Check if user owns the presentation
    if presentation.user_id != str(current_user.id):
        raise HTTPException(403, "Not authorized to view this presentation")
    
    slides = await slide_crud.get_slides_by_presentation(id)
    return PresentationWithSlides.from_dict({
        **presentation.dict(),
        "slides": slides,
    })


@PRESENTATION_ROUTER.delete("/{id}", status_code=204)
async def delete_presentation(
    id: str, 
    current_user: User = Depends(get_current_active_user)
):
    presentation = await presentation_crud.get_presentation_by_id(id)
    if not presentation:
        raise HTTPException(404, "Presentation not found")
    
    # Check if user owns the presentation
    if presentation.user_id != str(current_user.id):
        raise HTTPException(403, "Not authorized to delete this presentation")

    await presentation_crud.delete_presentation(id)


@PRESENTATION_ROUTER.post("/create", response_model=Presentation)
async def create_presentation(
    content: Annotated[str, Body()],
    n_slides: Annotated[int, Body()],
    language: Annotated[str, Body()],
    file_paths: Annotated[Optional[List[str]], Body()] = None,
    tone: Annotated[Tone, Body()] = Tone.DEFAULT,
    verbosity: Annotated[Verbosity, Body()] = Verbosity.STANDARD,
    instructions: Annotated[Optional[str], Body()] = None,
    include_table_of_contents: Annotated[bool, Body()] = False,
    include_title_slide: Annotated[bool, Body()] = True,
    web_search: Annotated[bool, Body()] = False,
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Log incoming request details
        logger.info(f"📝 Creating presentation for user: {current_user.id}")
        logger.info(f"📝 Request payload: content='{content[:50]}...', n_slides={n_slides}, language={language}")
        logger.info(f"📝 User details: id={current_user.id}, email={getattr(current_user, 'email', 'N/A')}")
        
        # Validate input parameters
        if include_table_of_contents and n_slides < 3:
            logger.warning(f"❌ Invalid request: Table of contents requires 3+ slides, got {n_slides}")
            raise HTTPException(
                status_code=400,
                detail="Number of slides cannot be less than 3 if table of contents is included",
            )

        # Check MongoDB connection
        try:
            from db.mongo import client
            if client:
                await client.server_info()
                logger.info("✅ MongoDB connection verified")
            else:
                logger.error("❌ MongoDB client is None")
                raise HTTPException(status_code=500, detail="Database connection not available")
        except Exception as e:
            logger.error(f"❌ MongoDB connection check failed: {e}")
            raise HTTPException(status_code=500, detail="Database connection failed")

        # Check LLM provider configuration
        llm_provider = os.getenv("LLM", "").lower()
        if llm_provider == "openai":
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                logger.error("❌ OPENAI_API_KEY not found in environment")
                raise HTTPException(status_code=500, detail="OpenAI API key not configured")
            logger.info("✅ OpenAI configuration verified")
        elif llm_provider == "google":
            google_key = os.getenv("GOOGLE_API_KEY")
            if not google_key:
                logger.error("❌ GOOGLE_API_KEY not found in environment")
                raise HTTPException(status_code=500, detail="Google API key not configured")
            logger.info("✅ Google configuration verified")
        else:
            logger.warning(f"⚠️ Unknown LLM provider: {llm_provider}")

        # Generate presentation ID
        presentation_id = str(uuid.uuid4())
        logger.info(f"📝 Generated presentation ID: {presentation_id}")

        # Create presentation object
        presentation_create = PresentationCreate(
            user_id=str(current_user.id),
            content=content,
            n_slides=n_slides,
            language=language,
            file_paths=file_paths,
            tone=tone.value,
            verbosity=verbosity.value,
            instructions=instructions,
            include_table_of_contents=include_table_of_contents,
            include_title_slide=include_title_slide,
            web_search=web_search,
        )

        logger.info("📝 Creating presentation in database...")
        created_presentation_id = await presentation_crud.create_presentation(presentation_create)
        logger.info(f"✅ Presentation created with ID: {created_presentation_id}")

        logger.info("📝 Retrieving created presentation...")
        presentation = await presentation_crud.get_presentation_by_id(created_presentation_id)
        logger.info(f"✅ Presentation retrieved successfully: {presentation.id}")

        return presentation

    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        # Log full exception details
        logger.error(f"❌ Internal server error in create_presentation: {str(e)}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        
        # Log request context for debugging
        logger.error(f"❌ Request context - User ID: {current_user.id if current_user else 'None'}")
        logger.error(f"❌ Request context - Content length: {len(content) if content else 0}")
        logger.error(f"❌ Request context - N slides: {n_slides}")
        
        # Return 500 with error details
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@PRESENTATION_ROUTER.post("/prepare", response_model=Presentation)
async def prepare_presentation(
    presentation_id: Annotated[str, Body()],
    outlines: Annotated[List[SlideOutlineModel], Body()],
    layout: Annotated[PresentationLayoutModel, Body()],
    title: Annotated[Optional[str], Body()] = None,
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Log incoming request details
        logger.info(f"📝 Preparing presentation for user: {current_user.id}")
        logger.info(f"📝 Presentation ID: {presentation_id}")
        logger.info(f"📝 Number of outlines: {len(outlines) if outlines else 0}")
        logger.info(f"📝 Layout name: {layout.name if layout else 'None'}")
        logger.info(f"📝 Layout ordered: {layout.ordered if layout else 'None'}")
        logger.info(f"📝 Number of slide layouts: {len(layout.slides) if layout and layout.slides else 0}")
        
        if not outlines:
            logger.warning("❌ No outlines provided")
            raise HTTPException(status_code=400, detail="Outlines are required")

        logger.info("📝 Fetching presentation from database...")
        presentation = await presentation_crud.get_presentation_by_id(presentation_id)
        if not presentation:
            logger.error(f"❌ Presentation not found: {presentation_id}")
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Check if user owns the presentation
        if presentation.user_id != str(current_user.id):
            logger.error(f"❌ User {current_user.id} not authorized to prepare presentation {presentation_id}")
            raise HTTPException(status_code=403, detail="Not authorized to prepare this presentation")

        logger.info("📝 Creating presentation outline model...")
        presentation_outline_model = PresentationOutlineModel(slides=outlines)

        total_slide_layouts = len(layout.slides)
        total_outlines = len(outlines)
        logger.info(f"📝 Total slide layouts: {total_slide_layouts}, Total outlines: {total_outlines}")

        logger.info("📝 Generating presentation structure...")
        if layout.ordered:
            logger.info("📝 Using ordered layout structure")
            presentation_structure = layout.to_presentation_structure()
        else:
            logger.info("📝 Generating structure using LLM...")
            try:
                presentation_structure: PresentationStructureModel = (
                    await generate_presentation_structure(
                        presentation_outline=presentation_outline_model,
                        presentation_layout=layout,
                        instructions=presentation.instructions,
                    )
                )
                logger.info("✅ LLM structure generation completed")
            except Exception as e:
                logger.error(f"❌ LLM structure generation failed: {str(e)}")
                logger.error(f"❌ Exception type: {type(e).__name__}")
                logger.error(f"❌ Full traceback: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate presentation structure: {str(e)}"
                )

        logger.info("📝 Processing slide structure...")
        presentation_structure.slides = presentation_structure.slides[: len(outlines)]
        for index in range(total_outlines):
            random_slide_index = random.randint(0, total_slide_layouts - 1)
            if index >= total_outlines:
                presentation_structure.slides.append(random_slide_index)
                continue
            if presentation_structure.slides[index] >= total_slide_layouts:
                presentation_structure.slides[index] = random_slide_index

        logger.info("📝 Processing table of contents...")
        if presentation.include_table_of_contents:
            n_toc_slides = presentation.n_slides - total_outlines
            toc_slide_layout_index = select_toc_or_list_slide_layout_index(layout)
            if toc_slide_layout_index != -1:
                outline_index = 1 if presentation.include_title_slide else 0
                for i in range(n_toc_slides):
                    outlines_to = outline_index + 10
                    if total_outlines == outlines_to:
                        outlines_to -= 1

                    presentation_structure.slides.insert(
                        i + 1 if presentation.include_title_slide else i,
                        toc_slide_layout_index,
                    )
                    toc_outline = f"Table of Contents\n\n"

                    for outline in presentation_outline_model.slides[
                        outline_index:outlines_to
                    ]:
                        page_number = (
                            outline_index - i + n_toc_slides + 1
                            if presentation.include_title_slide
                            else outline_index - i + n_toc_slides
                        )
                        toc_outline += f"Slide page number: {page_number}\n Slide Content: {outline.content[:100]}\n\n"
                        outline_index += 1

                    outline_index += 1

                    presentation_outline_model.slides.insert(
                        i + 1 if presentation.include_title_slide else i,
                        SlideOutlineModel(
                            content=toc_outline,
                        ),
                    )

        logger.info("📝 Updating presentation in database...")
        # Update presentation with new data
        presentation_update = PresentationUpdate(
            outlines=presentation_outline_model.model_dump(mode="json"),
            title=title or presentation.title,
            layout=layout.model_dump(),
            structure=presentation_structure.model_dump()
        )
        updated_presentation = await presentation_crud.update_presentation(str(presentation_id), presentation_update)
        logger.info(f"✅ Presentation updated successfully: {updated_presentation.id}")

        return updated_presentation

    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        # Log full exception details
        logger.error(f"❌ Internal server error in prepare_presentation: {str(e)}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        
        # Log request context for debugging
        logger.error(f"❌ Request context - User ID: {current_user.id if current_user else 'None'}")
        logger.error(f"❌ Request context - Presentation ID: {presentation_id}")
        logger.error(f"❌ Request context - Outlines count: {len(outlines) if outlines else 0}")
        logger.error(f"❌ Request context - Layout name: {layout.name if layout else 'None'}")
        
        # Return 500 with error details
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@PRESENTATION_ROUTER.get("/stream/{id}", response_model=PresentationWithSlides)
async def stream_presentation(
    id: str, current_user: User = Depends(get_current_active_user_with_query_fallback)
):
    presentation = await presentation_crud.get_presentation_by_id(id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    print(f"🔍 Stream validation - Presentation ID: {id}")
    print(f"🔍 Stream validation - Presentation found: {presentation is not None}")
    print(f"🔍 Stream validation - User ID: {presentation.user_id}")
    print(f"🔍 Stream validation - Current user ID: {current_user.id}")
    print(f"🔍 Stream validation - Structure: {presentation.structure}")
    print(f"🔍 Stream validation - Outlines: {presentation.outlines}")
    print(f"🔍 Stream validation - Structure type: {type(presentation.structure)}")
    print(f"🔍 Stream validation - Outlines type: {type(presentation.outlines)}")
    print(f"🔍 Stream validation - Structure empty check: {not presentation.structure or presentation.structure == {}}")
    print(f"🔍 Stream validation - Outlines empty check: {not presentation.outlines or presentation.outlines == {}}")
    
    # Check if user owns the presentation
    if presentation.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this presentation")
    
    # Check if presentation has the required structure and outlines
    if presentation.structure is None or not presentation.structure or presentation.structure == {}:
        print("❌ Presentation not prepared - missing structure")
        raise HTTPException(
            status_code=400,
            detail="Presentation not prepared. Please complete the outline generation and template selection process first.",
        )
    if presentation.outlines is None or not presentation.outlines or presentation.outlines == {}:
        print("❌ Presentation not prepared - missing outlines")
        raise HTTPException(
            status_code=400,
            detail="Presentation outlines are missing. Please generate outlines first by going to the outline page.",
        )

    image_generation_service = ImageGenerationService(get_images_directory())

    async def inner():
        from models.presentation_structure_model import PresentationStructureModel
        from models.presentation_layout import PresentationLayoutModel
        from models.presentation_outline_model import PresentationOutlineModel
        from datetime import datetime
        import json
        
        structure = PresentationStructureModel(**presentation.structure)
        layout = PresentationLayoutModel(**presentation.layout)
        outline = PresentationOutlineModel(**presentation.outlines)

        # These tasks will be gathered and awaited after all slides are generated
        async_assets_generation_tasks = []

        slides: List[Slide] = []
        yield SSEResponse(
            event="response",
            data=json.dumps({"type": "chunk", "chunk": '{ "slides": [ '}),
        ).to_string()
        for i, slide_layout_index in enumerate(structure.slides):
            slide_layout = layout.slides[slide_layout_index]

            try:
                slide_content = await get_slide_content_from_type_and_outline(
                    slide_layout,
                    outline.slides[i],
                    presentation.language,
                    presentation.tone,
                    presentation.verbosity,
                    presentation.instructions,
                )
            except HTTPException as e:
                yield SSEErrorResponse(detail=e.detail).to_string()
                return

            slide = Slide(
                presentation_id=id,
                slide_number=i,
                layout=slide_layout.id,
                notes=slide_content.get("__speaker_note__", ""),
                content=json.dumps(slide_content),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            slides.append(slide)

            # This will mutate slide and add placeholder assets
            process_slide_add_placeholder_assets(slide)

            # This will mutate slide
            async_assets_generation_tasks.append(
                process_slide_and_fetch_assets(image_generation_service, slide)
            )

            yield SSEResponse(
                event="response",
                data=json.dumps({"type": "chunk", "chunk": slide.model_dump_json()}),
            ).to_string()

        yield SSEResponse(
            event="response",
            data=json.dumps({"type": "chunk", "chunk": " ] }"}),
        ).to_string()

        generated_assets_lists = await asyncio.gather(*async_assets_generation_tasks)
        generated_assets = []
        for assets_list in generated_assets_lists:
            generated_assets.extend(assets_list)

        # Moved this here to make sure new slides are generated before deleting the old ones
        await slide_crud.delete_slides_by_presentation(str(id))
        
        # Commit operations handled by CRUD

        # Save slides to MongoDB
        for slide in slides:
            await slide_crud.create_slide(slide)

        response = PresentationWithSlides.from_dict({
            **presentation.model_dump(),
            "slides": slides,
        })

        yield SSECompleteResponse(
            key="presentation",
            value=response.model_dump(mode="json"),
        ).to_string()

    return StreamingResponse(inner(), media_type="text/event-stream")


@PRESENTATION_ROUTER.patch("/update", response_model=PresentationWithSlides)
async def update_presentation(
    id: Annotated[str, Body()],
    n_slides: Annotated[Optional[int], Body()] = None,
    title: Annotated[Optional[str], Body()] = None,
    slides: Annotated[Optional[List[Slide]], Body()] = None,
    current_user: User = Depends(get_current_active_user),
):
    presentation = await presentation_crud.get_presentation_by_id(str(id))
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    presentation_update_dict = {}
    if n_slides:
        presentation_update_dict["n_slides"] = n_slides
    if title:
        presentation_update_dict["title"] = title

    if n_slides or title:
        presentation_update = PresentationUpdate(**presentation_update_dict)
        await presentation_crud.update_presentation(str(id), presentation_update)

    if slides:
        # Slides are already in the correct format (string IDs)
        # Execute operations handled by CRUD.where(Slide.presentation == presentation.id)
        # Add all operations handled by CRUD
        for slide in slides:
            await slide_crud.update_slide(slide.id, slide)

    # Commit operations handled by CRUD

    return PresentationWithSlides.from_dict({
        **presentation.model_dump(),
        "slides": slides or [],
    })


@PRESENTATION_ROUTER.post("/export/pptx", response_model=str)
async def export_presentation_as_pptx(
    pptx_model: Annotated[PptxPresentationModel, Body()],
):
    temp_dir = TEMP_FILE_SERVICE.create_temp_dir()

    pptx_creator = PptxPresentationCreator(pptx_model, temp_dir)
    await pptx_creator.create_ppt()

    export_directory = get_exports_directory()
    pptx_path = os.path.join(
        export_directory, f"{pptx_model.name or uuid.uuid4()}.pptx"
    )
    pptx_creator.save(pptx_path)

    return pptx_path


@PRESENTATION_ROUTER.post("/export", response_model=PresentationPathAndEditPath)
async def export_presentation_as_pptx_or_pdf(
    id: Annotated[str, Body(description="Presentation ID to export")],
    export_as: Annotated[
        Literal["pptx", "pdf"], Body(description="Format to export the presentation as")
    ] = "pptx",
    current_user: User = Depends(get_current_active_user),
):
    presentation = await presentation_crud.get_presentation_by_id(str(id))

    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    presentation_and_path = await export_presentation(
        id,
        presentation.title or str(uuid.uuid4()),
        export_as,
    )

    return PresentationPathAndEditPath(
        **presentation_and_path.model_dump(),
        edit_path=f"/presentation?id={id}",
    )


async def check_if_api_request_is_valid(
    request: GeneratePresentationRequest,
    current_user: User = Depends(get_current_active_user),
) -> Tuple[str,]:
    presentation_id = str(uuid.uuid4())
    print(f"Presentation ID: {presentation_id}")

    # Making sure either content, slides markdown or files is provided
    if not (request.content or request.slides_markdown or request.files):
        raise HTTPException(
            status_code=400,
            detail="Either content or slides markdown or files is required to generate presentation",
        )

    # Making sure number of slides is greater than 0
    if request.n_slides <= 0:
        raise HTTPException(
            status_code=400,
            detail="Number of slides must be greater than 0",
        )

    # Checking if template is valid
    if request.template not in DEFAULT_TEMPLATES:
        request.template = request.template.lower()
        if not request.template.startswith("custom-"):
            raise HTTPException(
                status_code=400,
                detail="Template not found. Please use a valid template.",
            )
        template_id = request.template.replace("custom-", "")
        try:
            template = await template_crud.get_template_by_id(template_id)
            if not template:
                raise Exception()
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail="Template not found. Please use a valid template.",
            )

    return (presentation_id,)


async def generate_presentation_handler(
    request: GeneratePresentationRequest,
    presentation_id: str,
    async_status: Optional[Task],
    current_user: User = Depends(get_current_active_user),
):
    try:
        using_slides_markdown = False

        if request.slides_markdown:
            using_slides_markdown = True
            request.n_slides = len(request.slides_markdown)

        if not using_slides_markdown:
            additional_context = ""

            # Updating async status
            if async_status:
                async_status.message = "Generating presentation outlines"
                async_status.updated_at = datetime.now()
                await task_crud.update_task(str(async_status.id), async_status)

            if request.files:
                documents_loader = DocumentsLoader(file_paths=request.files)
                await documents_loader.load_documents()
                documents = documents_loader.documents
                if documents:
                    additional_context = "\n\n".join(documents)

            # Finding number of slides to generate by considering table of contents
            n_slides_to_generate = request.n_slides
            if request.include_table_of_contents:
                needed_toc_count = math.ceil(
                    (
                        (request.n_slides - 1)
                        if request.include_title_slide
                        else request.n_slides
                    )
                    / 10
                )
                n_slides_to_generate -= math.ceil(
                    (request.n_slides - needed_toc_count) / 10
                )

            presentation_outlines_text = ""
            async for chunk in generate_ppt_outline(
                request.content,
                n_slides_to_generate,
                request.language,
                additional_context,
                request.tone.value,
                request.verbosity.value,
                request.instructions,
                request.include_title_slide,
                request.web_search,
            ):

                if isinstance(chunk, HTTPException):
                    raise chunk

                presentation_outlines_text += chunk

            try:
                # Add defensive logging
                print("🧠 Raw Gemini output:", presentation_outlines_text[:200] + "..." if len(presentation_outlines_text) > 200 else presentation_outlines_text)
                
                # Try to parse as JSON first
                try:
                    presentation_outlines_json = dict(
                        dirtyjson.loads(presentation_outlines_text)
                    )
                except Exception as json_error:
                    print("⚠️ JSON parsing failed, attempting to wrap as plain text outline")
                    # If JSON parsing fails, wrap the text as a basic outline structure
                    presentation_outlines_json = {
                        "slides": [
                            {
                                "title": "Generated Outline",
                                "content": presentation_outlines_text
                            }
                        ]
                    }
                    print("✅ Wrapped plain text as outline structure")
                    
            except Exception as e:
                traceback.print_exc()
                raise HTTPException(
                    status_code=400,
                    detail="Failed to generate presentation outlines. Please try again.",
                )
            presentation_outlines = PresentationOutlineModel(
                **presentation_outlines_json
            )
            total_outlines = n_slides_to_generate

        else:
            # Setting outlines to slides markdown
            presentation_outlines = PresentationOutlineModel(
                slides=[
                    SlideOutlineModel(content=slide)
                    for slide in request.slides_markdown
                ]
            )
            total_outlines = len(request.slides_markdown)

        # Updating async status
        if async_status:
            async_status.message = f"Selecting layout for each slide"
            async_status.updated_at = datetime.now()
            await task_crud.update_task(str(async_status.id), async_status)

        print("-" * 40)
        print(f"Generated {total_outlines} outlines for the presentation")

        # Parse Layouts
        layout_model = await get_layout_by_name(request.template)
        total_slide_layouts = len(layout_model.slides)

        # Generate Structure
        if layout_model.ordered:
            presentation_structure = layout_model.to_presentation_structure()
        else:
            presentation_structure: PresentationStructureModel = (
                await generate_presentation_structure(
                    presentation_outlines,
                    layout_model,
                    request.instructions,
                    using_slides_markdown,
                )
            )

        presentation_structure.slides = presentation_structure.slides[:total_outlines]
        for index in range(total_outlines):
            random_slide_index = random.randint(0, total_slide_layouts - 1)
            if index >= total_outlines:
                presentation_structure.slides.append(random_slide_index)
                continue
            if presentation_structure.slides[index] >= total_slide_layouts:
                presentation_structure.slides[index] = random_slide_index

        # Injecting table of contents to the presentation structure and outlines
        if request.include_table_of_contents and not using_slides_markdown:
            n_toc_slides = request.n_slides - total_outlines
            toc_slide_layout_index = select_toc_or_list_slide_layout_index(layout_model)
            if toc_slide_layout_index != -1:
                outline_index = 1 if request.include_title_slide else 0
                for i in range(n_toc_slides):
                    outlines_to = outline_index + 10
                    if total_outlines == outlines_to:
                        outlines_to -= 1

                    presentation_structure.slides.insert(
                        i + 1 if request.include_title_slide else i,
                        toc_slide_layout_index,
                    )
                    toc_outline = f"Table of Contents\n\n"

                    for outline in presentation_outlines.slides[
                        outline_index:outlines_to
                    ]:
                        page_number = (
                            outline_index - i + n_toc_slides + 1
                            if request.include_title_slide
                            else outline_index - i + n_toc_slides
                        )
                        toc_outline += f"Slide page number: {page_number}\n Slide Content: {outline.content[:100]}\n\n"
                        outline_index += 1

                    outline_index += 1

                    presentation_outlines.slides.insert(
                        i + 1 if request.include_title_slide else i,
                        SlideOutlineModel(
                            content=toc_outline,
                        ),
                    )

        # Create Presentation
        presentation = Presentation(
            id=presentation_id,
            content=request.content,
            n_slides=request.n_slides,
            language=request.language,
            title=get_presentation_title_from_outlines(presentation_outlines),
            outlines=presentation_outlines.model_dump(),
            layout=layout_model.model_dump(),
            structure=presentation_structure.model_dump(),
            tone=request.tone.value,
            verbosity=request.verbosity.value,
            instructions=request.instructions,
        )

        # Updating async status
        if async_status:
            async_status.message = "Generating slides"
            async_status.updated_at = datetime.now()
            await task_crud.update_task(str(async_status.id), async_status)

        image_generation_service = ImageGenerationService(get_images_directory())
        async_assets_generation_tasks = []

        # 7. Generate slide content concurrently (batched), then build slides and fetch assets
        slides: List[Slide] = []

        slide_layout_indices = presentation_structure.slides
        slide_layouts = [layout_model.slides[idx] for idx in slide_layout_indices]

        # Schedule slide content generation and asset fetching in batches of 10
        batch_size = 10
        for start in range(0, len(slide_layouts), batch_size):
            end = min(start + batch_size, len(slide_layouts))

            print(f"Generating slides from {start} to {end}")

            # Generate contents for this batch concurrently
            content_tasks = [
                get_slide_content_from_type_and_outline(
                    slide_layouts[i],
                    presentation_outlines.slides[i],
                    request.language,
                    request.tone.value,
                    request.verbosity.value,
                    request.instructions,
                )
                for i in range(start, end)
            ]
            batch_contents: List[dict] = await asyncio.gather(*content_tasks)

            # Build slides for this batch
            batch_slides: List[Slide] = []
            for offset, slide_content in enumerate(batch_contents):
                i = start + offset
                slide_layout = slide_layouts[i]
                slide = Slide(
                    presentation=presentation_id,
                    layout_group=layout_model.name,
                    layout=slide_layout.id,
                    index=i,
                    speaker_note=slide_content.get("__speaker_note__"),
                    content=slide_content,
                )
                slides.append(slide)
                batch_slides.append(slide)

            # Start asset fetch tasks for just-generated slides so they run while next batch is processed
            asset_tasks = [
                process_slide_and_fetch_assets(image_generation_service, slide)
                for slide in batch_slides
            ]
            async_assets_generation_tasks.extend(asset_tasks)

        if async_status:
            async_status.message = "Fetching assets for slides"
            async_status.updated_at = datetime.now()
            await task_crud.update_task(str(async_status.id), async_status)

        # Run all asset tasks concurrently while batches may still be generating content
        generated_assets_list = await asyncio.gather(*async_assets_generation_tasks)
        generated_assets = []
        for assets_list in generated_assets_list:
            generated_assets.extend(assets_list)

        # 8. Save Presentation and Slides
        # Save slides to MongoDB
        for slide in slides:
            await slide_crud.create_slide(slide)

        if async_status:
            async_status.message = "Exporting presentation"
            async_status.updated_at = datetime.now()
            # Add operations handled by CRUD

        # 9. Export
        presentation_and_path = await export_presentation(
            presentation_id, presentation.title or str(uuid.uuid4()), request.export_as
        )

        response = PresentationPathAndEditPath(
            **presentation_and_path.model_dump(),
            edit_path=f"/presentation?id={presentation_id}",
        )

        if async_status:
            async_status.message = "Presentation generation completed"
            async_status.status = "completed"
            async_status.data = response.model_dump(mode="json")
            async_status.updated_at = datetime.now()
            await task_crud.update_task(str(async_status.id), async_status)

        # Triggering webhook on success
        CONCURRENT_SERVICE.run_task(
            None,
            WebhookService.send_webhook,
            WebhookEvent.PRESENTATION_GENERATION_COMPLETED,
            response.model_dump(mode="json"),
        )

        return response

    except Exception as e:
        if not isinstance(e, HTTPException):
            traceback.print_exc()
            e = HTTPException(status_code=500, detail="Presentation generation failed")

        api_error_model = APIErrorModel.from_exception(e)

        # Triggering webhook on failure
        CONCURRENT_SERVICE.run_task(
            None,
            WebhookService.send_webhook,
            WebhookEvent.PRESENTATION_GENERATION_FAILED,
            api_error_model.model_dump(mode="json"),
        )

        if async_status:
            async_status.status = "error"
            async_status.message = "Presentation generation failed"
            async_status.updated_at = datetime.now()
            async_status.error = api_error_model.model_dump(mode="json")
            await task_crud.update_task(str(async_status.id), async_status)

        else:
            raise e


@PRESENTATION_ROUTER.post("/generate", response_model=PresentationPathAndEditPath)
async def generate_presentation_sync(
    request: GeneratePresentationRequest,
    current_user: User = Depends(get_current_active_user),
):
    try:
        (presentation_id,) = await check_if_api_request_is_valid(request, sql_session)
        return await generate_presentation_handler(
            request, presentation_id, None, sql_session
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Presentation generation failed")


@PRESENTATION_ROUTER.post(
    "/generate/async", response_model=Task
)
async def generate_presentation_async(
    request: GeneratePresentationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
):
    try:
        (presentation_id,) = await check_if_api_request_is_valid(request, sql_session)

        async_status = Task(
            status="pending",
            message="Queued for generation",
            data=None,
        )
        await task_crud.update_task(str(async_status.id), async_status)

        background_tasks.add_task(
            generate_presentation_handler,
            request,
            presentation_id,
            async_status=async_status,
            sql_session=sql_session,
        )
        return async_status

    except Exception as e:
        if not isinstance(e, HTTPException):
            print(e)
            e = HTTPException(status_code=500, detail="Presentation generation failed")

        raise e


@PRESENTATION_ROUTER.get(
    "/status/{id}", response_model=Task
)
async def check_async_presentation_generation_status(
    id: str = Path(description="ID of the presentation generation task"),
    current_user: User = Depends(get_current_active_user),
):
    status = await task_crud.get_task_by_id(str(id))
    if not status:
        raise HTTPException(
            status_code=404, detail="No presentation generation task found"
        )
    return status


@PRESENTATION_ROUTER.post("/edit", response_model=PresentationPathAndEditPath)
async def edit_presentation_with_new_content(
    data: Annotated[EditPresentationRequest, Body()],
    current_user: User = Depends(get_current_active_user),
):
    presentation = await presentation_crud.get_presentation_by_id(str(data.presentation_id))
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    slides = await slide_crud.get_slides_by_presentation(str(data.presentation_id))

    new_slides = []
    slides_to_delete = []
    for each_slide in slides:
        updated_content = None
        new_slide_data = list(
            filter(lambda x: x.index == each_slide.index, data.slides)
        )
        if new_slide_data:
            updated_content = deep_update(each_slide.content, new_slide_data[0].content)
            new_slides.append(
                each_slide.get_new_slide(presentation.id, updated_content)
            )
            slides_to_delete.append(each_slide.id)

    await slide_crud.delete_slides_by_ids(slides_to_delete)

    # Add all operations handled by CRUD
    # Commit operations handled by CRUD

    presentation_and_path = await export_presentation(
        presentation.id, presentation.title or str(uuid.uuid4()), data.export_as
    )

    return PresentationPathAndEditPath(
        **presentation_and_path.model_dump(),
        edit_path=f"/presentation?id={presentation.id}",
    )


@PRESENTATION_ROUTER.post("/derive", response_model=PresentationPathAndEditPath)
async def derive_presentation_from_existing_one(
    data: Annotated[EditPresentationRequest, Body()],
    current_user: User = Depends(get_current_active_user),
):
    presentation = await presentation_crud.get_presentation_by_id(str(data.presentation_id))
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    slides = await slide_crud.get_slides_by_presentation(str(data.presentation_id))

    new_presentation = presentation.get_new_presentation()
    new_slides = []
    for each_slide in slides:
        updated_content = None
        new_slide_data = list(
            filter(lambda x: x.index == each_slide.index, data.slides)
        )
        if new_slide_data:
            updated_content = deep_update(each_slide.content, new_slide_data[0].content)
        new_slides.append(
            each_slide.get_new_slide(new_presentation.id, updated_content)
        )

    # Save new slides to MongoDB
        for slide in new_slides:
            await slide_crud.create_slide(slide)

    presentation_and_path = await export_presentation(
        new_presentation.id, new_presentation.title or str(uuid.uuid4()), data.export_as
    )

    return PresentationPathAndEditPath(
        **presentation_and_path.model_dump(),
        edit_path=f"/presentation?id={new_presentation.id}",
    )
