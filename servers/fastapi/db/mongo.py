from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional

# MongoDB Atlas connection configuration
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "presenton")

# Global MongoDB client and database instances
client: Optional[AsyncIOMotorClient] = None
db = None

async def connect_to_mongo():
    """Create database connection to MongoDB"""
    global client, db
    try:
        # Configure connection options based on URI type
        if "mongodb+srv://" in MONGO_URI:
            # MongoDB Atlas connection
            client = AsyncIOMotorClient(
                MONGO_URI,
                tls=True,
                tlsAllowInvalidCertificates=True,  # For development only
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
        else:
            # Local MongoDB connection
            client = AsyncIOMotorClient(
                MONGO_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
        
        db = client[DATABASE_NAME]
        
        # Test the connection
        await client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {DATABASE_NAME}")
        return db
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("🔌 MongoDB Atlas connection closed")

def get_database():
    """Get database instance"""
    if db is None:
        raise Exception("MongoDB not initialized. Call connect_to_mongo() first.")
    return db

# Collection references
def get_users_collection():
    if db is None:
        raise Exception("MongoDB not initialized. Call connect_to_mongo() first.")
    return db.users

def get_presentations_collection():
    return db.presentations

def get_slides_collection():
    return db.slides

def get_templates_collection():
    return db.templates

def get_tasks_collection():
    return db.tasks

def get_assets_collection():
    return db.assets

def get_vectors_collection():
    return db.vectors

def get_webhooks_collection():
    return db.webhook_subscriptions
