#!/usr/bin/env python3

import sys
sys.path.append('servers/fastapi')
from utils.user_config import update_env_with_user_config
from utils.llm_calls.generate_presentation_outlines import generate_ppt_outline
import asyncio

async def test_outlines():
    # Update environment with user config
    update_env_with_user_config()
    
    print('Testing outlines generation...')
    
    try:
        outline_text = ''
        async for chunk in generate_ppt_outline(
            content='AI in Humans',
            n_slides=1,
            language='English',
            additional_context='',
            tone='default',
            verbosity='standard',
            instructions=None,
            include_title_slide=False,
            web_search=False
        ):
            outline_text += chunk
            print('Chunk received:', chunk[:100] + '...' if len(chunk) > 100 else chunk)
        
        print('\nFull outline text:')
        print(outline_text)
        
        # Test JSON extraction
        json_text = outline_text.strip()
        if json_text.startswith('```json'):
            json_text = json_text[7:]
            if json_text.endswith('```'):
                json_text = json_text[:-3]
            json_text = json_text.strip()
        elif json_text.startswith('```'):
            json_text = json_text[3:]
            if json_text.endswith('```'):
                json_text = json_text[:-3]
            json_text = json_text.strip()
        
        print('\nExtracted JSON:')
        print(json_text[:200] + '...' if len(json_text) > 200 else json_text)
        
    except Exception as e:
        print('Error:', e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_outlines())
