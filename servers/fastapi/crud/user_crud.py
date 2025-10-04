from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from passlib.context import CryptContext
from models.mongo.user import User, UserCreate, UserUpdate, UserInDB
from db.mongo import get_users_collection

# Use a more compatible password hashing scheme
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

class UserCRUD:
    def __init__(self):
        self._collection = None
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = get_users_collection()
        return self._collection
    
    async def create_user(self, user: UserCreate) -> str:
        """Create a new user"""
        # Handle optional password (for OAuth users)
        if user.password:
            # Truncate password to 72 bytes for bcrypt compatibility
            password_bytes = user.password.encode('utf-8')
            if len(password_bytes) > 72:
                # Truncate to 72 bytes and decode back to string
                password = password_bytes[:72].decode('utf-8', errors='ignore')
            else:
                password = user.password
            hashed_password = pwd_context.hash(password)
        else:
            # For OAuth users or users without passwords, create a random hash
            hashed_password = pwd_context.hash("oauth_user")
        
        user_data = {
            "email": user.email,
            "name": user.name,
            "hashed_password": hashed_password,
            "plan": user.plan,
            "is_active": user.is_active,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        user_data = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user_data:
            user_data["id"] = str(user_data["_id"])
            del user_data["_id"]
            return UserInDB(**user_data)
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        user_data = await self.collection.find_one({"email": email})
        if user_data:
            user_data["id"] = str(user_data["_id"])
            del user_data["_id"]
            return UserInDB(**user_data)
        return None
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[UserInDB]:
        """Update user"""
        update_data = user_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
        return await self.get_user_by_id(user_id)
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        """List users with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        users = []
        async for user_data in cursor:
            user_data["id"] = str(user_data["_id"])
            del user_data["_id"]
            users.append(UserInDB(**user_data))
        return users
    
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user with email and password"""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not await self.verify_password(password, user.hashed_password):
            return None
        return user

# Global instance
user_crud = UserCRUD()
