from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from models.mongo.presentation_layout_code import PresentationLayoutCode, PresentationLayoutCodeCreate, PresentationLayoutCodeUpdate, PresentationLayoutCodeInDB
from db.mongo import get_database

class PresentationLayoutCodeCRUD:
    def __init__(self):
        self._db = None
        self._collection = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.db.presentation_layout_codes
        return self._collection
    
    async def create_layout_code(self, layout_code: PresentationLayoutCodeCreate) -> str:
        """Create a new presentation layout code"""
        layout_data = {
            "presentation": layout_code.presentation,
            "layout_id": layout_code.layout_id,
            "layout_name": layout_code.layout_name,
            "layout_code": layout_code.layout_code,
            "fonts": layout_code.fonts,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.collection.insert_one(layout_data)
        return str(result.inserted_id)
    
    async def get_layout_code_by_id(self, layout_id: str) -> Optional[PresentationLayoutCodeInDB]:
        """Get layout code by ID"""
        layout_data = await self.collection.find_one({"_id": ObjectId(layout_id)})
        if layout_data:
            layout_data["id"] = str(layout_data["_id"])
            del layout_data["_id"]
            return PresentationLayoutCodeInDB(**layout_data)
        return None
    
    async def get_layout_codes_by_presentation(self, presentation_id: str) -> List[PresentationLayoutCodeInDB]:
        """Get all layout codes for a presentation"""
        cursor = self.collection.find({"presentation": presentation_id}).sort("created_at", -1)
        layouts = []
        async for layout_data in cursor:
            layout_data["id"] = str(layout_data["_id"])
            del layout_data["_id"]
            layouts.append(PresentationLayoutCodeInDB(**layout_data))
        return layouts
    
    async def get_layout_code_by_presentation_and_layout_id(self, presentation_id: str, layout_id: str) -> Optional[PresentationLayoutCodeInDB]:
        """Get layout code by presentation and layout ID"""
        layout_data = await self.collection.find_one({
            "presentation": presentation_id,
            "layout_id": layout_id
        })
        if layout_data:
            layout_data["id"] = str(layout_data["_id"])
            del layout_data["_id"]
            return PresentationLayoutCodeInDB(**layout_data)
        return None
    
    async def update_layout_code(self, layout_id: str, layout_update: PresentationLayoutCodeUpdate) -> Optional[PresentationLayoutCodeInDB]:
        """Update layout code"""
        update_data = layout_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(layout_id)},
                {"$set": update_data}
            )
        return await self.get_layout_code_by_id(layout_id)
    
    async def delete_layout_code(self, layout_id: str) -> bool:
        """Delete layout code"""
        result = await self.collection.delete_one({"_id": ObjectId(layout_id)})
        return result.deleted_count > 0
    
    async def delete_layout_codes_by_presentation(self, presentation_id: str) -> int:
        """Delete all layout codes for a presentation"""
        result = await self.collection.delete_many({"presentation": presentation_id})
        return result.deleted_count
    
    async def get_presentation_summary(self) -> List[dict]:
        """Get presentation summary with layout counts"""
        pipeline = [
            {
                "$group": {
                    "_id": "$presentation",
                    "layout_count": {"$sum": 1},
                    "last_updated_at": {"$max": "$updated_at"}
                }
            },
            {
                "$sort": {"last_updated_at": -1}
            }
        ]
        
        cursor = self.collection.aggregate(pipeline)
        summaries = []
        async for doc in cursor:
            summaries.append({
                "presentation_id": doc["_id"],
                "layout_count": doc["layout_count"],
                "last_updated_at": doc["last_updated_at"]
            })
        return summaries

# Global instance
presentation_layout_code_crud = PresentationLayoutCodeCRUD()
