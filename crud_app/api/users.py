"""Users API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from crud_app.models.user import User, UserCreate, UserUpdate
from crud_app.services.user_service import user_service

router = APIRouter()


@router.get("/", response_model=List[dict])
def list_users(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return")
):
    """List all users with pagination."""
    return user_service.get_all_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=dict)
def get_user(user_id: int):
    """Retrieve a specific user by ID."""
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user


@router.post("/", response_model=dict, status_code=201)
def create_user(user: UserCreate):
    """Create a new user account."""
    try:
        return user_service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}", response_model=dict)
def update_user(user_id: int, update: UserUpdate):
    """Partially update a user's information."""
    try:
        updated = user_service.update_user(user_id, update)
        if not updated:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}")
def delete_user(user_id: int):
    """Delete a user and their associated items."""
    if not user_service.delete_user(user_id):
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return {"message": f"User {user_id} and their items deleted successfully"}


@router.get("/{user_id}/stats")
def get_user_stats(user_id: int):
    """Get statistics for a specific user."""
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    from crud_app.services.item_service import item_service
    items = item_service.get_items_by_owner(user_id)
    return {
        "user_id": user_id,
        "name": user["name"],
        "total_items": len(items),
        "total_value": sum(i["price"] for i in items),
    }
