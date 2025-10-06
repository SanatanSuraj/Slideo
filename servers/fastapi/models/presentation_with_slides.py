# servers/fastapi/models/presentation_with_slides.py
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel, field_validator
try:
    # v2 config
    from pydantic import ConfigDict
    V2 = True
except Exception:  # v1 fallback
    V2 = False

def _as_obj(v):
    if v is None:
        return None
    if isinstance(v, list):
        return {str(i): x for i, x in enumerate(v)}
    if isinstance(v, dict):
        return v
    # force a predictable type error at the boundary
    raise TypeError(f"Expected dict|list|None, got {type(v).__name__}")

T = TypeVar("T", bound="PresentationWithSlides")


class PresentationWithSlides(BaseModel):
    # keep forward compatibility
    if V2:
        model_config = ConfigDict(extra="allow")
    else:
        class Config:
            extra = "allow"

    # ... existing fields ...
    # slides: List[SlideInDB]
    layout: Optional[Dict[str, Any]] = None
    structure: Optional[Dict[str, Any]] = None
    outlines: Optional[Dict[str, Any]] = None

    if V2:
        @field_validator("layout", "structure", "outlines", mode="before")
        @classmethod
        def _normalize_obj(cls, v):
            return _as_obj(v)
    else:
        from pydantic import validator
        @validator("layout", "structure", "outlines", pre=True)
        def _normalize_obj_v1(cls, v):
            return _as_obj(v)

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Normalise dict payloads for both Pydantic v1 and v2 runtimes."""
        if data is None:
            raise ValueError("data must not be None")

        if V2:
            return cls.model_validate(data)

        return cls.parse_obj(data)
