from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from models.mongo.asset import Asset, AssetCreate, AssetUpdate, AssetInDB
from db.mongo import get_assets_collection

class AssetCRUD:
    def __init__(self):
        self._collection = None
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = get_assets_collection()
        return self._collection
    
    async def create_asset(self, asset: AssetCreate) -> str:
        """Create a new asset"""
        asset_data = {
            "user_id": asset.user_id,
            "filename": asset.filename,
            "file_path": asset.file_path,
            "file_size": asset.file_size,
            "mime_type": asset.mime_type,
            "asset_type": asset.asset_type,
            "metadata": asset.metadata,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.collection.insert_one(asset_data)
        return str(result.inserted_id)
    
    async def get_asset_by_id(self, asset_id: str) -> Optional[AssetInDB]:
        """Get asset by ID"""
        asset_data = await self.collection.find_one({"_id": ObjectId(asset_id)})
        if asset_data:
            asset_data["id"] = str(asset_data["_id"])
            del asset_data["_id"]
            return AssetInDB(**asset_data)
        return None
    
    async def get_assets_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[AssetInDB]:
        """Get assets by user ID"""
        cursor = self.collection.find({"user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
        assets = []
        async for asset_data in cursor:
            asset_data["id"] = str(asset_data["_id"])
            del asset_data["_id"]
            assets.append(AssetInDB(**asset_data))
        return assets
    
    async def get_assets_by_type(self, user_id: str, asset_type: str, skip: int = 0, limit: int = 100) -> List[AssetInDB]:
        """Get assets by type"""
        cursor = self.collection.find({
            "user_id": user_id,
            "asset_type": asset_type
        }).skip(skip).limit(limit).sort("created_at", -1)
        
        assets = []
        async for asset_data in cursor:
            asset_data["id"] = str(asset_data["_id"])
            del asset_data["_id"]
            assets.append(AssetInDB(**asset_data))
        return assets
    
    async def update_asset(self, asset_id: str, asset_update: AssetUpdate) -> Optional[AssetInDB]:
        """Update asset"""
        update_data = asset_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(asset_id)},
                {"$set": update_data}
            )
        return await self.get_asset_by_id(asset_id)
    
    async def delete_asset(self, asset_id: str) -> bool:
        """Delete asset"""
        result = await self.collection.delete_one({"_id": ObjectId(asset_id)})
        return result.deleted_count > 0
    
    async def search_assets(self, user_id: str, query: str, skip: int = 0, limit: int = 100) -> List[AssetInDB]:
        """Search assets by filename"""
        cursor = self.collection.find({
            "user_id": user_id,
            "filename": {"$regex": query, "$options": "i"}
        }).skip(skip).limit(limit).sort("created_at", -1)
        
        assets = []
        async for asset_data in cursor:
            asset_data["id"] = str(asset_data["_id"])
            del asset_data["_id"]
            assets.append(AssetInDB(**asset_data))
        return assets

# Global instance
asset_crud = AssetCRUD()
