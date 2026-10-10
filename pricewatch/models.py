import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class ProductItem(BaseModel):
    store: str
    variant_id: str
    url: str
    title: str
    vendor: str = ""
    category: str = "uncategorized"
    price: float = Field(gt=0)
    compare_at_price: Optional[float] = None
    in_stock: bool

    @field_validator("price", "compare_at_price", mode="before")
    @classmethod
    def clean_price(cls, v):
        if v in (None, ""):
            return None
        if isinstance(v, str):
            v = float(re.sub(r"[^\d.]", "", v) or 0)
        return v or None

    @field_validator("variant_id", mode="before")
    @classmethod
    def to_str(cls, v):
        return str(v)