"""
User Service Layer
Handles all business logic for user management operations.
"""

from datetime import datetime
from typing import List, Optional, Dict
from crud_app.services.db_service import get_db
from crud_app.models.user import UserCreate, UserUpdate, User


class UserService:
    """Service class for user CRUD operations and business logic."""

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        Retrieve all users with pagination support.
        
        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            
        Returns:
            List of user dictionaries
        """
        db = get_db()
        users = list(db["users"].values())
        return users[skip: skip + limit]

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """
        Fetch a single user by their unique ID.
        
        Args:
            user_id: The unique identifier of the user
            
        Returns:
            User dictionary if found, None otherwise
        """
        db = get_db()
        return db["users"].get(user_id)

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Find a user by their email address. Used for duplicate email validation.
        
        Args:
            email: Email address to search for
            
        Returns:
            User dictionary if found, None otherwise
        """
        db = get_db()
        for user in db["users"].values():
            if user["email"].lower() == email.lower():
                return user
        return None

    def create_user(self, user_data: UserCreate) -> Dict:
        """
        Create a new user after validating uniqueness constraints.
        
        Business Rules:
        - Email must be unique across all users
        - Password is stored (in POC; use hashing in production)
        - Default role is 'viewer' unless specified
        
        Args:
            user_data: Validated user creation payload
            
        Returns:
            Newly created user dictionary
            
        Raises:
            ValueError: If email already exists
        """
        db = get_db()
        
        # Validate email uniqueness
        if self.get_user_by_email(user_data.email):
            raise ValueError(f"User with email '{user_data.email}' already exists")
        
        db["user_counter"] += 1
        new_id = db["user_counter"]
        
        new_user = {
            "id": new_id,
            "name": user_data.name,
            "email": user_data.email,
            "role": user_data.role,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": None,
        }
        db["users"][new_id] = new_user
        return new_user

    def update_user(self, user_id: int, update_data: UserUpdate) -> Optional[Dict]:
        """
        Partially update a user's information.
        Only provided fields are updated (PATCH behavior).
        
        Args:
            user_id: ID of user to update
            update_data: Fields to update (None values are ignored)
            
        Returns:
            Updated user dictionary, or None if user not found
        """
        db = get_db()
        user = db["users"].get(user_id)
        if not user:
            return None
        
        update_fields = update_data.model_dump(exclude_none=True)
        
        # Check email uniqueness if email is being updated
        if "email" in update_fields:
            existing = self.get_user_by_email(update_fields["email"])
            if existing and existing["id"] != user_id:
                raise ValueError(f"Email '{update_fields['email']}' already in use")
        
        user.update(update_fields)
        user["updated_at"] = datetime.now().isoformat()
        return user

    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user and all their associated items.
        
        Cascade behavior: Deletes all items owned by this user.
        
        Args:
            user_id: ID of user to delete
            
        Returns:
            True if deleted successfully, False if user not found
        """
        db = get_db()
        if user_id not in db["users"]:
            return False
        
        # Cascade delete user's items
        items_to_delete = [
            item_id for item_id, item in db["items"].items()
            if item["owner_id"] == user_id
        ]
        for item_id in items_to_delete:
            del db["items"][item_id]
        
        del db["users"][user_id]
        return True

    def get_active_users_count(self) -> int:
        """Return the count of currently active users."""
        db = get_db()
        return sum(1 for u in db["users"].values() if u["is_active"])


# Singleton instance
user_service = UserService()
# test change
