import os
import uuid
import base64
from typing import Optional
from datetime import datetime
from db.mongo import get_database
from models.mongo.asset import AssetCreate
from crud.asset_crud import asset_crud
import logging

logger = logging.getLogger(__name__)

class BinaryStorageService:
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
            self._collection = self.db.pptx_binary_files
        return self._collection
    
    async def save_pptx_file(
        self, 
        file_path: str, 
        filename: str, 
        user_id: str,
        presentation_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Save PPTX file as binary data in MongoDB
        
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
            
            # Check if file is too large (MongoDB document limit is 16MB)
            if file_size > 15 * 1024 * 1024:  # 15MB limit for safety
                raise ValueError(f"File too large ({file_size} bytes). Use GridFS for files larger than 15MB.")
            
            # Encode binary data as base64
            file_content_b64 = base64.b64encode(file_content).decode('utf-8')
            
            # Generate unique ID
            file_id = str(uuid.uuid4())
            
            # Save binary data to MongoDB
            binary_doc = {
                "_id": file_id,
                "user_id": user_id,
                "filename": filename,
                "file_content": file_content_b64,
                "file_size": file_size,
                "presentation_id": presentation_id,
                "created_at": datetime.utcnow(),
                "metadata": metadata or {}
            }
            
            await self.collection.insert_one(binary_doc)
            
            # Create asset record
            asset_data = AssetCreate(
                user_id=user_id,
                filename=filename,
                file_path=file_id,  # Store document ID as path
                file_size=file_size,
                mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                asset_type="pptx",
                metadata={
                    "binary_file_id": file_id,
                    "presentation_id": presentation_id,
                    "original_filename": filename,
                    "storage_type": "binary",
                    **(metadata or {})
                }
            )
            
            asset_id = await asset_crud.create_asset(asset_data)
            
            logger.info(f"PPTX file saved as binary: {filename} (Asset ID: {asset_id})")
            return asset_id
            
        except Exception as e:
            logger.error(f"Failed to save PPTX file as binary: {e}")
            raise
    
    async def get_pptx_file(self, asset_id: str) -> Optional[bytes]:
        """
        Retrieve PPTX file from binary storage
        
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
            
            # Get binary file ID from metadata
            binary_file_id = asset.metadata.get("binary_file_id")
            if not binary_file_id:
                return None
            
            # Get binary document
            binary_doc = await self.collection.find_one({"_id": binary_file_id})
            if not binary_doc:
                return None
            
            # Decode base64 content
            file_content_b64 = binary_doc["file_content"]
            file_content = base64.b64decode(file_content_b64)
            
            return file_content
            
        except Exception as e:
            logger.error(f"Failed to retrieve PPTX file from binary storage: {e}")
            return None
    
    async def delete_pptx_file(self, asset_id: str) -> bool:
        """
        Delete PPTX file from binary storage and asset record
        
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
            
            # Get binary file ID from metadata
            binary_file_id = asset.metadata.get("binary_file_id")
            if binary_file_id:
                # Delete binary document
                await self.collection.delete_one({"_id": binary_file_id})
            
            # Delete asset record
            await asset_crud.delete_asset(asset_id)
            
            logger.info(f"PPTX file deleted from binary storage: {asset_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete PPTX file from binary storage: {e}")
            return False

# Global instance - lazy loaded
_binary_storage_service_instance = None

def get_binary_storage_service() -> BinaryStorageService:
    global _binary_storage_service_instance
    if _binary_storage_service_instance is None:
        _binary_storage_service_instance = BinaryStorageService()
    return _binary_storage_service_instance

# For backward compatibility
binary_storage_service = get_binary_storage_service()
