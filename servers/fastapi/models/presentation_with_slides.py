from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel

from models.mongo.slide import SlideInDB


class PresentationWithSlides(BaseModel):
    id: str
    content: str
    n_slides: int
    language: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tone: Optional[str] = None
    verbosity: Optional[str] = None
    slides: List[SlideInDB]
