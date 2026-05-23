"""Item data models."""

from pydantic import BaseModel, Field
from typing import Optional


class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Item title")
    description: Optional[str] = Field(None, description="Item description")
    price: float = Field(..., gt=0, description="Item price (must be positive)")
    category: str = Field(default="general", description="Item category")
    in_stock: bool = Field(default=True, description="Whether item is in stock")


class ItemCreate(ItemBase):
    owner_id: int = Field(..., description="ID of the user who owns this item")


class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    in_stock: Optional[bool] = None


class Item(ItemBase):
    id: int
    owner_id: int
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
