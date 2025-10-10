from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from models.mongo.presentation_final_edit import (
    PresentationFinalEdit, 
    PresentationFinalEditCreate, 
    PresentationFinalEditUpdate, 
    PresentationFinalEditInDB
)
from db.mongo import get_presentation_final_edits_collection

class PresentationFinalEditCRUD:
    def __init__(self):
        self._collection = None
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = get_presentation_final_edits_collection()
        return self._collection
    
    async def create_presentation_final_edit(self, presentation_final_edit: PresentationFinalEditCreate) -> str:
        """Create a new presentation final edit"""
        # Generate a unique ID for the document
        import uuid
        document_id = str(uuid.uuid4())
        
        presentation_final_edit_data = {
            "id": document_id,  # Add explicit id field
            "presentation_id": presentation_final_edit.presentation_id,
            "user_id": presentation_final_edit.user_id,
            "title": presentation_final_edit.title,
            "template_id": presentation_final_edit.template_id,
            "slides": presentation_final_edit.slides,
            "thumbnail_url": presentation_final_edit.thumbnail_url,
            "s3_pptx_url": presentation_final_edit.s3_pptx_url,
            "s3_pdf_url": presentation_final_edit.s3_pdf_url,
            "is_published": presentation_final_edit.is_published,
            "edited_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.collection.insert_one(presentation_final_edit_data)
        return str(result.inserted_id)
    
    async def get_presentation_final_edit_by_id(self, presentation_final_edit_id: str) -> Optional[PresentationFinalEditInDB]:
        """Get presentation final edit by ID"""
        presentation_final_edit_data = await self.collection.find_one({"_id": ObjectId(presentation_final_edit_id)})
        if presentation_final_edit_data:
            presentation_final_edit_data["id"] = str(presentation_final_edit_data["_id"])
            del presentation_final_edit_data["_id"]
            return PresentationFinalEditInDB(**presentation_final_edit_data)
        return None
    
    async def get_presentation_final_edit_by_presentation_id(self, presentation_id: str) -> Optional[PresentationFinalEditInDB]:
        """Get presentation final edit by presentation ID"""
        presentation_final_edit_data = await self.collection.find_one({"presentation_id": presentation_id})
        if presentation_final_edit_data:
            presentation_final_edit_data["id"] = str(presentation_final_edit_data["_id"])
            del presentation_final_edit_data["_id"]
            return PresentationFinalEditInDB(**presentation_final_edit_data)
        return None
    
    async def get_presentation_final_edits_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[PresentationFinalEditInDB]:
        """Get presentation final edits by user ID"""
        cursor = self.collection.find({"user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
        presentation_final_edits = []
        async for presentation_final_edit_data in cursor:
            presentation_final_edit_data["id"] = str(presentation_final_edit_data["_id"])
            del presentation_final_edit_data["_id"]
            presentation_final_edits.append(PresentationFinalEditInDB(**presentation_final_edit_data))
        return presentation_final_edits
    
    async def get_published_presentation_final_edits(self, skip: int = 0, limit: int = 100) -> List[PresentationFinalEditInDB]:
        """Get all published presentation final edits"""
        cursor = self.collection.find({"is_published": True}).skip(skip).limit(limit).sort("created_at", -1)
        presentation_final_edits = []
        async for presentation_final_edit_data in cursor:
            presentation_final_edit_data["id"] = str(presentation_final_edit_data["_id"])
            del presentation_final_edit_data["_id"]
            presentation_final_edits.append(PresentationFinalEditInDB(**presentation_final_edit_data))
        return presentation_final_edits
    
    async def update_presentation_final_edit(self, presentation_final_edit_id: str, presentation_final_edit_update: PresentationFinalEditUpdate) -> Optional[PresentationFinalEditInDB]:
        """Update presentation final edit"""
        update_data = presentation_final_edit_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(presentation_final_edit_id)},
                {"$set": update_data}
            )
        return await self.get_presentation_final_edit_by_id(presentation_final_edit_id)
    
    async def delete_presentation_final_edit(self, presentation_final_edit_id: str) -> bool:
        """Delete presentation final edit"""
        result = await self.collection.delete_one({"_id": ObjectId(presentation_final_edit_id)})
        return result.deleted_count > 0
    
    async def delete_presentation_final_edit_by_presentation_id(self, presentation_id: str) -> bool:
        """Delete presentation final edit by presentation ID"""
        result = await self.collection.delete_one({"presentation_id": presentation_id})
        return result.deleted_count > 0
    
    async def search_presentation_final_edits(self, user_id: str, query: str, skip: int = 0, limit: int = 100) -> List[PresentationFinalEditInDB]:
        """Search presentation final edits by title or content"""
        search_filter = {
            "user_id": user_id,
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"presentation_id": {"$regex": query, "$options": "i"}}
            ]
        }
        cursor = self.collection.find(search_filter).skip(skip).limit(limit).sort("created_at", -1)
        presentation_final_edits = []
        async for presentation_final_edit_data in cursor:
            presentation_final_edit_data["id"] = str(presentation_final_edit_data["_id"])
            del presentation_final_edit_data["_id"]
            presentation_final_edits.append(PresentationFinalEditInDB(**presentation_final_edit_data))
        return presentation_final_edits

# Create a global instance
presentation_final_edit_crud = PresentationFinalEditCRUD()
