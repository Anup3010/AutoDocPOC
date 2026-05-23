"""
Item Service Layer
Handles all business logic for item/inventory management operations.
"""

from datetime import datetime
from typing import List, Optional, Dict
from crud_app.services.db_service import get_db
from crud_app.models.item import ItemCreate, ItemUpdate


class ItemService:
    """Service class for item CRUD operations."""

    def get_all_items(self, skip: int = 0, limit: int = 100,
                      category: Optional[str] = None) -> List[Dict]:
        """
        Retrieve all items with optional category filtering and pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            category: Optional category filter
            
        Returns:
            Filtered and paginated list of items
        """
        db = get_db()
        items = list(db["items"].values())
        if category:
            items = [i for i in items if i["category"] == category]
        return items[skip: skip + limit]

    def get_item_by_id(self, item_id: int) -> Optional[Dict]:
        """
        Fetch a single item by ID.
        
        Args:
            item_id: Unique item identifier
            
        Returns:
            Item dictionary if found, None otherwise
        """
        db = get_db()
        return db["items"].get(item_id)

    def get_items_by_owner(self, owner_id: int) -> List[Dict]:
        """
        Get all items belonging to a specific user.
        Used for user profile pages and ownership validation.
        
        Args:
            owner_id: ID of the owning user
            
        Returns:
            List of items owned by the user
        """
        db = get_db()
        return [item for item in db["items"].values() if item["owner_id"] == owner_id]

    def create_item(self, item_data: ItemCreate) -> Dict:
        """
        Create a new inventory item.
        
        Business Rules:
        - Owner must exist (validated at API layer)
        - Price must be positive (enforced by model)
        - Category defaults to 'general'
        
        Args:
            item_data: Validated item creation payload
            
        Returns:
            Newly created item dictionary
        """
        db = get_db()
        db["item_counter"] += 1
        new_id = db["item_counter"]
        
        new_item = {
            "id": new_id,
            "title": item_data.title,
            "description": item_data.description,
            "price": item_data.price,
            "category": item_data.category,
            "in_stock": item_data.in_stock,
            "owner_id": item_data.owner_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": None,
        }
        db["items"][new_id] = new_item
        return new_item

    def update_item(self, item_id: int, update_data: ItemUpdate) -> Optional[Dict]:
        """
        Partially update item details.
        
        Args:
            item_id: ID of item to update
            update_data: Fields to update
            
        Returns:
            Updated item dictionary, or None if not found
        """
        db = get_db()
        item = db["items"].get(item_id)
        if not item:
            return None
        
        update_fields = update_data.model_dump(exclude_none=True)
        item.update(update_fields)
        item["updated_at"] = datetime.now().isoformat()
        return item

    def delete_item(self, item_id: int) -> bool:
        """
        Remove an item from inventory.
        
        Args:
            item_id: ID of item to delete
            
        Returns:
            True if deleted, False if not found
        """
        db = get_db()
        if item_id not in db["items"]:
            return False
        del db["items"][item_id]
        return True

    def get_total_inventory_value(self) -> float:
        """Calculate total value of all in-stock items."""
        db = get_db()
        return sum(
            item["price"] for item in db["items"].values()
            if item.get("in_stock", True)
        )


# Singleton instance
item_service = ItemService()
