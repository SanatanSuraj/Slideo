from fastapi import APIRouter, HTTPException
from db.mongo import get_database
import asyncio

router = APIRouter(prefix="/db_status", tags=["Database Status"])

@router.get("/")
async def db_status():
    """Check MongoDB Atlas connection status"""
    try:
        db = get_database()
        
        # Get database stats
        stats = await db.command("dbStats")
        
        # Get collection list
        collections = await db.list_collection_names()
        
        # Test a simple operation
        test_result = await db.command("ping")
        
        return {
            "status": "connected",
            "database": stats.get("db"),
            "collections": collections,
            "ping": test_result,
            "total_size": stats.get("dataSize", 0),
            "indexes": stats.get("indexes", 0),
            "objects": stats.get("objects", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@router.get("/collections")
async def list_collections():
    """List all collections in the database"""
    try:
        db = get_database()
        collections = await db.list_collection_names()
        
        collection_info = []
        for collection_name in collections:
            collection = db[collection_name]
            count = await collection.count_documents({})
            collection_info.append({
                "name": collection_name,
                "count": count
            })
        
        return {
            "collections": collection_info,
            "total_collections": len(collections)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list collections: {str(e)}")

@router.get("/health")
async def health_check():
    """Simple health check for MongoDB Atlas"""
    try:
        db = get_database()
        await db.command("ping")
        return {"status": "healthy", "database": "mongodb_atlas"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
