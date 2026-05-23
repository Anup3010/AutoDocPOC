"""In-memory database service for POC."""

from datetime import datetime
from typing import Dict, List, Optional

# In-memory storage
_db = {
    "users": {},
    "items": {},
    "user_counter": 0,
    "item_counter": 0,
}


def init_db():
    """Initialize with sample data."""
    global _db
    # Add sample users
    _db["user_counter"] = 2
    _db["users"] = {
        1: {
            "id": 1, "name": "Alice Admin", "email": "alice@example.com",
            "role": "admin", "is_active": True,
            "created_at": "2024-01-01T10:00:00", "updated_at": None
        },
        2: {
            "id": 2, "name": "Bob Editor", "email": "bob@example.com",
            "role": "editor", "is_active": True,
            "created_at": "2024-01-02T11:00:00", "updated_at": None
        },
    }
    # Add sample items
    _db["item_counter"] = 2
    _db["items"] = {
        1: {
            "id": 1, "title": "Laptop Pro", "description": "High-performance laptop",
            "price": 1299.99, "category": "electronics", "in_stock": True,
            "owner_id": 1, "created_at": "2024-01-03T09:00:00", "updated_at": None
        },
        2: {
            "id": 2, "title": "Wireless Mouse", "description": "Ergonomic wireless mouse",
            "price": 49.99, "category": "accessories", "in_stock": True,
            "owner_id": 2, "created_at": "2024-01-04T10:00:00", "updated_at": None
        },
    }


def get_db():
    return _db
