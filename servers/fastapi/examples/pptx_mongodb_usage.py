"""
Example usage of MongoDB PPTX storage system
"""

import asyncio
from services.gridfs_service import get_gridfs_service
from services.binary_storage_service import get_binary_storage_service
from utils.export_utils import export_presentation

async def example_usage():
    """Example of how to use the MongoDB PPTX storage system"""
    
    # Example 1: Save PPTX file to GridFS (for large files)
    print("=== GridFS Example ===")
    try:
        gridfs_service = get_gridfs_service()
        asset_id = await gridfs_service.save_pptx_file(
            file_path="/path/to/your/presentation.pptx",
            filename="my_presentation.pptx",
            user_id="user123",
            presentation_id="presentation456",
            metadata={
                "title": "My Awesome Presentation",
                "description": "A presentation about MongoDB storage",
                "tags": ["mongodb", "storage", "pptx"]
            }
        )
        print(f"PPTX saved to GridFS with Asset ID: {asset_id}")
        
        # Retrieve the file
        file_content = await gridfs_service.get_pptx_file(asset_id)
        print(f"Retrieved file content: {len(file_content)} bytes")
        
    except Exception as e:
        print(f"GridFS example failed: {e}")
    
    # Example 2: Save PPTX file as binary (for smaller files)
    print("\n=== Binary Storage Example ===")
    try:
        binary_service = get_binary_storage_service()
        asset_id = await binary_service.save_pptx_file(
            file_path="/path/to/your/small_presentation.pptx",
            filename="small_presentation.pptx",
            user_id="user123",
            presentation_id="presentation789",
            metadata={
                "title": "Small Presentation",
                "description": "A small presentation stored as binary"
            }
        )
        print(f"PPTX saved as binary with Asset ID: {asset_id}")
        
        # Retrieve the file
        file_content = await binary_storage_service.get_pptx_file(asset_id)
        print(f"Retrieved file content: {len(file_content)} bytes")
        
    except Exception as e:
        print(f"Binary storage example failed: {e}")
    
    # Example 3: Export presentation with MongoDB storage
    print("\n=== Export with MongoDB Storage ===")
    try:
        presentation_and_path = await export_presentation(
            presentation_id="presentation123",
            title="My Exported Presentation",
            export_as="pptx",
            user_id="user123",
            save_to_mongodb=True
        )
        print(f"Presentation exported and saved to MongoDB: {presentation_and_path.path}")
        
    except Exception as e:
        print(f"Export with MongoDB storage failed: {e}")

# API Endpoints Usage Examples
"""
# Download PPTX file
GET /api/v1/ppt/pptx/{asset_id}/download

# Get user's PPTX files
GET /api/v1/ppt/pptx/user/{user_id}?skip=0&limit=100

# Get PPTX files for a presentation
GET /api/v1/ppt/pptx/presentation/{presentation_id}

# Delete PPTX file
DELETE /api/v1/ppt/pptx/{asset_id}

# Get PPTX file info
GET /api/v1/ppt/pptx/{asset_id}/info
"""

if __name__ == "__main__":
    asyncio.run(example_usage())
