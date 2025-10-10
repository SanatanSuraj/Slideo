from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import urllib.parse
from typing import Optional
from fastapi import HTTPException

# Set up logger
logger = logging.getLogger("uvicorn")

# MongoDB Atlas connection configuration
def get_mongo_uri():
    return os.getenv("MONGODB_URI", "mongodb://localhost:27017")

def get_database_name():
    return os.getenv("MONGODB_DATABASE", "presenton")

def parse_mongodb_uri(uri: str) -> dict:
    """Parse MongoDB URI to extract connection details for logging"""
    try:
        parsed = urllib.parse.urlparse(uri)
        return {
            'scheme': parsed.scheme,
            'hostname': parsed.hostname,
            'port': parsed.port,
            'username': parsed.username,
            'database': parsed.path.lstrip('/') if parsed.path else 'default',
            'has_password': bool(parsed.password)
        }
    except Exception as e:
        logger.warning(f"Could not parse MongoDB URI: {e}")
        return {'error': str(e)}

# Global MongoDB client and database instances
client: Optional[AsyncIOMotorClient] = None
db = None

async def connect_to_mongo():
    """Create database connection to MongoDB"""
    global client, db
    try:
        # Get environment variables
        mongo_uri = get_mongo_uri()
        database_name = get_database_name()
        
        # Parse and log connection details
        connection_details = parse_mongodb_uri(mongo_uri)
        logger.info(f"🔌 Attempting to connect to MongoDB")
        logger.info(f"🔌 Connection type: {connection_details.get('scheme', 'unknown')}")
        logger.info(f"🔌 Hostname: {connection_details.get('hostname', 'unknown')}")
        logger.info(f"🔌 Username: {connection_details.get('username', 'none')}")
        logger.info(f"🔌 Database: {database_name}")
        logger.info(f"🔌 Has password: {'Yes' if connection_details.get('has_password') else 'No'}")
        
        # Configure connection options based on URI type
        if "mongodb+srv://" in mongo_uri:
            # MongoDB Atlas connection
            logger.info("🌐 Using MongoDB Atlas connection")
            logger.info("🌐 Configuring TLS and connection options for Atlas...")
            
            client = AsyncIOMotorClient(
                mongo_uri,
                tls=True,
                tlsAllowInvalidCertificates=True,  # For development only
                serverSelectionTimeoutMS=10000,  # Increased timeout for Atlas
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                retryWrites=True,
                w='majority'
            )
        else:
            # Local MongoDB connection
            logger.info("🏠 Using local MongoDB connection")
            client = AsyncIOMotorClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
        
        db = client[database_name]
        
        # Test the connection with comprehensive error handling
        logger.info("🔍 Testing MongoDB connection...")
        try:
            # First test: Basic ping
            await client.admin.command('ping')
            logger.info("✅ MongoDB ping successful")
            
            # Second test: Server info
            server_info = await client.server_info()
            logger.info("✅ MongoDB connection established successfully.")
            logger.info(f"✅ MongoDB version: {server_info.get('version', 'Unknown')}")
            logger.info(f"✅ MongoDB host: {server_info.get('host', 'Unknown')}")
            logger.info(f"✅ Database: {database_name}")
            
            # Third test: Database access
            collections = await db.list_collection_names()
            logger.info(f"✅ Database access verified - {len(collections)} collections found")
            
        except Exception as auth_error:
            logger.error(f"❌ MongoDB authentication/connection test failed: {auth_error}")
            
            # Provide specific error guidance
            if "bad auth" in str(auth_error).lower() or "authentication failed" in str(auth_error).lower():
                logger.error("🔐 AUTHENTICATION ERROR DETECTED:")
                logger.error("🔐 1. Verify your MongoDB Atlas username and password")
                logger.error("🔐 2. Check that the database user has read/write permissions")
                logger.error("🔐 3. Ensure your IP address is whitelisted in MongoDB Atlas")
                logger.error("🔐 4. Verify the database name in your connection string")
                logger.error(f"🔐 5. Current username: {connection_details.get('username', 'unknown')}")
                logger.error(f"🔐 6. Current database: {database_name}")
            elif "timeout" in str(auth_error).lower():
                logger.error("⏰ CONNECTION TIMEOUT:")
                logger.error("⏰ 1. Check your internet connection")
                logger.error("⏰ 2. Verify your IP is whitelisted in MongoDB Atlas")
                logger.error("⏰ 3. Check firewall settings")
            elif "network" in str(auth_error).lower():
                logger.error("🌐 NETWORK ERROR:")
                logger.error("🌐 1. Check your internet connection")
                logger.error("🌐 2. Verify MongoDB Atlas cluster is running")
                logger.error("🌐 3. Check DNS resolution")
            
            raise HTTPException(status_code=500, detail=f"MongoDB connection failed: {str(auth_error)}")
            
        print(f"✅ Connected to MongoDB: {database_name}")
        return db
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        logger.error(f"❌ Full error: {str(e)}")
        
        # Log connection details for debugging
        mongo_uri = get_mongo_uri()
        database_name = get_database_name()
        connection_details = parse_mongodb_uri(mongo_uri)
        logger.error(f"❌ Connection details:")
        logger.error(f"❌ - URI type: {connection_details.get('scheme', 'unknown')}")
        logger.error(f"❌ - Hostname: {connection_details.get('hostname', 'unknown')}")
        logger.error(f"❌ - Username: {connection_details.get('username', 'unknown')}")
        logger.error(f"❌ - Database: {database_name}")
        
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

def get_presentation_final_edits_collection():
    return db.presentation_final_edits
