"""Items API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from crud_app.models.item import Item, ItemCreate, ItemUpdate
from crud_app.services.item_service import item_service
from crud_app.services.user_service import user_service

router = APIRouter()


@router.get("/", response_model=List[dict])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """List all items with optional category filter and pagination."""
    return item_service.get_all_items(skip=skip, limit=limit, category=category)


@router.get("/{item_id}", response_model=dict)
def get_item(item_id: int):
    """Retrieve a specific item by ID."""
    item = item_service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return item


@router.post("/", response_model=dict, status_code=201)
def create_item(item: ItemCreate):
    """Create a new item. Owner must be a valid existing user."""
    # Validate that owner exists
    owner = user_service.get_user_by_id(item.owner_id)
    if not owner:
        raise HTTPException(
            status_code=404,
            detail=f"Owner user {item.owner_id} not found"
        )
    return item_service.create_item(item)


@router.patch("/{item_id}", response_model=dict)
def update_item(item_id: int, update: ItemUpdate):
    """Partially update item details."""
    updated = item_service.update_item(item_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return updated


@router.delete("/{item_id}")
def delete_item(item_id: int):
    """Remove an item from the inventory."""
    if not item_service.delete_item(item_id):
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return {"message": f"Item {item_id} deleted successfully"}


@router.get("/inventory/summary")
def inventory_summary():
    """Get overall inventory statistics."""
    items = item_service.get_all_items()
    categories = {}
    for item in items:
        cat = item.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "total_items": len(items),
        "in_stock_count": sum(1 for i in items if i.get("in_stock")),
        "total_value": item_service.get_total_inventory_value(),
        "categories": categories,
    }
