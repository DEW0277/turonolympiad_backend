from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.modules.auth.service.auth_service import AuthService
from app.modules.auth.schemas.user import (
    UserResponse,
    UserRoleUpdate,
    UserStatusUpdate,
    UserRole
)
from app.dependencies.database_dependecy import get_session
from app.dependencies.current_user import get_current_admin_active


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.get("/users", response_model=dict)
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    admin_user=Depends(get_current_admin_active),
    db: AsyncSession = Depends(get_session)
):
    """
    Get all users with pagination (admin only).
    
    Query params:
        skip: Number of records to skip
        limit: Number of records to return (max 100)
    """
    if limit > 100:
        limit = 100
    
    service = AuthService(db)
    result = await service.auth_repository.get_all_users(skip=skip, limit=limit)
    
    return {
        "total": result["total"],
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone_number": user.phone_number,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
            for user in result["items"]
        ]
    }


@router.get("/users/{user_id}", response_model=dict)
async def get_user_detail(
    user_id: str,
    admin_user=Depends(get_current_admin_active),
    db: AsyncSession = Depends(get_session)
):
    """
    Get detailed information about a specific user (admin only).
    
    Path params:
        user_id: The user's ID
    """
    service = AuthService(db)
    user = await service.auth_repository.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "role": user.role.value,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_update: UserRoleUpdate,
    admin_user=Depends(get_current_admin_active),
    db: AsyncSession = Depends(get_session)
):
    """
    Change a user's role (admin only).
    Can promote ordinary users to admin or demote admins to ordinary.
    
    Path params:
        user_id: The user's ID
    
    Body:
        role: 'admin' or 'ordinary'
    """
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    service = AuthService(db)
    user = await service.auth_repository.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Ensure at least one admin exists
    if role_update.role == UserRole.ORDINARY:
        admin_count = await service.auth_repository.get_admin_count()
        if admin_count <= 1:  # Only one admin (the current one)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote the last admin. Promote another user to admin first"
            )
    
    updated_user = await service.auth_repository.update_user_role(user_id, role_update.role)
    
    return {
        "status": "success",
        "message": f"User role updated to {role_update.role.value}",
        "user": {
            "id": updated_user.id,
            "first_name": updated_user.first_name,
            "last_name": updated_user.last_name,
            "phone_number": updated_user.phone_number,
            "role": updated_user.role.value,
            "is_active": updated_user.is_active
        }
    }


@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    status_update: UserStatusUpdate,
    admin_user=Depends(get_current_admin_active),
    db: AsyncSession = Depends(get_session)
):
    """
    Activate or deactivate a user account (admin only).
    Deactivated users cannot login.
    
    Path params:
        user_id: The user's ID
    
    Body:
        is_active: true to activate, false to deactivate
    """
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    service = AuthService(db)
    user = await service.auth_repository.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = await service.auth_repository.update_user_status(user_id, status_update.is_active)
    
    status_text = "activated" if status_update.is_active else "deactivated"
    
    return {
        "status": "success",
        "message": f"User {status_text} successfully",
        "user": {
            "id": updated_user.id,
            "first_name": updated_user.first_name,
            "last_name": updated_user.last_name,
            "phone_number": updated_user.phone_number,
            "role": updated_user.role.value,
            "is_active": updated_user.is_active
        }
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_user=Depends(get_current_admin_active),
    db: AsyncSession = Depends(get_session)
):
    """
    Delete a user account permanently (admin only).
    This action cannot be undone.
    
    Path params:
        user_id: The user's ID
    """
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    service = AuthService(db)
    user = await service.auth_repository.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting the only admin
    if user.role.value == "admin":
        admin_count = await service.auth_repository.get_admin_count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last admin. Promote another user to admin first"
            )
    
    deleted = await service.auth_repository.delete_user(user_id)
    
    if deleted:
        return {
            "status": "success",
            "message": f"User {user_id} deleted successfully"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.get("/admins")
async def list_admins(
    admin_user=Depends(get_current_admin_active),
    db: AsyncSession = Depends(get_session)
):
    """
    Get list of all admin users (admin only).
    """
    service = AuthService(db)
    admins = await service.auth_repository.get_admins()
    
    return {
        "total": len(admins),
        "items": [
            {
                "id": admin.id,
                "first_name": admin.first_name,
                "last_name": admin.last_name,
                "phone_number": admin.phone_number,
                "role": admin.role.value,
                "is_active": admin.is_active,
                "created_at": admin.created_at
            }
            for admin in admins
        ]
    }


@router.get("/stats")
async def get_admin_stats(
    admin_user=Depends(get_current_admin_active),
    db: AsyncSession = Depends(get_session)
):
    """
    Get admin dashboard statistics (admin only).
    """
    service = AuthService(db)
    all_users = await service.auth_repository.get_all_users(limit=1)
    admins = await service.auth_repository.get_admins()
    
    total_users = all_users["total"]
    total_admins = len(admins)
    total_ordinary = total_users - total_admins
    active_users = sum(1 for user in (await service.auth_repository.get_all_users(limit=1000))["items"] if user.is_active)
    
    return {
        "total_users": total_users,
        "total_admins": total_admins,
        "total_ordinary_users": total_ordinary,
        "active_users": active_users,
        "inactive_users": total_users - active_users
    }
