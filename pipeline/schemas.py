from pydantic import BaseModel, Field
from typing import Optional

class ProductAttributes(BaseModel):
    product_type: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    target_age: Optional[str] = None
    key_features: list[str] = Field(default_factory=list)
    materials: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    is_baby_product: bool  # grounding gate — if False, we refuse

class PDPOutput(BaseModel):
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    bullets_en: list[str] = Field(default_factory=list)
    bullets_ar: list[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    grounded: bool
    refused_fields: list[str] = Field(default_factory=list)
    refusal_reason: Optional[str] = None