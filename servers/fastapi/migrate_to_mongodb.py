#!/usr/bin/env python3
"""
Migration script to move from SQLite/SQLModel to MongoDB
This script helps migrate existing data and clean up old database files
"""

import asyncio
import os
import shutil
from pathlib import Path

async def cleanup_old_database_files():
    """Remove old database files and directories"""
    print("🧹 Cleaning up old database files...")
    
    # Files and directories to remove
    cleanup_paths = [
        "./app_data/fastapi.db",
        "./app_data/container.db", 
        "./chroma/",
        "./app_data/chroma/",
        "./servers/fastapi/app_data/",
        "./servers/fastapi/chroma/"
    ]
    
    for path in cleanup_paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f"✅ Removed directory: {path}")
            else:
                os.remove(path)
                print(f"✅ Removed file: {path}")
        else:
            print(f"ℹ️  Path not found: {path}")

def update_gitignore():
    """Update .gitignore to exclude MongoDB data"""
    gitignore_path = ".gitignore"
    
    # MongoDB-specific entries to add
    mongodb_entries = [
        "",
        "# MongoDB",
        "*.db",
        "data/",
        "mongodb-data/",
        ".env.local"
    ]
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            content = f.read()
        
        # Add MongoDB entries if not already present
        for entry in mongodb_entries:
            if entry and entry not in content:
                content += f"\n{entry}"
        
        with open(gitignore_path, "w") as f:
            f.write(content)
        print("✅ Updated .gitignore")
    else:
        print("ℹ️  .gitignore not found, skipping update")

def create_mongodb_directories():
    """Create necessary directories for MongoDB"""
    print("📁 Creating MongoDB directories...")
    
    directories = [
        "./data",
        "./data/mongodb",
        "./logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

async def main():
    """Main migration function"""
    print("🚀 Starting MongoDB migration...")
    print("=" * 50)
    
    # Step 1: Clean up old database files
    await cleanup_old_database_files()
    
    # Step 2: Create new directories
    create_mongodb_directories()
    
    # Step 3: Update .gitignore
    update_gitignore()
    
    print("=" * 50)
    print("✅ Migration completed!")
    print("\n📋 Next steps:")
    print("1. Install MongoDB dependencies: pip install -r requirements.txt")
    print("2. Start MongoDB: mongod --dbpath ./data/mongodb")
    print("3. Update your .env file with MongoDB connection string")
    print("4. Start the FastAPI server: uvicorn api.main:app --reload")
    print("\n🔧 Environment variables to set:")
    print("MONGODB_URI=mongodb://localhost:27017")
    print("MONGODB_DATABASE=presenton")
    print("JWT_SECRET=your-secret-key-here")

if __name__ == "__main__":
    asyncio.run(main())
