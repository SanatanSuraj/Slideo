from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from models.image_prompt import ImagePrompt
from models.mongo.asset import Asset, AssetCreate
from crud.asset_crud import asset_crud
from services.image_generation_service import ImageGenerationService
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
        path=image.path,
        asset_type="image",
        is_uploaded=False
    )
    await asset_crud.create_asset(asset_create)

    return image.path


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
        new_filename = get_file_name_with_random_uuid(file)
        image_path = os.path.join(
            get_images_directory(), os.path.basename(new_filename)
        )

        with open(image_path, "wb") as f:
            f.write(await file.read())

        asset_create = AssetCreate(
            user_id=str(current_user.id),
            path=image_path,
            asset_type="image",
            is_uploaded=True
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

        os.remove(image.path)
        await asset_crud.delete_asset(str(id))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")
