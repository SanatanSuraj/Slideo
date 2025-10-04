from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional
from models.mongo.user import User, UserCreate, UserUpdate
from models.auth_models import LoginRequest, RegisterRequest
from crud.user_crud import user_crud
from auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from auth.dependencies import get_current_active_user
from db.mongo import connect_to_mongo

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=dict)
async def register(request: RegisterRequest):
    """Register a new user"""
    # Check if user already exists
    existing_user = await user_crud.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user data
    user_data = UserCreate(
        name=request.name,
        email=request.email,
        password=request.password
    )
    
    # Create new user
    user_id = await user_crud.create_user(user_data)
    
    # Get the created user
    user = await user_crud.get_user_by_id(user_id)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user_id}, remember_me=request.remember_me)
    refresh_token = create_refresh_token(data={"sub": user_id}, remember_me=request.remember_me)
    
    return {
        "message": "User created successfully",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "plan": user.plan,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
    }

@router.post("/login", response_model=dict)
async def login(request: LoginRequest):
    """Login user"""
    user = await user_crud.authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id}, remember_me=request.remember_me)
    refresh_token = create_refresh_token(data={"sub": user.id}, remember_me=request.remember_me)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "plan": user.plan,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
    }

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        payload = verify_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        user = await user_crud.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new access token
        access_token = create_access_token(data={"sub": user_id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update current user information"""
    updated_user = await user_crud.update_user(current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return User(
        id=updated_user.id,
        email=updated_user.email,
        name=updated_user.name,
        plan=updated_user.plan,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at
    )

@router.delete("/me")
async def delete_current_user(current_user: User = Depends(get_current_active_user)):
    """Delete current user account"""
    success = await user_crud.delete_user(current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}

@router.post("/google", response_model=dict)
async def google_auth(google_data: dict):
    """Handle Google OAuth authentication"""
    google_id = google_data.get("google_id")
    email = google_data.get("email")
    name = google_data.get("name")
    picture = google_data.get("picture")
    
    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required Google OAuth data"
        )
    
    # Check if user exists by email
    user = await user_crud.get_user_by_email(email)
    
    if not user:
        # Create new user with Google OAuth data
        user_create = UserCreate(
            email=email,
            name=name or "Google User",
            password="",  # No password for OAuth users
            is_active=True
        )
        user_id = await user_crud.create_user(user_create)
        user = await user_crud.get_user_by_id(user_id)
    else:
        # Use existing user
        user_id = user.id
    
    # Create tokens
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "plan": user.plan,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
    }
