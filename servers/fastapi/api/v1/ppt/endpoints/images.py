from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from models.image_prompt import ImagePrompt
from models.mongo.asset import Asset, AssetCreate
from crud.asset_crud import asset_crud
from services.image_generation_service import ImageGenerationService
from services.s3_service import s3_service
from utils.asset_directory_utils import get_images_directory
import os
import uuid
from utils.file_utils import get_file_name_with_random_uuid
from auth.dependencies import get_current_active_user
from models.mongo.user import User

IMAGES_ROUTER = APIRouter(prefix="/images", tags=["Images"])


@IMAGES_ROUTER.get("/generate")
async def generate_image(
    prompt: str, 
    current_user: User = Depends(get_current_active_user)
):
    images_directory = get_images_directory()
    image_prompt = ImagePrompt(prompt=prompt)
    image_generation_service = ImageGenerationService(images_directory)

    image = await image_generation_service.generate_image(image_prompt)
    if not isinstance(image, Asset):
        return image

    # Save to MongoDB
    asset_create = AssetCreate(
        user_id=str(current_user.id),
        filename=image.filename,
        file_path=image.file_path,
        file_size=image.file_size,
        mime_type=image.mime_type,
        asset_type=image.asset_type,
        metadata=image.metadata
    )
    await asset_crud.create_asset(asset_create)

    return image.file_path


@IMAGES_ROUTER.get("/generated", response_model=List[Asset])
async def get_generated_images(current_user: User = Depends(get_current_active_user)):
    try:
        images = await asset_crud.get_assets_by_user_and_type(str(current_user.id), "image", uploaded=False)
        return images
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve generated images: {str(e)}"
        )


@IMAGES_ROUTER.post("/upload")
async def upload_image(
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Read file content
        file_content = await file.read()
        
        # Get file info
        new_filename = get_file_name_with_random_uuid(file)
        file_size = len(file_content)
        
        # Determine content type
        content_type = file.content_type or "image/jpeg"
        
        try:
            # Upload to S3
            s3_url = s3_service.upload_file_from_bytes(
                file_content, 
                new_filename, 
                content_type
            )
            print(f"✅ IMAGE UPLOAD: Successfully uploaded to S3: {s3_url}")
            
            asset_create = AssetCreate(
                user_id=str(current_user.id),
                filename=new_filename,
                file_path=s3_url,  # Use S3 URL
                file_size=file_size,
                mime_type=content_type,
                asset_type="image",
                is_uploaded=True,
                metadata={"storage": "s3"}
            )
            
        except Exception as s3_error:
            print(f"❌ IMAGE UPLOAD: S3 upload failed: {s3_error}")
            print(f"🔄 IMAGE UPLOAD: Falling back to local storage")
            
            # Fallback to local storage
            image_path = os.path.join(
                get_images_directory(), os.path.basename(new_filename)
            )

            with open(image_path, "wb") as f:
                f.write(file_content)

            # Convert absolute path to relative path for static serving
            from utils.get_env import get_app_data_directory_env
            app_data_dir = get_app_data_directory_env() or "./app_data"
            if not os.path.isabs(app_data_dir):
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
                app_data_dir = os.path.join(project_root, app_data_dir.lstrip("./"))
            
            # Create relative path for static serving
            if image_path.startswith(app_data_dir):
                relative_path = os.path.relpath(image_path, app_data_dir)
                static_path = f"/app_data/{relative_path}"
            else:
                static_path = image_path

            asset_create = AssetCreate(
                user_id=str(current_user.id),
                filename=new_filename,
                file_path=static_path,  # Use local path
                file_size=file_size,
                mime_type=content_type,
                asset_type="image",
                is_uploaded=True,
                metadata={"storage": "local", "s3_error": str(s3_error)}
            )
        
        asset_id = await asset_crud.create_asset(asset_create)
        image_asset = await asset_crud.get_asset_by_id(asset_id)

        return image_asset
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")


@IMAGES_ROUTER.get("/uploaded", response_model=List[Asset])
async def get_uploaded_images(current_user: User = Depends(get_current_active_user)):
    try:
        images = await asset_crud.get_assets_by_user_and_type(str(current_user.id), "image", uploaded=True)
        return images
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve uploaded images: {str(e)}"
        )


@IMAGES_ROUTER.delete("/{id}", status_code=204)
async def delete_uploaded_image_by_id(
    id: uuid.UUID, 
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Fetch the asset to get its actual file path
        image = await asset_crud.get_asset_by_id(str(id))
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Check if user owns the asset
        if image.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to delete this image")

        # Delete file based on storage type
        if s3_service.is_s3_url(image.file_path):
            # Delete from S3
            s3_key = s3_service.extract_s3_key_from_url(image.file_path)
            if s3_key:
                s3_service.delete_file(s3_key)
                print(f"🗑️ IMAGE DELETE: Deleted from S3: {s3_key}")
            else:
                print(f"⚠️ IMAGE DELETE: Could not extract S3 key from URL: {image.file_path}")
        else:
            # Delete local file
            if os.path.exists(image.file_path):
                os.remove(image.file_path)
                print(f"🗑️ IMAGE DELETE: Deleted local file: {image.file_path}")
            else:
                print(f"⚠️ IMAGE DELETE: Local file not found: {image.file_path}")
        
        # Delete from database
        await asset_crud.delete_asset(str(id))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")
