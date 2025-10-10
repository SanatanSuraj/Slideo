from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from models.mongo.final_presentation import (
    FinalPresentation, 
    FinalPresentationCreate, 
    FinalPresentationUpdate,
    FinalPresentationInDB
)
from db.mongo import get_database

class FinalPresentationCRUD:
    def __init__(self):
        self._collection = None
    
    @property
    def collection(self):
        if self._collection is None:
            db = get_database()
            self._collection = db.final_presentations
        return self._collection
    
    async def create_final_presentation(self, final_presentation: FinalPresentationCreate) -> str:
        """Create a new final presentation"""
        # Generate a unique ID for the document
        import uuid
        document_id = str(uuid.uuid4())
        
        final_presentation_data = {
            "id": document_id,
            "presentation_id": final_presentation.presentation_id,
            "user_id": final_presentation.user_id,
            "title": final_presentation.title,
            "description": final_presentation.description,
            "template_id": final_presentation.template_id,
            "slides": final_presentation.slides,
            "layout": final_presentation.layout,
            "structure": final_presentation.structure,
            "outlines": final_presentation.outlines,
            "total_slides": final_presentation.total_slides,
            "language": final_presentation.language,
            "export_format": final_presentation.export_format,
            "thumbnail_url": final_presentation.thumbnail_url,
            "s3_pptx_url": final_presentation.s3_pptx_url,
            "s3_pdf_url": final_presentation.s3_pdf_url,
            "is_published": final_presentation.is_published,
            "is_complete": final_presentation.is_complete,
            "created_at": final_presentation.created_at,
            "updated_at": final_presentation.updated_at,
            "generated_at": final_presentation.generated_at
        }
        
        result = await self.collection.insert_one(final_presentation_data)
        return str(result.inserted_id)
    
    async def get_final_presentation_by_id(self, final_presentation_id: str) -> Optional[FinalPresentationInDB]:
        """Get final presentation by ID"""
        final_presentation_data = await self.collection.find_one({"_id": ObjectId(final_presentation_id)})
        if final_presentation_data:
            final_presentation_data["id"] = str(final_presentation_data["_id"])
            del final_presentation_data["_id"]
            return FinalPresentationInDB(**final_presentation_data)
        return None
    
    async def get_final_presentation_by_presentation_id(self, presentation_id: str) -> Optional[FinalPresentationInDB]:
        """Get final presentation by original presentation ID"""
        final_presentation_data = await self.collection.find_one({"presentation_id": presentation_id})
        if final_presentation_data:
            final_presentation_data["id"] = str(final_presentation_data["_id"])
            del final_presentation_data["_id"]
            return FinalPresentationInDB(**final_presentation_data)
        return None
    
    async def get_final_presentations_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[FinalPresentationInDB]:
        """Get final presentations by user ID"""
        cursor = self.collection.find({"user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
        final_presentations = []
        async for final_presentation_data in cursor:
            final_presentation_data["id"] = str(final_presentation_data["_id"])
            del final_presentation_data["_id"]
            final_presentations.append(FinalPresentationInDB(**final_presentation_data))
        return final_presentations
    
    async def update_final_presentation(self, final_presentation_id: str, final_presentation_update: FinalPresentationUpdate) -> Optional[FinalPresentationInDB]:
        """Update a final presentation"""
        update_data = final_presentation_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_final_presentation_by_id(final_presentation_id)
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(final_presentation_id)},
            {"$set": update_data}
        )
        
        if result.modified_count:
            return await self.get_final_presentation_by_id(final_presentation_id)
        return None
    
    async def delete_final_presentation(self, final_presentation_id: str) -> bool:
        """Delete a final presentation"""
        result = await self.collection.delete_one({"_id": ObjectId(final_presentation_id)})
        return result.deleted_count > 0
    
    async def search_final_presentations(self, user_id: str, query: str, skip: int = 0, limit: int = 100) -> List[FinalPresentationInDB]:
        """Search final presentations by title or description"""
        search_filter = {
            "user_id": user_id,
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
        }
        
        cursor = self.collection.find(search_filter).skip(skip).limit(limit).sort("created_at", -1)
        final_presentations = []
        async for final_presentation_data in cursor:
            final_presentation_data["id"] = str(final_presentation_data["_id"])
            del final_presentation_data["_id"]
            final_presentations.append(FinalPresentationInDB(**final_presentation_data))
        return final_presentations
    
    async def get_published_final_presentations(self, skip: int = 0, limit: int = 100) -> List[FinalPresentationInDB]:
        """Get published final presentations"""
        cursor = self.collection.find({"is_published": True}).skip(skip).limit(limit).sort("created_at", -1)
        final_presentations = []
        async for final_presentation_data in cursor:
            final_presentation_data["id"] = str(final_presentation_data["_id"])
            del final_presentation_data["_id"]
            final_presentations.append(FinalPresentationInDB(**final_presentation_data))
        return final_presentations

# Create global instance
final_presentation_crud = FinalPresentationCRUD()
