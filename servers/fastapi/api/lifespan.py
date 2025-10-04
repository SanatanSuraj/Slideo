from contextlib import asynccontextmanager
import os

from fastapi import FastAPI

from db.mongo import connect_to_mongo, close_mongo_connection
from utils.get_env import get_app_data_directory_env
from utils.model_availability import (
    check_llm_and_image_provider_api_or_model_availability,
)


@asynccontextmanager
async def app_lifespan(_: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Initializes the application data directory and connects to MongoDB.

    """
    app_data_dir = get_app_data_directory_env() or "./app_data"
    os.makedirs(app_data_dir, exist_ok=True)
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Temporarily disabled to debug startup issues
    # await check_llm_and_image_provider_api_or_model_availability()
    yield
    
    # Close MongoDB connection
    await close_mongo_connection()
