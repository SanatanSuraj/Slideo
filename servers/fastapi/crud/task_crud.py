from typing import Optional, List
from datetime import datetime, timedelta
from bson import ObjectId
from models.mongo.task import Task, TaskCreate, TaskUpdate, TaskInDB, TaskStatus
from db.mongo import get_tasks_collection

class TaskCRUD:
    def __init__(self):
        self._collection = None
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = get_tasks_collection()
        return self._collection
    
    async def create_task(self, task: TaskCreate) -> str:
        """Create a new task"""
        task_data = {
            "user_id": task.user_id,
            "presentation_id": task.presentation_id,
            "task_type": task.task_type,
            "status": task.status,
            "progress": task.progress,
            "message": task.message,
            "result": task.result,
            "error": task.error,
            "metadata": task.metadata,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None
        }
        result = await self.collection.insert_one(task_data)
        return str(result.inserted_id)
    
    async def get_task_by_id(self, task_id: str) -> Optional[TaskInDB]:
        """Get task by ID"""
        task_data = await self.collection.find_one({"_id": ObjectId(task_id)})
        if task_data:
            task_data["id"] = str(task_data["_id"])
            del task_data["_id"]
            return TaskInDB(**task_data)
        return None
    
    async def get_tasks_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[TaskInDB]:
        """Get tasks by user ID"""
        cursor = self.collection.find({"user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
        tasks = []
        async for task_data in cursor:
            task_data["id"] = str(task_data["_id"])
            del task_data["_id"]
            tasks.append(TaskInDB(**task_data))
        return tasks
    
    async def get_tasks_by_presentation(self, presentation_id: str) -> List[TaskInDB]:
        """Get tasks by presentation ID"""
        cursor = self.collection.find({"presentation_id": presentation_id}).sort("created_at", -1)
        tasks = []
        async for task_data in cursor:
            task_data["id"] = str(task_data["_id"])
            del task_data["_id"]
            tasks.append(TaskInDB(**task_data))
        return tasks
    
    async def get_tasks_by_status(self, status: TaskStatus, skip: int = 0, limit: int = 100) -> List[TaskInDB]:
        """Get tasks by status"""
        cursor = self.collection.find({"status": status}).skip(skip).limit(limit).sort("created_at", -1)
        tasks = []
        async for task_data in cursor:
            task_data["id"] = str(task_data["_id"])
            del task_data["_id"]
            tasks.append(TaskInDB(**task_data))
        return tasks
    
    async def update_task(self, task_id: str, task_update: TaskUpdate) -> Optional[TaskInDB]:
        """Update task"""
        update_data = task_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            
            # Set started_at when status changes to running
            if "status" in update_data and update_data["status"] == TaskStatus.RUNNING:
                update_data["started_at"] = datetime.utcnow()
            
            # Set completed_at when status changes to completed or failed
            if "status" in update_data and update_data["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                update_data["completed_at"] = datetime.utcnow()
            
            await self.collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": update_data}
            )
        return await self.get_task_by_id(task_id)
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete task"""
        result = await self.collection.delete_one({"_id": ObjectId(task_id)})
        return result.deleted_count > 0
    
    async def delete_old_tasks(self, days_old: int = 30) -> int:
        """Delete old completed/failed tasks"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        result = await self.collection.delete_many({
            "status": {"$in": [TaskStatus.COMPLETED, TaskStatus.FAILED]},
            "completed_at": {"$lt": cutoff_date}
        })
        return result.deleted_count

# Global instance
task_crud = TaskCRUD()
