from datetime import datetime
from typing import Optional, Dict, Any
import json
from models.llm_message import LLMSystemMessage, LLMUserMessage
from models.presentation_layout import SlideLayoutModel
from models.presentation_outline_model import SlideOutlineModel
from services.llm_client import LLMClient
from utils.llm_client_error_handler import handle_llm_client_exceptions
from utils.llm_provider import get_model
from utils.schema_utils import add_field_in_schema, remove_fields_from_schema
from utils.llm_calls.improved_llm_client import improved_llm_client


def get_system_prompt(
    tone: Optional[str] = None,
    verbosity: Optional[str] = None,
    instructions: Optional[str] = None,
):
    return f"""
        You are a presentation generation model.
        Generate slides strictly from the provided outline.

        Rules:
        - Each outline section = one slide.
        - Use the same title and create concise content based on that section.
        - No generic placeholders (like 'Product Overview', 'Market Validation', etc.).
        - Maintain order and logical flow from the outline.
        - Output must be JSON: {{ "slides": [ {{ "title": "", "content": "" }} ] }}.

        {"# User Instructions:" if instructions else ""}
        {instructions or ""}

        {"# Tone:" if tone else ""}
        {tone or ""}

        {"# Verbosity:" if verbosity else ""}
        {verbosity or ""}

        # Steps
        1. Analyze the outline content carefully.
        2. Generate structured slide based STRICTLY on the outline content.
        3. Generate speaker note that is simple, clear, concise and to the point.

        # Critical Requirements
        - Use ONLY the content provided in the outline - do not add generic content
        - Do not generate generic slide titles like "Product Overview", "Market Validation", "Company Traction"
        - Extract the actual title and content from the outline section
        - Maintain the specific information from the outline
        - Slide body should not use words like "This slide", "This presentation"
        - Rephrase the slide body to make it flow naturally while preserving outline content
        - Only use markdown to highlight important points
        - Make sure to follow language guidelines
        - Speaker note should be normal text, not markdown
        - Strictly follow the max and min character limit for every property in the slide
        - Never ever go over the max character limit. Limit your narration to make sure you never go over the max character limit
        - Number of items should not be more than max number of items specified in slide schema. If you have to put multiple points then merge them to obey max number of items
        - Generate content as per the given tone
        - Be very careful with number of words to generate for given field. As generating more than max characters will overflow in the design. So, analyze early and never generate more characters than allowed
        - Do not add emoji in the content
        - Metrics should be in abbreviated form with least possible characters. Do not add long sequence of words for metrics
        - Include relevant statistics, data points, and metrics when available
        - Create engaging, informative content that provides value to the audience
        - Use bullet points and structured formatting for better readability
        - Include specific examples and case studies where relevant
        - For verbosity:
            - If verbosity is 'concise', then generate description as 1/3 or lower of the max character limit. Don't worry if you miss content or context.
            - If verbosity is 'standard', then generate description as 2/3 of the max character limit.
            - If verbosity is 'text-heavy', then generate description as 3/4 or higher of the max character limit. Make sure it does not exceed the max character limit.

        User instructions, tone and verbosity should always be followed and should supercede any other instruction, except for max and min character limit, slide schema and number of items.

        - Provide output in json format and **don't include <parameters> tags**.

        # Image and Icon Output Format
        image: {{
            __image_prompt__: string,
        }}
        icon: {{
            __icon_query__: string,
        }}

    """


def get_user_prompt(outline: str, language: str):
    return f"""
        ## Current Date and Time
        {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        ## Icon Query And Image Prompt Language
        English

        ## Slide Content Language
        {language}

        ## Slide Outline (USE THIS CONTENT ONLY)
        {outline}

        IMPORTANT: Generate slide content based STRICTLY on the outline above. Do not add generic content or placeholder titles.
    """


def get_messages(
    outline: str,
    language: str,
    tone: Optional[str] = None,
    verbosity: Optional[str] = None,
    instructions: Optional[str] = None,
):
    system_prompt = get_system_prompt(tone, verbosity, instructions)
    user_prompt = get_user_prompt(outline, language)
    
    # Debug logging
    print(f"🔍 System Prompt (first 200 chars): {system_prompt[:200]}...")
    print(f"🔍 User Prompt (first 200 chars): {user_prompt[:200]}...")

    return [
        LLMSystemMessage(
            content=system_prompt,
        ),
        LLMUserMessage(
            content=user_prompt,
        ),
    ]


async def get_slide_content_from_type_and_outline(
    slide_layout: SlideLayoutModel,
    outline: SlideOutlineModel,
    language: str,
    tone: Optional[str] = None,
    verbosity: Optional[str] = None,
    instructions: Optional[str] = None,
):
    try:
        # Debug logging
        print(f"🔍 Slide Content Generation Debug:")
        print(f"🔍 Outline content: {outline.content[:100]}...")
        print(f"🔍 Language: {language}")
        print(f"🔍 Tone: {tone}")
        print(f"🔍 Verbosity: {verbosity}")
        print(f"🔍 Slide Layout Schema: {slide_layout.json_schema}")
        
        # Generate content using the layout-specific schema
        response = await generate_slide_content_with_schema(
            slide_layout=slide_layout,
            outline=outline.content,
            language=language,
            tone=tone,
            verbosity=verbosity,
            instructions=instructions
        )
        
        # Validate the response against the schema
        validated_response = validate_slide_content_against_schema(
            content=response,
            schema=slide_layout.json_schema
        )
        
        # Debug the response
        print(f"🔍 Generated slide content: {str(validated_response)[:200]}...")
        print(f"🔍 Validation completed successfully")
        print(f"🔍 Final content type: {type(validated_response)}")
        print(f"🔍 Final content keys: {list(validated_response.keys()) if isinstance(validated_response, dict) else 'Not a dict'}")
        
        # Extract individual slide content if the response contains a slides array
        if isinstance(validated_response, dict) and 'slides' in validated_response:
            slides_array = validated_response['slides']
            if isinstance(slides_array, list) and len(slides_array) > 0:
                # Return the first slide content
                slide_content = slides_array[0]
                print(f"🔍 Extracted individual slide content: {slide_content}")
                return slide_content
            else:
                print(f"🔍 No slides found in response, returning original content")
                return validated_response
        else:
            return validated_response

    except Exception as e:
        raise handle_llm_client_exceptions(e)


async def generate_slide_content_with_schema(
    slide_layout: SlideLayoutModel,
    outline: str,
    language: str,
    tone: Optional[str] = None,
    verbosity: Optional[str] = None,
    instructions: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate slide content using the specific layout schema"""
    
    # Get the schema from the layout
    schema = slide_layout.json_schema
    
    # Create a schema-aware system prompt
    system_prompt = f"""
    You are a presentation generation model.
    Generate slide content strictly from the provided outline and according to the specific schema.

    Rules:
    - Each outline section = one slide.
    - Use the same title and create concise content based on that section.
    - No generic placeholders (like 'Product Overview', 'Market Validation', etc.).
    - Maintain order and logical flow from the outline.
    - Output must match the EXACT schema provided below.

    {"# User Instructions:" if instructions else ""}
    {instructions or ""}

    {"# Tone:" if tone else ""}
    {tone or ""}

    {"# Verbosity:" if verbosity else ""}
    {verbosity or ""}

    # Steps
    1. Analyze the outline content carefully.
    2. Generate structured slide based STRICTLY on the outline content.
    3. Generate speaker note that is simple, clear, concise and to the point.

    # Critical Requirements
    - Use ONLY the content provided in the outline - do not add generic content
    - Do not generate generic slide titles like "Product Overview", "Market Validation", "Company Traction"
    - Extract the actual title and content from the outline section
    - Maintain the specific information from the outline
    - Slide body should not use words like "This slide", "This presentation"
    - Rephrase the slide body to make it flow naturally while preserving outline content
    - Only use markdown to highlight important points
    - Make sure to follow language guidelines
    - Speaker note should be normal text, not markdown
    - Strictly follow the max and min character limit for every property in the slide
    - Never ever go over the max character limit. Limit your narration to make sure you never go over the max character limit
    - Number of items should not be more than max number of items specified in slide schema. If you have to put multiple points then merge them to obey max number of items
    - Generate content as per the given tone
    - Be very careful with number of words to generate for given field. As generating more than max characters will overflow in the design. So, analyze early and never generate more characters than allowed
    - Do not add emoji in the content
    - Metrics should be in abbreviated form with least possible characters. Do not add long sequence of words for metrics
    - Include relevant statistics, data points, and metrics when available
    - Create engaging, informative content that provides value to the audience
    - Use bullet points and structured formatting for better readability
    - Include specific examples and case studies where relevant
    - For verbosity:
        - If verbosity is 'concise', then generate description as 1/3 or lower of the max character limit. Don't worry if you miss content or context.
        - If verbosity is 'standard', then generate description as 2/3 of the max character limit.
        - If verbosity is 'text-heavy', then generate description as 3/4 or higher of the max character limit. Make sure it does not exceed the max character limit.

    User instructions, tone and verbosity should always be followed and should supercede any other instruction, except for max and min character limit, slide schema and number of items.

    - Provide output in json format and **don't include <parameters> tags**.

    # REQUIRED OUTPUT SCHEMA
    You MUST generate content that matches this EXACT schema structure:
    {json.dumps(schema, indent=2)}

    # Image and Icon Output Format
    For image fields, use:
    {{
        "__image_url__": "/static/images/placeholder.jpg",
        "__image_prompt__": "description of the image"
    }}
    
    For icon fields, use:
    {{
        "__icon_url__": "/static/icons/placeholder.svg", 
        "__icon_query__": "description of the icon"
    }}

    IMPORTANT: Your response must be a valid JSON object that matches the schema above exactly.
    """
    
    user_prompt = f"""
    ## Current Date and Time
    {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    ## Icon Query And Image Prompt Language
    English

    ## Slide Content Language
    {language}

    ## Slide Outline (USE THIS CONTENT ONLY)
    {outline}

    IMPORTANT: Generate slide content based STRICTLY on the outline above. Do not add generic content or placeholder titles.
    The output must match the schema structure provided in the system prompt.
    """
    
    # Use the original LLM client with schema-based generation
    try:
        # Get the system and user prompts with schema
        system_prompt = get_system_prompt(tone, verbosity, instructions)
        user_prompt = get_user_prompt(outline, language)
        
        # Add schema to the system prompt
        print(f"🔍 SCHEMA DEBUG: {json.dumps(schema, indent=2)}")
        system_prompt += f"""

# CRITICAL: REQUIRED OUTPUT SCHEMA
You MUST generate content that matches this EXACT schema structure. DO NOT use the old format with "slides" array.

REQUIRED SCHEMA:
{json.dumps(schema, indent=2)}

# CRITICAL INSTRUCTIONS:
1. Generate a SINGLE object (not an array with "slides")
2. Include ALL required fields: {list(schema.get('required', []))}
3. For image fields, ALWAYS include:
   {{
       "__image_url__": "/static/images/placeholder.jpg",
       "__image_prompt__": "detailed description of the image"
   }}
4. For icon fields, ALWAYS include:
   {{
       "__icon_url__": "/static/icons/placeholder.svg", 
       "__icon_query__": "description of the icon"
   }}

# EXAMPLE OUTPUT FORMAT:
{{
    "title": "Your slide title",
    "image": {{
        "__image_url__": "/static/images/placeholder.jpg",
        "__image_prompt__": "AI technology and human collaboration"
    }},
    "bulletPoints": [
        {{
            "title": "Point 1",
            "icon": {{
                "__icon_url__": "/static/icons/placeholder.svg",
                "__icon_query__": "technology icon"
            }}
        }}
    ]
}}

IMPORTANT: Your response must be a valid JSON object that matches the schema above exactly. DO NOT use the old "slides" array format.
"""

        # Use the original LLM client with schema-aware prompts
        from services.llm_client import LLMSystemMessage, LLMUserMessage
        from utils.llm_provider import get_model
        
        messages = [
            LLMSystemMessage(content=system_prompt),
            LLMUserMessage(content=user_prompt)
        ]
        
        response = await improved_llm_client.llm_client.generate(
            model=get_model(),
            messages=messages,
            max_tokens=4000
        )
        
        try:
            parsed_response = json.loads(response)
            print(f"🔍 Schema-based response parsed successfully: {parsed_response}")
            return parsed_response
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed_json = json.loads(json_match.group())
                print(f"🔍 Extracted JSON from response: {parsed_json}")
                return parsed_json
            else:
                raise ValueError(f"Failed to parse JSON response: {response}")
            
    except Exception as e:
        print(f"🔍 Error in schema-aware generation: {str(e)}")
        # Fallback to the original method
        return await improved_llm_client.generate_slide_content(
            outline=outline,
            language=language,
            tone=tone,
            verbosity=verbosity,
            instructions=instructions
        )


def validate_slide_content_against_schema(content: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and fix slide content against the template schema"""
    try:
        print(f"🔍 Validating content: {content}")
        print(f"🔍 Against schema: {schema}")
        
        # Clean the content first - remove any unwanted fields
        cleaned_content = _clean_content(content)
        print(f"🔍 Cleaned content: {cleaned_content}")
        
        # Basic validation - check if required fields exist
        required_fields = _extract_required_fields_from_schema(schema)
        missing_fields = []
        
        for field in required_fields:
            if field not in cleaned_content:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"🔍 Missing required fields: {missing_fields}")
            # Add default values for missing fields
            cleaned_content = _add_default_values_for_missing_fields(cleaned_content, schema, missing_fields)
        
        # Validate field types and constraints
        final_content = _validate_and_fix_field_constraints(cleaned_content, schema)
        
        print(f"🔍 Final validated content: {final_content}")
        return final_content
        
    except Exception as e:
        print(f"🔍 Error validating content against schema: {str(e)}")
        return content


def _clean_content(content: Dict[str, Any]) -> Dict[str, Any]:
    """Clean content by removing unwanted fields and extracting proper JSON"""
    cleaned = {}
    
    # Remove system fields that shouldn't be in the final content
    system_fields = ['__speaker_note__', 'content', 'error', 'raw']
    
    # First, extract JSON from content field if it exists
    if 'content' in content and isinstance(content['content'], str):
        try:
            # Look for JSON in the content string
            import re
            json_match = re.search(r'\{.*\}', content['content'], re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_json = json.loads(json_str)
                # Merge the parsed JSON into cleaned content (this takes priority)
                cleaned.update(parsed_json)
        except (json.JSONDecodeError, AttributeError):
            # If we can't parse JSON, skip this field
            pass
    
    # Then add other fields, but don't override the extracted JSON
    for key, value in content.items():
        if key not in system_fields and key not in cleaned:
            cleaned[key] = value
    
    return cleaned


def _extract_required_fields_from_schema(schema: Dict[str, Any]) -> list:
    """Extract required fields from JSON schema"""
    required_fields = []
    
    if "properties" in schema:
        for field_name, field_schema in schema["properties"].items():
            # Check if field is required (not in anyOf, oneOf, etc.)
            if "default" not in field_schema and "optional" not in str(field_schema):
                required_fields.append(field_name)
    
    return required_fields


def _add_default_values_for_missing_fields(content: Dict[str, Any], schema: Dict[str, Any], missing_fields: list) -> Dict[str, Any]:
    """Add default values for missing required fields"""
    if "properties" in schema:
        for field_name in missing_fields:
            if field_name in schema["properties"]:
                field_schema = schema["properties"][field_name]
                if "default" in field_schema:
                    content[field_name] = field_schema["default"]
                else:
                    # Generate a basic default based on field type
                    if "string" in str(field_schema.get("type", "")):
                        content[field_name] = f"Default {field_name}"
                    elif "array" in str(field_schema.get("type", "")):
                        content[field_name] = []
                    elif "object" in str(field_schema.get("type", "")):
                        content[field_name] = {}
                    else:
                        content[field_name] = ""
    
    return content


def _validate_and_fix_field_constraints(content: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and fix field constraints like min/max length"""
    if "properties" in schema:
        for field_name, field_schema in schema["properties"].items():
            if field_name in content:
                # Check string length constraints
                if "minLength" in field_schema and len(str(content[field_name])) < field_schema["minLength"]:
                    # Pad with default content if too short
                    content[field_name] = str(content[field_name]) + " " * (field_schema["minLength"] - len(str(content[field_name])))
                
                if "maxLength" in field_schema and len(str(content[field_name])) > field_schema["maxLength"]:
                    # Truncate if too long
                    content[field_name] = str(content[field_name])[:field_schema["maxLength"]]
                
                # Check array length constraints
                if isinstance(content[field_name], list) and "items" in field_schema:
                    if "minItems" in field_schema and len(content[field_name]) < field_schema["minItems"]:
                        # Add default items if array is too short
                        for i in range(field_schema["minItems"] - len(content[field_name])):
                            content[field_name].append(f"Item {i+1}")
                    
                    if "maxItems" in field_schema and len(content[field_name]) > field_schema["maxItems"]:
                        # Truncate array if too long
                        content[field_name] = content[field_name][:field_schema["maxItems"]]
    
    return content
