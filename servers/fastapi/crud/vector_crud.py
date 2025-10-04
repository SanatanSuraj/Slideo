from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from models.mongo.vector import Vector, VectorCreate, VectorUpdate, VectorInDB
from db.mongo import get_vectors_collection

class VectorCRUD:
    def __init__(self):
        self._collection = None
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = get_vectors_collection()
        return self._collection
    
    async def create_vector(self, vector: VectorCreate) -> str:
        """Create a new vector"""
        vector_data = {
            "user_id": vector.user_id,
            "content": vector.content,
            "embedding": vector.embedding,
            "metadata": vector.metadata,
            "vector_type": vector.vector_type,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.collection.insert_one(vector_data)
        return str(result.inserted_id)
    
    async def get_vector_by_id(self, vector_id: str) -> Optional[VectorInDB]:
        """Get vector by ID"""
        vector_data = await self.collection.find_one({"_id": ObjectId(vector_id)})
        if vector_data:
            vector_data["id"] = str(vector_data["_id"])
            del vector_data["_id"]
            return VectorInDB(**vector_data)
        return None
    
    async def get_vectors_by_type(self, vector_type: str, skip: int = 0, limit: int = 100) -> List[VectorInDB]:
        """Get vectors by type"""
        cursor = self.collection.find({"vector_type": vector_type}).skip(skip).limit(limit)
        vectors = []
        async for vector_data in cursor:
            vector_data["id"] = str(vector_data["_id"])
            del vector_data["_id"]
            vectors.append(VectorInDB(**vector_data))
        return vectors
    
    async def get_vectors_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[VectorInDB]:
        """Get vectors by user ID"""
        cursor = self.collection.find({"user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
        vectors = []
        async for vector_data in cursor:
            vector_data["id"] = str(vector_data["_id"])
            del vector_data["_id"]
            vectors.append(VectorInDB(**vector_data))
        return vectors
    
    async def search_similar_vectors(self, query_embedding: List[float], vector_type: str, limit: int = 10) -> List[VectorInDB]:
        """Search for similar vectors using cosine similarity"""
        # This is a simplified implementation
        # In production, you might want to use a proper vector search index
        cursor = self.collection.find({"vector_type": vector_type}).limit(limit * 2)
        vectors = []
        async for vector_data in cursor:
            vector_data["id"] = str(vector_data["_id"])
            del vector_data["_id"]
            vectors.append(VectorInDB(**vector_data))
        
        # Simple similarity calculation (in production, use proper vector search)
        return vectors[:limit]
    
    async def update_vector(self, vector_id: str, vector_update: VectorUpdate) -> Optional[VectorInDB]:
        """Update vector"""
        update_data = vector_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(vector_id)},
                {"$set": update_data}
            )
        return await self.get_vector_by_id(vector_id)
    
    async def delete_vector(self, vector_id: str) -> bool:
        """Delete vector"""
        result = await self.collection.delete_one({"_id": ObjectId(vector_id)})
        return result.deleted_count > 0
    
    async def delete_vectors_by_user(self, user_id: str) -> int:
        """Delete all vectors for a user"""
        result = await self.collection.delete_many({"user_id": user_id})
        return result.deleted_count

# Global instance
vector_crud = VectorCRUD()
