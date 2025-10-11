from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse, Response as FastAPIResponse
from typing import List, Optional
from models.mongo.user import User
from auth.dependencies import get_current_active_user
from services.gridfs_service import get_gridfs_service
from services.binary_storage_service import get_binary_storage_service
from crud.asset_crud import asset_crud
import io
import logging

logger = logging.getLogger(__name__)

PPTX_STORAGE_ROUTER = APIRouter()

@PPTX_STORAGE_ROUTER.get("/pptx/{asset_id}/download")
async def download_pptx_file(
    asset_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Download PPTX file from MongoDB storage
    """
    try:
        # Get asset metadata
        asset = await asset_crud.get_asset_by_id(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="PPTX file not found")
        
        # Check if user owns the file
        if asset.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get file content based on storage type
        storage_type = asset.metadata.get("storage_type", "gridfs")
        
        if storage_type == "gridfs":
            gridfs_service = get_gridfs_service()
            file_content = await gridfs_service.get_pptx_file(asset_id)
        else:
            binary_service = get_binary_storage_service()
            file_content = await binary_service.get_pptx_file(asset_id)
        
        if not file_content:
            raise HTTPException(status_code=404, detail="File content not found")
        
        # Sanitize filename for download
        import urllib.parse
        safe_filename = urllib.parse.quote(asset.filename)
        
        # Create response with file content
        return FastAPIResponse(
            content=file_content,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": f"attachment; filename=\"{safe_filename}\""
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download PPTX file: {e}")
        raise HTTPException(status_code=500, detail="Failed to download file")

@PPTX_STORAGE_ROUTER.get("/pptx/{asset_id}/download-temp")
async def download_pptx_file_temp(
    asset_id: str,
    token: str
):
    """
    Download PPTX file from MongoDB storage using temporary token
    """
    try:
        logger.info(f"Download request for asset {asset_id} with token: {token[:20]}...")
        
        # Verify the token
        from auth.jwt_handler import verify_token
        try:
            payload = verify_token(token)
            user_id = payload.get("sub")
            if not user_id:
                logger.error("Token verification failed: no user_id in payload")
                raise HTTPException(status_code=401, detail="Invalid token")
            logger.info(f"Token verified for user: {user_id}")
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        # Get asset metadata
        asset = await asset_crud.get_asset_by_id(asset_id)
        if not asset:
            logger.error(f"Asset not found: {asset_id}")
            raise HTTPException(status_code=404, detail="PPTX file not found")
        
        logger.info(f"Asset found: {asset_id}, owner: {asset.user_id}, requester: {user_id}")
        
        # Check if user owns the file
        if asset.user_id != user_id:
            logger.error(f"Access denied: asset owner {asset.user_id} != requester {user_id}")
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get file content based on storage type
        storage_type = asset.metadata.get("storage_type", "gridfs")
        
        if storage_type == "gridfs":
            gridfs_service = get_gridfs_service()
            file_content = await gridfs_service.get_pptx_file(asset_id)
        else:
            binary_service = get_binary_storage_service()
            file_content = await binary_service.get_pptx_file(asset_id)
        
        if not file_content:
            raise HTTPException(status_code=404, detail="File content not found")
        
        # Sanitize filename for download
        import urllib.parse
        safe_filename = urllib.parse.quote(asset.filename)
        
        # Create response with file content
        return FastAPIResponse(
            content=file_content,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": f"attachment; filename=\"{safe_filename}\""
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download PPTX file: {e}")
        raise HTTPException(status_code=500, detail="Failed to download file")

@PPTX_STORAGE_ROUTER.get("/pptx/user/{user_id}")
async def get_user_pptx_files(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all PPTX files for a user
    """
    try:
        # Check if user is accessing their own files
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        gridfs_service = get_gridfs_service()
        files = await gridfs_service.get_pptx_files_by_user(user_id, skip, limit)
        return {"files": files, "total": len(files)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user PPTX files: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve files")

@PPTX_STORAGE_ROUTER.get("/pptx/presentation/{presentation_id}")
async def get_presentation_pptx_files(
    presentation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all PPTX files for a specific presentation
    """
    try:
        gridfs_service = get_gridfs_service()
        files = await gridfs_service.get_pptx_files_by_presentation(presentation_id)
        
        # Filter files owned by current user
        user_files = [f for f in files if f.get("user_id") == current_user.id]
        
        return {"files": user_files, "total": len(user_files)}
        
    except Exception as e:
        logger.error(f"Failed to get presentation PPTX files: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve files")

@PPTX_STORAGE_ROUTER.delete("/pptx/{asset_id}")
async def delete_pptx_file(
    asset_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete PPTX file from MongoDB storage
    """
    try:
        # Get asset metadata
        asset = await asset_crud.get_asset_by_id(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="PPTX file not found")
        
        # Check if user owns the file
        if asset.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete file based on storage type
        storage_type = asset.metadata.get("storage_type", "gridfs")
        
        if storage_type == "gridfs":
            gridfs_service = get_gridfs_service()
            success = await gridfs_service.delete_pptx_file(asset_id)
        else:
            binary_service = get_binary_storage_service()
            success = await binary_service.delete_pptx_file(asset_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete file")
        
        return {"message": "PPTX file deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete PPTX file: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete file")

@PPTX_STORAGE_ROUTER.get("/pptx/{asset_id}/info")
async def get_pptx_file_info(
    asset_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get PPTX file metadata without downloading the file
    """
    try:
        # Get asset metadata
        asset = await asset_crud.get_asset_by_id(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="PPTX file not found")
        
        # Check if user owns the file
        if asset.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "id": asset.id,
            "filename": asset.filename,
            "file_size": asset.file_size,
            "mime_type": asset.mime_type,
            "created_at": asset.created_at,
            "updated_at": asset.updated_at,
            "metadata": asset.metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get PPTX file info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve file info")
