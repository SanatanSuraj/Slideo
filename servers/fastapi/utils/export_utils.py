import json
import os
import aiohttp
from typing import Literal
import uuid
from fastapi import HTTPException
from pathvalidate import sanitize_filename

from models.pptx_models import PptxPresentationModel
from models.presentation_and_path import PresentationAndPath
from services.pptx_presentation_creator import PptxPresentationCreator
from services.temp_file_service import TEMP_FILE_SERVICE
from services.gridfs_service import get_gridfs_service
from services.binary_storage_service import get_binary_storage_service
from utils.asset_directory_utils import get_exports_directory
import uuid


async def export_presentation(
    presentation_id, title: str, export_as: Literal["pptx", "pdf"], 
    user_id: str = None, save_to_mongodb: bool = True
) -> PresentationAndPath:
    if export_as == "pptx":

        # Get authentication token for PPTX model conversion
        auth_token = None
        if user_id:
            try:
                # Generate a temporary token for PPTX model conversion
                from auth.jwt_handler import create_access_token
                auth_token = create_access_token(data={"sub": user_id}, expires_delta=None)
                print(f"Generated auth token for user {user_id}: {auth_token[:20]}...")
            except Exception as e:
                print(f"Warning: Could not generate auth token for PPTX model conversion: {e}")
        else:
            print("Warning: No user_id provided for token generation")

        # Get the converted PPTX model from the Next.js service
        async with aiohttp.ClientSession() as session:
            pptx_model_url = f"http://localhost:3000/api/presentation_to_pptx_model?id={presentation_id}"
            if auth_token:
                pptx_model_url += f"&token={auth_token}"
            
            async with session.get(pptx_model_url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Failed to get PPTX model: {error_text}")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to convert presentation to PPTX model",
                    )
                pptx_model_data = await response.json()

        # Create PPTX file using the converted model
        pptx_model = PptxPresentationModel(**pptx_model_data)
        temp_dir = TEMP_FILE_SERVICE.create_temp_dir()
        pptx_creator = PptxPresentationCreator(pptx_model, temp_dir)
        await pptx_creator.create_ppt()

        # Generate filename
        filename = f"{sanitize_filename(title or str(uuid.uuid4()))}.pptx"
        
        # Save to local filesystem first
        export_directory = get_exports_directory()
        pptx_path = os.path.join(export_directory, filename)
        pptx_creator.save(pptx_path)

        # Save to MongoDB if requested and user_id provided
        mongodb_path = pptx_path
        if save_to_mongodb and user_id:
            try:
                # Choose storage method based on file size
                file_size = os.path.getsize(pptx_path)
                
                if file_size > 15 * 1024 * 1024:  # Use GridFS for large files
                    gridfs_service = get_gridfs_service()
                    asset_id = await gridfs_service.save_pptx_file(
                        file_path=pptx_path,
                        filename=filename,
                        user_id=user_id,
                        presentation_id=str(presentation_id),
                        metadata={
                            "export_type": "presentation",
                            "file_size": file_size,
                            "created_from": "export"
                        }
                    )
                    mongodb_path = f"mongodb://asset/{asset_id}"
                else:  # Use binary storage for smaller files
                    binary_service = get_binary_storage_service()
                    asset_id = await binary_service.save_pptx_file(
                        file_path=pptx_path,
                        filename=filename,
                        user_id=user_id,
                        presentation_id=str(presentation_id),
                        metadata={
                            "export_type": "presentation",
                            "file_size": file_size,
                            "created_from": "export"
                        }
                    )
                    mongodb_path = f"mongodb://asset/{asset_id}"
                
                print(f"PPTX file saved to MongoDB with Asset ID: {asset_id}")
                
            except Exception as e:
                print(f"Failed to save PPTX to MongoDB: {e}")
                # Continue with local file path if MongoDB save fails

        # Create proper download URL for MongoDB assets
        download_url = None
        if save_to_mongodb and user_id and mongodb_path.startswith("mongodb://asset/"):
            asset_id = mongodb_path.replace("mongodb://asset/", "")
            # Use temporary download endpoint with token
            if auth_token:
                download_url = f"/api/v1/ppt/pptx/{asset_id}/download-temp?token={auth_token}"
                print(f"Created download URL: {download_url}")
            else:
                print("Warning: No auth token available for download URL")
                # Fallback to regular download endpoint (will require authentication)
                download_url = f"/api/v1/ppt/pptx/{asset_id}/download"
        
        return PresentationAndPath(
            presentation_id=str(presentation_id),
            path=mongodb_path,
            s3_pptx_url=download_url if export_as == "pptx" else None,
            s3_pdf_url=mongodb_path if export_as == "pdf" else None,
        )
    else:
        async with aiohttp.ClientSession() as session:
            # Get authentication token for PDF export
            auth_token = None
            if user_id:
                # For now, we'll use a simple approach - in production you might want to 
                # generate a temporary token or use a different authentication method
                try:
                    # Try to get token from environment or generate one
                    auth_token = os.getenv("PDF_EXPORT_TOKEN")
                    if not auth_token:
                        # Generate a temporary token for PDF export
                        from auth.jwt_handler import create_access_token
                        auth_token = create_access_token(data={"sub": user_id}, expires_delta=None)
                except Exception as e:
                    print(f"Warning: Could not generate auth token for PDF export: {e}")
            
            async with session.post(
                "http://localhost:3000/api/export-as-pdf-canvas",
                json={
                    "id": str(presentation_id),
                    "title": sanitize_filename(title or str(uuid.uuid4())),
                    "token": auth_token,
                },
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Failed to export PDF: {error_text}")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to export presentation as PDF",
                    )
                response_json = await response.json()

        return PresentationAndPath(
            presentation_id=str(presentation_id),
            path=response_json["path"],
            s3_pptx_url=None,
            s3_pdf_url=response_json["path"] if export_as == "pdf" else None,
        )
