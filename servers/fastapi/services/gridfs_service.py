import os
import uuid
from typing import Optional, BinaryIO
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from db.mongo import get_database
from models.mongo.asset import AssetCreate
from crud.asset_crud import asset_crud
import logging

logger = logging.getLogger(__name__)

class GridFSService:
    def __init__(self):
        self._gridfs = None
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def gridfs(self) -> AsyncIOMotorGridFSBucket:
        if self._gridfs is None:
            self._gridfs = AsyncIOMotorGridFSBucket(self.db, collection="pptx_files")
        return self._gridfs
    
    async def save_pptx_file(
        self, 
        file_path: str, 
        filename: str, 
        user_id: str,
        presentation_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Save PPTX file to GridFS and create asset record
        
        Args:
            file_path: Path to the PPTX file
            filename: Original filename
            user_id: User who owns the file
            presentation_id: Associated presentation ID
            metadata: Additional metadata
            
        Returns:
            Asset ID
        """
        try:
            # Read file content
            with open(file_path, 'rb') as file:
                file_content = file.read()
            
            # Get file size
            file_size = len(file_content)
            
            # Generate unique filename if needed
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Prepare metadata
            gridfs_metadata = {
                "user_id": user_id,
                "presentation_id": presentation_id,
                "original_filename": filename,
                "created_at": datetime.utcnow(),
                "file_type": "pptx",
                **(metadata or {})
            }
            
            # Save to GridFS
            file_id = await self.gridfs.upload_from_stream(
                unique_filename,
                file_content,
                metadata=gridfs_metadata
            )
            
            # Create asset record
            asset_data = AssetCreate(
                user_id=user_id,
                filename=filename,
                file_path=str(file_id),  # Store GridFS file ID as path
                file_size=file_size,
                mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                asset_type="pptx",
                metadata={
                    "gridfs_file_id": str(file_id),
                    "presentation_id": presentation_id,
                    "original_filename": filename,
                    **(metadata or {})
                }
            )
            
            asset_id = await asset_crud.create_asset(asset_data)
            
            logger.info(f"PPTX file saved to GridFS: {filename} (Asset ID: {asset_id})")
            return asset_id
            
        except Exception as e:
            logger.error(f"Failed to save PPTX file to GridFS: {e}")
            raise
    
    async def get_pptx_file(self, asset_id: str) -> Optional[bytes]:
        """
        Retrieve PPTX file from GridFS
        
        Args:
            asset_id: Asset ID
            
        Returns:
            File content as bytes or None if not found
        """
        try:
            # Get asset metadata
            asset = await asset_crud.get_asset_by_id(asset_id)
            if not asset:
                return None
            
            # Get GridFS file ID from metadata
            gridfs_file_id = asset.metadata.get("gridfs_file_id")
            if not gridfs_file_id:
                return None
            
            # Download from GridFS
            grid_out = await self.gridfs.open_download_stream_by_name(
                asset.metadata.get("original_filename", "unknown")
            )
            
            file_content = await grid_out.read()
            return file_content
            
        except Exception as e:
            logger.error(f"Failed to retrieve PPTX file from GridFS: {e}")
            return None
    
    async def delete_pptx_file(self, asset_id: str) -> bool:
        """
        Delete PPTX file from GridFS and asset record
        
        Args:
            asset_id: Asset ID
            
        Returns:
            True if deleted successfully
        """
        try:
            # Get asset metadata
            asset = await asset_crud.get_asset_by_id(asset_id)
            if not asset:
                return False
            
            # Get GridFS file ID from metadata
            gridfs_file_id = asset.metadata.get("gridfs_file_id")
            if gridfs_file_id:
                # Delete from GridFS
                await self.gridfs.delete(gridfs_file_id)
            
            # Delete asset record
            await asset_crud.delete_asset(asset_id)
            
            logger.info(f"PPTX file deleted from GridFS: {asset_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete PPTX file from GridFS: {e}")
            return False
    
    async def get_pptx_files_by_user(self, user_id: str, skip: int = 0, limit: int = 100):
        """Get all PPTX files for a user"""
        return await asset_crud.get_assets_by_type(user_id, "pptx", skip, limit)
    
    async def get_pptx_files_by_presentation(self, presentation_id: str):
        """Get all PPTX files for a specific presentation"""
        collection = asset_crud.collection
        cursor = collection.find({
            "asset_type": "pptx",
            "metadata.presentation_id": presentation_id
        }).sort("created_at", -1)
        
        assets = []
        async for asset_data in cursor:
            asset_data["id"] = str(asset_data["_id"])
            del asset_data["_id"]
            assets.append(asset_data)
        return assets

# Global instance - lazy loaded
_gridfs_service_instance = None

def get_gridfs_service() -> GridFSService:
    global _gridfs_service_instance
    if _gridfs_service_instance is None:
        _gridfs_service_instance = GridFSService()
    return _gridfs_service_instance

# For backward compatibility
gridfs_service = get_gridfs_service()
