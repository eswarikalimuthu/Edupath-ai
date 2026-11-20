"""
EduPath AI - Authentication API Endpoints
Registration, Login, Token Refresh, and Profile Inspection.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from backend.schemas import (
    UserRegisterRequest, UserLoginRequest, TokenResponse,
    RefreshTokenRequest, UserResponse
)
from database.crud import (
    create_user, get_user_by_email, get_user_by_username, get_user_by_id
)
from security.password import hash_password, verify_password
from security.authentication import (
    create_access_token, create_refresh_token, decode_token, AuthenticationError
)
from security.authorization import get_current_user
from database.models import UserRecord

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: UserRegisterRequest):
    if get_user_by_email(req.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
    if get_user_by_username(req.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken. Please choose another."
        )

    hashed = hash_password(req.password)
    user = create_user(
        email=req.email,
        username=req.username,
        hashed_password=hashed,
        role=req.role
    )

    token_data = {"sub": user.id, "role": user.role, "username": user.username}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        username=user.username,
        role=user.role
    )

@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest):
    # Support login via username or email
    user = get_user_by_username(req.username) or get_user_by_email(req.username)
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended or inactive."
        )

    token_data = {"sub": user.id, "role": user.role, "username": user.username}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        username=user.username,
        role=user.role
    )

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(req: RefreshTokenRequest):
    try:
        payload = decode_token(req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        user_id = payload.get("sub")
        user = get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User invalid or inactive")

        token_data = {"sub": user.id, "role": user.role, "username": user.username}
        new_access = create_access_token(token_data)
        new_refresh = create_refresh_token(token_data)

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            user_id=user.id,
            username=user.username,
            role=user.role
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserRecord = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role,
        is_active=current_user.is_active
    )
