from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from models.mongo.slide import Slide, SlideCreate, SlideUpdate, SlideInDB
from db.mongo import get_slides_collection

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

# Global instance
slide_crud = SlideCRUD()
