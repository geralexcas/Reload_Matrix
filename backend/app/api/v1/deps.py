from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.config import settings
from app.core import security
from app.models.sql import user as user_model, company as company_model
from app.models.sql.user import user_permissions


async def get_current_user(
    token: str = Depends(security.oauth2_scheme), db: Session = Depends(get_db)
) -> user_model.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = (
        db.query(user_model.User).filter(user_model.User.username == username).first()
    )
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: user_model.User = Depends(get_current_user),
) -> user_model.User:
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user


async def get_current_superuser(
    current_user: user_model.User = Depends(get_current_user),
) -> user_model.User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


def verify_company_membership(
    company_id: int,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> company_model.Company:
    if current_user.is_superuser:
        db_company = db.query(company_model.Company).filter(
            company_model.Company.id == company_id
        ).first()
        if db_company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        return db_company
    
    if not current_user.company_id:
        raise HTTPException(
            status_code=403,
            detail="User has no company assigned. Contact administrator."
        )
    
    if current_user.company_id != company_id:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. You belong to company {current_user.company_id}, not company {company_id}."
        )
    
    db_company = db.query(company_model.Company).filter(
        company_model.Company.id == company_id
    ).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return db_company


def require_permission(module: str, action: str):
    async def _check_permission(
        current_user: user_model.User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ) -> user_model.User:
        if current_user.is_superuser:
            return current_user

        from app.models.sql.audit import Permission
        from app.models.sql.user import user_permissions

        permission = (
            db.query(Permission)
            .join(user_permissions, Permission.id == user_permissions.c.permission_id)
            .filter(
                Permission.module == module,
                Permission.action == action,
                user_permissions.c.user_id == current_user.id,
            )
            .first()
        )
        if not permission:
            raise HTTPException(
                status_code=403, detail=f"Permission denied: '{action}' on '{module}'"
            )
        return current_user

    return _check_permission
