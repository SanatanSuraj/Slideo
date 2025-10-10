#!/usr/bin/env python3
"""
Test script to generate an image of "Books in library" with real API key
"""
import asyncio
import os
import sys
import json

# Set environment variables
os.environ['APP_DATA_DIRECTORY'] = '/Users/sanatansuraj/Desktop/presenton/app_data'
os.environ['IMAGE_PROVIDER'] = 'dall-e-3'
# API key should be loaded from .env file or userConfig.json

# Add the FastAPI server path to Python path
sys.path.append('/Users/sanatansuraj/Desktop/presenton/servers/fastapi')

from services.image_generation_service import ImageGenerationService
from models.image_prompt import ImagePrompt
from utils.asset_directory_utils import get_images_directory

async def test_library_image():
    """Test generating an image of books in library"""
    print("📚 Testing Image Generation: Books in Library")
    print("=" * 50)
    
    # Create image generation service
    images_directory = get_images_directory()
    print(f"📁 Images directory: {images_directory}")
    
    service = ImageGenerationService(images_directory)
    print(f"🔧 Image generation function: {service.image_gen_func}")
    print(f"🔧 Is stock provider: {service.is_stock_provider_selected()}")
    
    # Create a test prompt for books in library
    prompt = ImagePrompt(prompt="Books in library")
    print(f"📝 Test prompt: {prompt.prompt}")
    
    try:
        # Generate image
        print(f"\n🖼️ Starting image generation...")
        result = await service.generate_image(prompt)
        
        print(f"\n✅ Image generation completed!")
        print(f"📊 Result type: {type(result)}")
        
        if isinstance(result, str):
            if result.startswith("http"):
                print(f"🌐 Generated HTTP URL: {result}")
            elif os.path.exists(result):
                print(f"📁 Generated local file: {result}")
                print(f"📊 File size: {os.path.getsize(result)} bytes")
                print(f"📊 File exists: ✅")
                print(f"🎉 SUCCESS: Image generated and saved successfully!")
                print(f"📍 Location: {result}")
            else:
                print(f"❌ File not found: {result}")
        else:
            print(f"📦 Generated AssetInDB:")
            print(f"   - Filename: {result.filename}")
            print(f"   - File path: {result.file_path}")
            print(f"   - File size: {result.file_size} bytes")
            print(f"   - MIME type: {result.mime_type}")
            print(f"   - File exists: {'✅' if os.path.exists(result.file_path) else '❌'}")
            
            if os.path.exists(result.file_path):
                print(f"🎉 SUCCESS: Image generated and saved successfully!")
                print(f"📍 Location: {result.file_path}")
            else:
                print(f"❌ ERROR: Generated file does not exist")
                
    except Exception as e:
        print(f"❌ Error during image generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_library_image())
