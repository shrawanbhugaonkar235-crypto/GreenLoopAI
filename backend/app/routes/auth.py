import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from pymongo.errors import DuplicateKeyError

from app.database import get_db
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    AuthTokenResponse
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest):
    """
    Registers a new citizen account with secure bcrypt password hashing
    and returns a signed expiring JWT access token.
    """
    db = get_db()
    email_norm = req.email.strip().lower()

    # Check existing citizen
    existing = db.users.find_one({"email": email_norm})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists."
        )

    user_id = str(uuid.uuid4())
    pw_hash = hash_password(req.password)
    now_iso = datetime.now(timezone.utc).isoformat()

    user_doc = {
        "id": user_id,
        "name": req.name.strip(),
        "email": email_norm,
        "password_hash": pw_hash,
        "created_at": now_iso,
        "updated_at": now_iso
    }

    try:
        db.users.insert_one(user_doc)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists."
        )

    # Issue signed JWT
    token = create_access_token({
        "sub": user_id,
        "email": email_norm,
        "name": req.name.strip()
    })

    return AuthTokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user_id,
            name=req.name.strip(),
            email=email_norm,
            created_at=now_iso
        )
    )

@router.post("/login", response_model=AuthTokenResponse)
async def login(req: UserLoginRequest):
    """
    Authenticates a citizen by verifying credentials against stored bcrypt hash,
    and returns a signed expiring JWT token.
    """
    db = get_db()
    email_norm = req.email.strip().lower()

    user = db.users.find_one({"email": email_norm})
    if not user or not verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = create_access_token({
        "sub": user["id"],
        "email": user["email"],
        "name": user["name"]
    })

    return AuthTokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            created_at=user.get("created_at")
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Retrieves the currently authenticated citizen profile.
    """
    return UserResponse(
        id=current_user["id"],
        name=current_user["name"],
        email=current_user["email"],
        created_at=current_user.get("created_at")
    )
