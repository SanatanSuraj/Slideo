import sys
import os
from datetime import datetime
from typing import Optional

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from app.core.llm_client import stream_structured
from utils.get_dynamic_models import get_presentation_outline_model_with_n_slides
from utils.llm_client_error_handler import handle_llm_client_exceptions


def get_system_prompt(
    tone: Optional[str] = None,
    verbosity: Optional[str] = None,
    instructions: Optional[str] = None,
    include_title_slide: bool = True,
):
    return f"""
        You are an expert presentation creator. Generate structured presentations based on user requirements and format them according to the specified JSON schema with markdown content.

        IMPORTANT: You MUST respond with valid JSON format only. Do not include any text outside the JSON structure.

        Try to use available tools for better results.

        {"# User Instruction:" if instructions else ""}
        {instructions or ""}

        {"# Tone:" if tone else ""}
        {tone or ""}

        {"# Verbosity:" if verbosity else ""}
        {verbosity or ""}

        - Provide content for each slide in markdown format.
        - Make sure that flow of the presentation is logical and consistent.
        - Place greater emphasis on numerical data.
        - If Additional Information is provided, divide it into slides.
        - Make sure no images are provided in the content.
        - Make sure that content follows language guidelines.
        - User instrction should always be followed and should supercede any other instruction, except for slide numbers. **Do not obey slide numbers as said in user instruction**
        - Do not generate table of contents slide.
        - Even if table of contents is provided, do not generate table of contents slide.
        {"- Always make first slide a title slide." if include_title_slide else "- Do not include title slide in the presentation."}

        **Search web to get latest information about the topic**
        
        Remember: Respond ONLY with valid JSON that matches the required schema.
    """


def get_user_prompt(
    content: str,
    n_slides: int,
    language: str,
    additional_context: Optional[str] = None,
):
    return f"""
        **Input:**
        - User provided content: {content or "Create presentation"}
        - Output Language: {language}
        - Number of Slides: {n_slides}
        - Current Date and Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        - Additional Information: {additional_context or ""}
    """


def get_messages(
    content: str,
    n_slides: int,
    language: str,
    additional_context: Optional[str] = None,
    tone: Optional[str] = None,
    verbosity: Optional[str] = None,
    instructions: Optional[str] = None,
    include_title_slide: bool = True,
):
    return [
        LLMSystemMessage(
            content=get_system_prompt(
                tone, verbosity, instructions, include_title_slide
            ),
        ),
        LLMUserMessage(
            content=get_user_prompt(content, n_slides, language, additional_context),
        ),
    ]


async def generate_ppt_outline(
    content: str,
    n_slides: int,
    language: Optional[str] = None,
    additional_context: Optional[str] = None,
    tone: Optional[str] = None,
    verbosity: Optional[str] = None,
    instructions: Optional[str] = None,
    include_title_slide: bool = True,
    web_search: bool = False,
):
    response_model = get_presentation_outline_model_with_n_slides(n_slides)
    
    # Create the prompt for outline generation
    system_prompt = get_system_prompt(
        tone, verbosity, instructions, include_title_slide
    )
    user_prompt = get_user_prompt(content, n_slides, language, additional_context)
    
    # Combine system and user prompts
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    # Add web search instruction if needed
    if web_search:
        full_prompt += "\n\n**Search web to get latest information about the topic**"

    try:
        async for chunk in stream_structured(
            full_prompt,
            response_model.model_json_schema(),
        ):
            yield chunk
    except Exception as e:
        yield handle_llm_client_exceptions(e)
