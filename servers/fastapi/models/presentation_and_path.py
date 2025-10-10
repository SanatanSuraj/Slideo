from pydantic import BaseModel
from typing import Optional


class PresentationAndPath(BaseModel):
    presentation_id: str
    path: str
    s3_pptx_url: Optional[str] = None
    s3_pdf_url: Optional[str] = None


class PresentationPathAndEditPath(PresentationAndPath):
    edit_path: str
