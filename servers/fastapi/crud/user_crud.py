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
        # Try to find user by ObjectId first
        try:
            user_data = await self.collection.find_one({"_id": ObjectId(user_id)})
        except:
            user_data = None
        
        # If not found, try to find by string ID (for legacy documents)
        if not user_data:
            user_data = await self.collection.find_one({"_id": user_id})
        
        if user_data:
            user_data["id"] = str(user_data["_id"])
            del user_data["_id"]
            
            # Handle schema compatibility - convert old schema to new schema
            user_data = self._normalize_user_data(user_data)
            
            return UserInDB(**user_data)
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        user_data = await self.collection.find_one({"email": email})
        if user_data:
            user_data["id"] = str(user_data["_id"])
            del user_data["_id"]
            
            # Handle schema compatibility - convert old schema to new schema
            user_data = self._normalize_user_data(user_data)
            
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
            
            # Handle schema compatibility - convert old schema to new schema
            user_data = self._normalize_user_data(user_data)
            
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
    
    def _normalize_user_data(self, user_data: dict) -> dict:
        """Normalize user data to handle schema compatibility between old and new formats"""
        normalized = user_data.copy()
        
        # Handle old schema fields
        if "firstName" in normalized and "lastName" in normalized:
            # Combine firstName and lastName into name
            first_name = normalized.get("firstName", "")
            last_name = normalized.get("lastName", "")
            normalized["name"] = f"{first_name} {last_name}".strip()
            # Remove old fields
            normalized.pop("firstName", None)
            normalized.pop("lastName", None)
        
        # Handle password field mapping
        if "password" in normalized and "hashed_password" not in normalized:
            normalized["hashed_password"] = normalized["password"]
            normalized.pop("password", None)
        
        # Handle date field mapping
        if "createdAt" in normalized and "created_at" not in normalized:
            normalized["created_at"] = normalized["createdAt"]
            normalized.pop("createdAt", None)
        
        if "updatedAt" in normalized and "updated_at" not in normalized:
            normalized["updated_at"] = normalized["updatedAt"]
            normalized.pop("updatedAt", None)
        
        # Handle boolean field mapping
        if "isActive" in normalized and "is_active" not in normalized:
            normalized["is_active"] = normalized["isActive"]
            normalized.pop("isActive", None)
        
        # Ensure required fields have default values if missing
        if "hashed_password" not in normalized:
            normalized["hashed_password"] = pwd_context.hash("default_password")
        
        if "created_at" not in normalized:
            normalized["created_at"] = datetime.utcnow()
        
        if "updated_at" not in normalized:
            normalized["updated_at"] = datetime.utcnow()
        
        if "is_active" not in normalized:
            normalized["is_active"] = True
        
        if "plan" not in normalized:
            normalized["plan"] = "free"
        
        # Remove any extra fields that might cause issues
        extra_fields = ["__v", "lastLogin", "isVerified"]
        for field in extra_fields:
            normalized.pop(field, None)
        
        return normalized

# Global instance
user_crud = UserCRUD()
