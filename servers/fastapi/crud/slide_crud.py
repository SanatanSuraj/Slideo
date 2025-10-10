from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from models.mongo.slide import Slide, SlideCreate, SlideUpdate, SlideInDB
from db.mongo import get_slides_collection
import json
import os
from utils.get_env import get_app_data_directory_env

class SlideCRUD:
    def __init__(self):
        self._collection = None
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = get_slides_collection()
        return self._collection
    
    async def create_slide(self, slide: SlideCreate) -> str:
        """Create a new slide"""
        slide_data = {
            "presentation_id": slide.presentation_id,
            "slide_number": slide.slide_number,
            "content": slide.content,
            "layout": slide.layout,
            "layout_group": slide.layout_group,
            "notes": slide.notes,
            "images": slide.images,
            "shapes": slide.shapes,
            "text_boxes": slide.text_boxes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.collection.insert_one(slide_data)
        return str(result.inserted_id)
    
    async def get_slide_by_id(self, slide_id: str) -> Optional[SlideInDB]:
        """Get slide by ID"""
        slide_data = await self.collection.find_one({"_id": ObjectId(slide_id)})
        if slide_data:
            slide_data["id"] = str(slide_data["_id"])
            del slide_data["_id"]
            return SlideInDB(**slide_data)
        return None
    
    async def get_slides_by_presentation(self, presentation_id: str) -> List[SlideInDB]:
        """Get all slides for a presentation"""
        cursor = self.collection.find({"presentation_id": presentation_id}).sort("slide_number", 1)
        slides = []
        async for slide_data in cursor:
            slide_data["id"] = str(slide_data["_id"])
            del slide_data["_id"]
            slides.append(SlideInDB(**slide_data))
        return slides
    
    async def update_slide(self, slide_id: str, slide_update: SlideUpdate) -> Optional[SlideInDB]:
        """Update slide"""
        update_data = slide_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(slide_id)},
                {"$set": update_data}
            )
        return await self.get_slide_by_id(slide_id)
    
    async def delete_slide(self, slide_id: str) -> bool:
        """Delete slide"""
        result = await self.collection.delete_one({"_id": ObjectId(slide_id)})
        return result.deleted_count > 0
    
    async def delete_slides_by_presentation(self, presentation_id: str) -> int:
        """Delete all slides for a presentation"""
        result = await self.collection.delete_many({"presentation_id": presentation_id})
        return result.deleted_count
    
    async def delete_slides_by_ids(self, slide_ids: List[str]) -> int:
        """Delete slides by their IDs"""
        if not slide_ids:
            return 0
        object_ids = [ObjectId(slide_id) for slide_id in slide_ids]
        result = await self.collection.delete_many({"_id": {"$in": object_ids}})
        return result.deleted_count
    
    def _migrate_image_paths_in_content(self, content: str) -> str:
        """Migrate absolute image paths to relative paths in slide content"""
        try:
            # Parse JSON content
            if isinstance(content, str):
                content_dict = json.loads(content)
            else:
                content_dict = content
            
            # Get the app_data directory for path resolution
            app_data_dir = get_app_data_directory_env() or "./app_data"
            if not os.path.isabs(app_data_dir):
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
                app_data_dir = os.path.join(project_root, app_data_dir.lstrip("./"))
            
            # Recursively find and replace image URLs
            def replace_image_paths(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key == "__image_url__" and isinstance(value, str):
                            # Check if it's an S3 URL - leave it as is
                            if "s3.amazonaws.com" in value or "amazonaws.com" in value:
                                print(f"✅ S3 URL preserved: {value}")
                                pass  # Keep S3 URLs unchanged
                            # Check if it's an absolute path that should be converted
                            elif value.startswith(app_data_dir) and "/images/" in value:
                                # Convert to relative path
                                relative_path = os.path.relpath(value, app_data_dir)
                                obj[key] = f"/app_data/{relative_path}"
                                print(f"🔄 MIGRATED: {value} -> {obj[key]}")
                        else:
                            replace_image_paths(value)
                elif isinstance(obj, list):
                    for item in obj:
                        replace_image_paths(item)
            
            replace_image_paths(content_dict)
            
            # Convert back to JSON string
            return json.dumps(content_dict)
            
        except Exception as e:
            print(f"❌ Error migrating image paths: {e}")
            return content  # Return original content if migration fails
    
    async def get_slide_by_id(self, slide_id: str) -> Optional[SlideInDB]:
        """Get slide by ID with path migration"""
        slide_data = await self.collection.find_one({"_id": ObjectId(slide_id)})
        if slide_data:
            slide_data["id"] = str(slide_data["_id"])
            del slide_data["_id"]
            
            # Migrate image paths in content
            if "content" in slide_data and slide_data["content"]:
                slide_data["content"] = self._migrate_image_paths_in_content(slide_data["content"])
            
            return SlideInDB(**slide_data)
        return None
    
    async def get_slides_by_presentation(self, presentation_id: str) -> List[SlideInDB]:
        """Get all slides for a presentation with path migration"""
        cursor = self.collection.find({"presentation_id": presentation_id}).sort("slide_number", 1)
        slides = []
        async for slide_data in cursor:
            slide_data["id"] = str(slide_data["_id"])
            del slide_data["_id"]
            
            # Migrate image paths in content
            if "content" in slide_data and slide_data["content"]:
                slide_data["content"] = self._migrate_image_paths_in_content(slide_data["content"])
            
            slides.append(SlideInDB(**slide_data))
        return slides

# Global instance
slide_crud = SlideCRUD()
