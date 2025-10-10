import asyncio
import os
import aiohttp
from google import genai
from google.genai.types import GenerateContentConfig
from openai import AsyncOpenAI
from models.image_prompt import ImagePrompt
from models.mongo.asset import AssetInDB
from utils.download_helpers import download_file
from utils.get_env import get_pexels_api_key_env
from utils.get_env import get_pixabay_api_key_env
from utils.image_provider import (
    is_pixels_selected,
    is_pixabay_selected,
    is_gemini_flash_selected,
    is_dalle3_selected,
)
from services.s3_service import s3_service
import uuid


class ImageGenerationService:

    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        self.image_gen_func = self.get_image_gen_func()

    def get_image_gen_func(self):
        if is_pixabay_selected():
            return self.get_image_from_pixabay
        elif is_pixels_selected():
            return self.get_image_from_pexels
        elif is_gemini_flash_selected():
            return self.generate_image_google
        elif is_dalle3_selected():
            return self.generate_image_openai
        return None

    def is_stock_provider_selected(self):
        return is_pixels_selected() or is_pixabay_selected()

    async def generate_image(self, prompt: ImagePrompt) -> str | AssetInDB:
        """
        Generates an image based on the provided prompt.
        - If no image generation function is available, returns a placeholder image.
        - If the stock provider is selected, it uses the prompt directly,
        otherwise it uses the full image prompt with theme.
        - Output Directory is used for saving the generated image not the stock provider.
        """
        print(f"🖼️ IMAGE GENERATION: Starting image generation for prompt: {prompt.prompt}")
        print(f"🖼️ IMAGE GENERATION: Image generation function available: {self.image_gen_func is not None}")
        print(f"🖼️ IMAGE GENERATION: Output directory: {self.output_directory}")
        
        if not self.image_gen_func:
            print("❌ IMAGE GENERATION: No image generation function found. Using placeholder image.")
            return "/static/images/placeholder.jpg"

        image_prompt = prompt.get_image_prompt(
            with_theme=not self.is_stock_provider_selected()
        )
        print(f"🖼️ IMAGE GENERATION: Final image prompt: {image_prompt}")
        print(f"🖼️ IMAGE GENERATION: Is stock provider: {self.is_stock_provider_selected()}")

        try:
            if self.is_stock_provider_selected():
                print(f"🖼️ IMAGE GENERATION: Using stock provider")
                image_path = await self.image_gen_func(image_prompt)
            else:
                print(f"🖼️ IMAGE GENERATION: Using AI generation with output directory: {self.output_directory}")
                image_path = await self.image_gen_func(
                    image_prompt, self.output_directory
                )
            
            print(f"🖼️ IMAGE GENERATION: Generated image path: {image_path}")
            
            if image_path:
                if image_path.startswith("http"):
                    print(f"🖼️ IMAGE GENERATION: Returning HTTP URL: {image_path}")
                    return image_path
                elif os.path.exists(image_path):
                    print(f"🖼️ IMAGE GENERATION: Image file exists, uploading to S3")
                    from datetime import datetime
                    
                    try:
                        # Upload to S3
                        s3_url = s3_service.upload_file(image_path)
                        print(f"🖼️ IMAGE GENERATION: Successfully uploaded to S3: {s3_url}")
                        
                        # Get file info
                        file_size = os.path.getsize(image_path)
                        filename = os.path.basename(image_path)
                        mime_type = "image/png"  # DALL-E 3 generates PNG images
                        
                        # Clean up local file after successful upload
                        try:
                            os.remove(image_path)
                            print(f"🗑️ IMAGE GENERATION: Cleaned up local file: {image_path}")
                        except Exception as e:
                            print(f"⚠️ IMAGE GENERATION: Failed to clean up local file: {e}")
                        
                        asset = AssetInDB(
                            filename=filename,
                            file_path=s3_url,  # Use S3 URL instead of local path
                            file_size=file_size,
                            mime_type=mime_type,
                            asset_type="image",
                            user_id="system",  # Will be updated when saved to DB
                            created_at=datetime.now(),
                            updated_at=datetime.now(),
                            metadata={
                                "prompt": prompt.prompt,
                                "theme_prompt": prompt.theme_prompt,
                                "storage": "s3",
                            },
                        )
                        print(f"🖼️ IMAGE GENERATION: Created asset: {asset.filename} at {asset.file_path}")
                        return asset
                        
                    except Exception as s3_error:
                        print(f"❌ IMAGE GENERATION: S3 upload failed: {s3_error}")
                        # Fallback to local storage if S3 fails
                        print(f"🔄 IMAGE GENERATION: Falling back to local storage")
                        
                        # Get file info
                        file_size = os.path.getsize(image_path)
                        filename = os.path.basename(image_path)
                        mime_type = "image/png"
                        
                        # Convert absolute path to relative path for static serving
                        from utils.get_env import get_app_data_directory_env
                        app_data_dir = get_app_data_directory_env() or "./app_data"
                        if not os.path.isabs(app_data_dir):
                            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
                            app_data_dir = os.path.join(project_root, app_data_dir.lstrip("./"))
                        
                        # Create relative path for static serving
                        if image_path.startswith(app_data_dir):
                            relative_path = os.path.relpath(image_path, app_data_dir)
                            static_path = f"/app_data/{relative_path}"
                        else:
                            static_path = image_path
                        
                        asset = AssetInDB(
                            filename=filename,
                            file_path=static_path,
                            file_size=file_size,
                            mime_type=mime_type,
                            asset_type="image",
                            user_id="system",
                            created_at=datetime.now(),
                            updated_at=datetime.now(),
                            metadata={
                                "prompt": prompt.prompt,
                                "theme_prompt": prompt.theme_prompt,
                                "storage": "local",
                                "s3_error": str(s3_error),
                            },
                        )
                        print(f"🖼️ IMAGE GENERATION: Created asset with local fallback: {asset.filename} at {asset.file_path}")
                        return asset
                else:
                    print(f"❌ IMAGE GENERATION: Image file does not exist at: {image_path}")
            raise Exception(f"Image not found at {image_path}")

        except Exception as e:
            print(f"❌ IMAGE GENERATION: Error generating image: {e}")
            import traceback
            traceback.print_exc()
            return "/static/images/placeholder.jpg"

    async def generate_image_openai(self, prompt: str, output_directory: str) -> str:
        from utils.get_env import get_openai_api_key_env
        print(f"🖼️ DALL-E 3: Starting image generation with prompt: {prompt}")
        print(f"🖼️ DALL-E 3: Output directory: {output_directory}")
        
        api_key = get_openai_api_key_env()
        if not api_key or api_key == "your-openai-api-key-here":
            print(f"❌ DALL-E 3: Invalid OpenAI API key")
            raise Exception("OpenAI API key not configured")
        
        print(f"🖼️ DALL-E 3: Using OpenAI API key: {api_key[:10]}...")
        
        client = AsyncOpenAI(api_key=api_key)
        result = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            quality="standard",
            size="1024x1024",
        )
        image_url = result.data[0].url
        print(f"🖼️ DALL-E 3: Generated image URL: {image_url}")
        
        downloaded_path = await download_file(image_url, output_directory)
        print(f"🖼️ DALL-E 3: Downloaded image to: {downloaded_path}")
        return downloaded_path

    async def generate_image_google(self, prompt: str, output_directory: str) -> str:
        client = genai.Client()
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash-image-preview",
            contents=[prompt],
            config=GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
        )

        image_data = None
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image_data = part.inline_data.data
                break

        if image_data is None:
            raise Exception("No image generated from Google Gemini")
        
        # Save to temporary file first
        temp_filename = f"{uuid.uuid4()}.jpg"
        image_path = os.path.join(output_directory, temp_filename)
        
        with open(image_path, "wb") as f:
            f.write(image_data)
        
        return image_path

    async def get_image_from_pexels(self, prompt: str) -> str:
        async with aiohttp.ClientSession(trust_env=True) as session:
            response = await session.get(
                f"https://api.pexels.com/v1/search?query={prompt}&per_page=1",
                headers={"Authorization": f"{get_pexels_api_key_env()}"},
            )
            data = await response.json()
            image_url = data["photos"][0]["src"]["large"]
            return image_url

    async def get_image_from_pixabay(self, prompt: str) -> str:
        async with aiohttp.ClientSession(trust_env=True) as session:
            response = await session.get(
                f"https://pixabay.com/api/?key={get_pixabay_api_key_env()}&q={prompt}&image_type=photo&per_page=3"
            )
            data = await response.json()
            image_url = data["hits"][0]["largeImageURL"]
            return image_url
