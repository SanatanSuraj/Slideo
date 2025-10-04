from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(str, Enum):
    PRESENTATION_GENERATION = "presentation_generation"
    IMAGE_GENERATION = "image_generation"
    EXPORT = "export"
    PROCESSING = "processing"

class TaskBase(BaseModel):
    task_type: TaskType
    status: TaskStatus = TaskStatus.PENDING
    progress: int = 0
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TaskCreate(TaskBase):
    user_id: str
    presentation_id: Optional[str] = None

class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    progress: Optional[int] = None
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TaskInDB(TaskBase):
    id: Optional[str] = None
    user_id: str
    presentation_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Task(TaskBase):
    id: Optional[str] = None
    user_id: str
    presentation_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
