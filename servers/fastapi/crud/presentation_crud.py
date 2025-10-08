from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from models.mongo.presentation import Presentation, PresentationCreate, PresentationUpdate, PresentationInDB
from db.mongo import get_presentations_collection

class PresentationCRUD:
    def __init__(self):
        self._collection = None
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = get_presentations_collection()
        return self._collection
    
    async def create_presentation(self, presentation: PresentationCreate) -> str:
        """Create a new presentation"""
        # Generate a unique ID for the document
        import uuid
        document_id = str(uuid.uuid4())
        
        presentation_data = {
            "id": document_id,  # Add explicit id field
            "user_id": presentation.user_id,
            "title": presentation.title,
            "content": presentation.content,
            "n_slides": presentation.n_slides,
            "language": presentation.language,
            "file_paths": presentation.file_paths,
            "outlines": presentation.outlines,
            "layout": presentation.layout,
            "structure": presentation.structure,
            "instructions": presentation.instructions,
            "tone": presentation.tone,
            "verbosity": presentation.verbosity,
            "include_table_of_contents": presentation.include_table_of_contents,
            "include_title_slide": presentation.include_title_slide,
            "web_search": presentation.web_search,
            "uuid": presentation.uuid,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.collection.insert_one(presentation_data)
        return str(result.inserted_id)
    
    async def get_presentation_by_id(self, presentation_id: str) -> Optional[PresentationInDB]:
        """Get presentation by ID"""
        presentation_data = await self.collection.find_one({"_id": ObjectId(presentation_id)})
        if presentation_data:
            presentation_data["id"] = str(presentation_data["_id"])
            del presentation_data["_id"]
            return PresentationInDB(**presentation_data)
        return None
    
    async def get_presentations_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[PresentationInDB]:
        """Get presentations by user ID"""
        cursor = self.collection.find({"user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
        presentations = []
        async for presentation_data in cursor:
            presentation_data["id"] = str(presentation_data["_id"])
            del presentation_data["_id"]
            presentations.append(PresentationInDB(**presentation_data))
        return presentations
    
    async def update_presentation(self, presentation_id: str, presentation_update: PresentationUpdate) -> Optional[PresentationInDB]:
        """Update presentation"""
        update_data = presentation_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(presentation_id)},
                {"$set": update_data}
            )
        return await self.get_presentation_by_id(presentation_id)
    
    async def delete_presentation(self, presentation_id: str) -> bool:
        """Delete presentation"""
        result = await self.collection.delete_one({"_id": ObjectId(presentation_id)})
        return result.deleted_count > 0
    
    async def search_presentations(self, user_id: str, query: str, skip: int = 0, limit: int = 100) -> List[PresentationInDB]:
        """Search presentations by title or content"""
        cursor = self.collection.find({
            "user_id": user_id,
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"content": {"$regex": query, "$options": "i"}}
            ]
        }).skip(skip).limit(limit).sort("created_at", -1)
        
        presentations = []
        async for presentation_data in cursor:
            presentation_data["id"] = str(presentation_data["_id"])
            del presentation_data["_id"]
            presentations.append(PresentationInDB(**presentation_data))
        return presentations

# Global instance
presentation_crud = PresentationCRUD()
