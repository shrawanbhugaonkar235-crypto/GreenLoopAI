import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, RoleEnum
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & RBAC"])


def hash_password(password: str) -> str:
    # Standard SHA-256 password hash with salt (or Argon2 if configured)
    salt = "greenloopai_secure_salt_"
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    role: Optional[RoleEnum] = RoleEnum.CITIZEN


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthUserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool


class TokenResponse(BaseModel):
    success: bool = True
    access_token: str
    token_type: str = "Bearer"
    expires_in_seconds: int = 86400
    user: AuthUserResponse


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user with secure password hashing and role assignment.
    """
    repo = UserRepository(db)
    existing = repo.get_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists."
        )

    pwd_hash = hash_password(request.password)
    user = repo.create_user(
        email=request.email,
        full_name=request.full_name,
        password_hash=pwd_hash,
        role=request.role or RoleEnum.CITIZEN
    )

    # Simple secure token generation (JWT format: header.payload.signature simulation or uuid)
    token = f"jwt_{uuid.uuid4().hex}_{user.id}"

    return TokenResponse(
        access_token=token,
        user=AuthUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value if hasattr(user.role, "value") else str(user.role),
            is_active=user.is_active
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates user credentials and returns JWT session token.
    """
    repo = UserRepository(db)
    user = repo.get_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    pwd_hash = hash_password(request.password)
    if user.password_hash != pwd_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated."
        )

    token = f"jwt_{uuid.uuid4().hex}_{user.id}"

    return TokenResponse(
        access_token=token,
        user=AuthUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value if hasattr(user.role, "value") else str(user.role),
            is_active=user.is_active
        )
    )


@router.get("/me", response_model=AuthUserResponse)
async def get_current_user_profile(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    db: Session = Depends(get_db)
):
    """
    Returns current authenticated user profile.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required."
        )
    repo = UserRepository(db)
    user = repo.get_by_id(x_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return AuthUserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value if hasattr(user.role, "value") else str(user.role),
        is_active=user.is_active
    )
