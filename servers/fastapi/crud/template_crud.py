from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from models.mongo.template import Template, TemplateCreate, TemplateUpdate, TemplateInDB
from db.mongo import get_templates_collection

class TemplateCRUD:
    def __init__(self):
        self._collection = None
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = get_templates_collection()
        return self._collection
    
    async def create_template(self, template: TemplateCreate) -> str:
        """Create a new template"""
        template_data = {
            "user_id": template.user_id,
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "layout": template.layout,
            "structure": template.structure,
            "is_public": template.is_public,
            "tags": template.tags,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.collection.insert_one(template_data)
        return str(result.inserted_id)
    
    async def get_template_by_id(self, template_id: str) -> Optional[TemplateInDB]:
        """Get template by ID"""
        template_data = await self.collection.find_one({"_id": ObjectId(template_id)})
        if template_data:
            template_data["id"] = str(template_data["_id"])
            del template_data["_id"]
            return TemplateInDB(**template_data)
        return None
    
    async def get_templates_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[TemplateInDB]:
        """Get templates by user ID"""
        cursor = self.collection.find({"user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
        templates = []
        async for template_data in cursor:
            template_data["id"] = str(template_data["_id"])
            del template_data["_id"]
            templates.append(TemplateInDB(**template_data))
        return templates
    
    async def get_public_templates(self, skip: int = 0, limit: int = 100) -> List[TemplateInDB]:
        """Get public templates"""
        cursor = self.collection.find({"is_public": True}).skip(skip).limit(limit).sort("created_at", -1)
        templates = []
        async for template_data in cursor:
            template_data["id"] = str(template_data["_id"])
            del template_data["_id"]
            templates.append(TemplateInDB(**template_data))
        return templates
    
    async def update_template(self, template_id: str, template_update: TemplateUpdate) -> Optional[TemplateInDB]:
        """Update template"""
        update_data = template_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(template_id)},
                {"$set": update_data}
            )
        return await self.get_template_by_id(template_id)
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete template"""
        result = await self.collection.delete_one({"_id": ObjectId(template_id)})
        return result.deleted_count > 0
    
    async def search_templates(self, query: str, skip: int = 0, limit: int = 100) -> List[TemplateInDB]:
        """Search public templates"""
        cursor = self.collection.find({
            "is_public": True,
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"tags": {"$in": [{"$regex": query, "$options": "i"}]}}
            ]
        }).skip(skip).limit(limit).sort("created_at", -1)
        
        templates = []
        async for template_data in cursor:
            template_data["id"] = str(template_data["_id"])
            del template_data["_id"]
            templates.append(TemplateInDB(**template_data))
        return templates

# Global instance
template_crud = TemplateCRUD()
