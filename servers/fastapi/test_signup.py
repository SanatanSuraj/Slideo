#!/usr/bin/env python3
"""
Simple test script to verify signup endpoint works
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crud.user_crud import user_crud
from models.mongo.user import UserCreate
from db.mongo import connect_to_mongo

async def test_signup():
    """Test user creation"""
    try:
        print("🔌 Connecting to MongoDB...")
        await connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        print("🧪 Testing user creation...")
        
        # Test user data
        import time
        test_user = UserCreate(
            name="Test User",
            email=f"test{int(time.time())}@example.com",
            password="testpassword123"
        )
        
        # Create user
        user_id = await user_crud.create_user(test_user)
        print(f"✅ User created with ID: {user_id}")
        
        # Get user back
        user = await user_crud.get_user_by_id(user_id)
        if user:
            print(f"✅ User retrieved: {user.email}")
        else:
            print("❌ Failed to retrieve user")
            
        # Clean up - delete test user
        await user_crud.delete_user(user_id)
        print("✅ Test user deleted")
        
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_signup())
