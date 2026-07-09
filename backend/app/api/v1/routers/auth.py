from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.models.sql import user as user_model
from app.schemas import user as user_schema
from app.core import security
from app.core.config import settings
from app.core.database import get_db

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/token", response_model=user_schema.Token)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = (
        db.query(user_model.User)
        .filter(
            (user_model.User.username == form_data.username)
            | (user_model.User.email == form_data.username)
        )
        .first()
    )
    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=security.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = security.create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )
    user.hashed_refresh_token = security.get_password_hash(refresh_token)
    db.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=user_schema.Token)
@limiter.limit("10/minute")
async def refresh_access_token(
    request: Request,
    token_data: user_schema.RefreshToken, db: Session = Depends(get_db)
):
    try:
        payload = security.jwt.decode(
            token_data.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        if username is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except security.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = (
        db.query(user_model.User).filter(user_model.User.username == username).first()
    )
    if not user or not user.hashed_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or no refresh token stored",
        )
    if not security.verify_password(
        token_data.refresh_token, user.hashed_refresh_token
    ):
        user.hashed_refresh_token = None
        db.commit()
        from app.core.audit import log_security_event
        log_security_event(
            user_id=user.id,
            event_type="REFRESH_TOKEN_REUSE_DETECTED",
            details="Intento de reusar refresh token inválido"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked - possible security breach",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Generate new refresh token
    refresh_token_expires = timedelta(days=security.REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh_token = security.create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )
    user.hashed_refresh_token = security.get_password_hash(new_refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(token_data: user_schema.RefreshToken, db: Session = Depends(get_db)):
    try:
        payload = security.jwt.decode(
            token_data.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        username: str = payload.get("sub")
    except security.JWTError:
        pass
    else:
        user = (
            db.query(user_model.User)
            .filter(user_model.User.username == username)
            .first()
        )
        if user and user.hashed_refresh_token:
            user.hashed_refresh_token = None
            db.commit()
    return {"message": "Logged out successfully"}


@router.post(
    "/register",
    response_model=user_schema.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("3/hour")
def register_user(
    request: Request,
    user: user_schema.UserCreate, db: Session = Depends(get_db)
):
    is_valid, message = security.validate_password_strength(user.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    db_user = (
        db.query(user_model.User).filter(user_model.User.email == user.email).first()
    )
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = (
        db.query(user_model.User)
        .filter(user_model.User.username == user.username)
        .first()
    )
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = security.get_password_hash(user.password)
    db_user = user_model.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=True,
        is_superuser=False,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


