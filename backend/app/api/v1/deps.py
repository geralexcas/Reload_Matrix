from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.config import settings
from app.core import security
from app.core.tenant_context import current_tenant_id
from app.models.sql import user as user_model, company as company_model


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
        token_cid = payload.get("cid")
    except JWTError:
        raise credentials_exception

    user = (
        db.query(user_model.User).filter(user_model.User.username == username).first()
    )
    if user is None:
        raise credentials_exception

    # Validate tenant claim: if token has cid, it must match user's current
    # company_id.  Divergence means company assignment changed → force re-login.
    if token_cid is not None and user.company_id and token_cid != user.company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant context changed. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Set tenant context for ORM auto-filter + RLS (the before_cursor_execute
    # event in tenant_context reads this ContextVar and sets app.tenant_id on
    # the PG connection before every query).  Users with company_id get
    # filtered; platform-admin (superuser without company_id) sets the tenant
    # via verify_company_membership when operating on a specific company.
    if user.company_id:
        current_tenant_id.set(user.company_id)

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


async def get_current_platform_admin(
    current_user: user_model.User = Depends(get_current_user),
) -> user_model.User:
    """Platform admin: superuser WITHOUT company_id (global admin, tenant onboarding)."""
    if not current_user.is_superuser or current_user.company_id:
        raise HTTPException(
            status_code=403,
            detail="Platform admin access required. Contact the platform administrator."
        )
    return current_user


def verify_company_membership(
    company_id: int,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> company_model.Company:
    # Platform-admin: superuser without company_id — can access any tenant
    if current_user.is_superuser and not current_user.company_id:
        db_company = db.query(company_model.Company).filter(
            company_model.Company.id == company_id
        ).first()
        if db_company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        # ponytail: platform-admin operates on one tenant at a time; scope the
        # ContextVar so the ORM filter + RLS apply to the administered company
        # (denies access to other tenants even via raw SQL).
        current_tenant_id.set(company_id)
        return db_company

    # Tenant-superuser or regular user: limited to their own company
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
        if current_user.is_superuser and not current_user.company_id:
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
