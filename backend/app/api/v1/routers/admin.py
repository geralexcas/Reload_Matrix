from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.sql import user as user_model
from app.models.sql.audit import AuditLog, Permission
from app.schemas import user as user_schema
from app.core.database import get_db
from app.core import security
from app.api.v1.deps import (
    get_current_superuser,
    get_current_active_user,
    get_current_platform_admin,
    require_permission,
)
from app.services.backup_service import BackupService
from app.services.permission_service import assign_role_permissions, seed_permissions


router = APIRouter()


# ===== USER MANAGEMENT =====


@router.get("/users/", response_model=List[user_schema.UserResponse])
def list_users(
    company_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("users", "read")),
):
    """List all users. Platform admin can see all or filter by company.
    Tenant users only see their own company."""
    query = db.query(user_model.User)

    # Platform admin: superuser without company_id — can see all or filter
    if current_user.is_superuser and not current_user.company_id:
        if company_id:
            query = query.filter(user_model.User.company_id == company_id)
    elif current_user.company_id:
        # Tenant user (including tenant-superuser): only own company
        query = query.filter(user_model.User.company_id == current_user.company_id)
    else:
        query = query.filter(user_model.User.id == current_user.id)

    return query.offset(skip).limit(limit).all()


@router.get("/users/{user_id}", response_model=user_schema.UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("users", "read")),
):
    """Get user by ID. Regular users can only see users in their own company."""
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ponytail: platform-admin (superuser sin company_id) bypass; tenant-superuser
    # y usuarios regulares solo pueden ver usuarios de su propia empresa.
    is_platform_admin = current_user.is_superuser and not current_user.company_id
    if not is_platform_admin and user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=403, detail="Not enough permissions to view this user"
        )

    return user


@router.post(
    "/users/",
    response_model=user_schema.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: dict,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_platform_admin),
):
    """Create a new user in any tenant (platform admin only).

    `is_superuser=True` grants tenant-admin privileges within the company.
    """
    company_id = user_data.get("company_id")
    email = user_data.get("email")
    username = user_data.get("username")
    password = user_data.get("password")
    full_name = user_data.get("full_name")
    role = user_data.get("role", "VENDEDOR")
    is_superuser = user_data.get("is_superuser", False)

    existing = (
        db.query(user_model.User)
        .filter(
            (user_model.User.email == email) | (user_model.User.username == username)
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Email or username already exists")

    is_valid, message = security.validate_password_strength(password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    hashed_password = security.get_password_hash(password)
    db_user = user_model.User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        full_name=full_name,
        role=role,
        is_active=True,
        is_superuser=is_superuser,
        company_id=company_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    seed_permissions(db)
    assign_role_permissions(db, db_user)
    db.commit()

    return db_user


@router.put("/users/{user_id}", response_model=user_schema.UserResponse)
def update_user(
    user_id: int,
    user_data: user_schema.UserCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_superuser),
):
    """Update a user (superuser only)."""
    db_user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # ponytail: tenant-superuser solo puede mutar usuarios de su empresa;
    # platform-admin (superuser sin company_id) bypass.
    is_platform_admin = current_user.is_superuser and not current_user.company_id
    if not is_platform_admin and db_user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=403, detail="Not enough permissions to modify this user"
        )

    db_user.email = user_data.email
    db_user.username = user_data.username
    db_user.full_name = user_data.full_name
    db_user.role = user_data.role
    if user_data.password:
        db_user.hashed_password = security.get_password_hash(user_data.password)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.patch("/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_superuser),
):
    """Activate or deactivate a user (superuser only)."""
    db_user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    # ponytail: tenant-superuser solo muta usuarios de su empresa.
    is_platform_admin = current_user.is_superuser and not current_user.company_id
    if not is_platform_admin and db_user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=403, detail="Not enough permissions to modify this user"
        )

    db_user.is_active = not db_user.is_active
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "is_active": db_user.is_active}


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_superuser),
):
    """Delete a user (superuser only)."""
    db_user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    # ponytail: tenant-superuser solo borra usuarios de su empresa.
    is_platform_admin = current_user.is_superuser and not current_user.company_id
    if not is_platform_admin and db_user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=403, detail="Not enough permissions to delete this user"
        )

    db.delete(db_user)
    db.commit()
    return None


@router.post("/users/{user_id}/reset-password/")
def reset_user_password(
    user_id: int,
    password_data: dict,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_superuser),
):
    """Reset password for a user (superuser only)."""
    db_user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # ponytail: tenant-superuser solo resetea passwords de su empresa.
    is_platform_admin = current_user.is_superuser and not current_user.company_id
    if not is_platform_admin and db_user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=403, detail="Not enough permissions to modify this user"
        )

    new_password = password_data.get("new_password")
    if not new_password:
        raise HTTPException(status_code=400, detail="new_password is required")

    is_valid, message = security.validate_password_strength(new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    db_user.hashed_password = security.get_password_hash(new_password)
    db.commit()
    return {"message": "Password reset successfully"}


# ===== AUDIT LOG =====


@router.get("/audit-logs/")
def get_audit_logs(
    company_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("users", "read")),
):
    """Query audit logs. Platform admin sees all or filters by company.
    Tenant users only see their own company's logs."""
    query = db.query(AuditLog)

    # Platform admin: superuser without company_id — can see all or filter
    if current_user.is_superuser and not current_user.company_id:
        if company_id:
            query = query.filter(AuditLog.company_id == company_id)
    elif current_user.company_id:
        # Tenant user: only own company's logs
        query = query.filter(AuditLog.company_id == current_user.company_id)
    else:
        return []

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if action:
        query = query.filter(AuditLog.action == action)
    return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()


# ===== PERMISSIONS =====


@router.get("/permissions/")
def list_permissions(
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_superuser),
):
    """List all available permissions (superuser only)."""
    return db.query(Permission).all()


@router.post("/permissions/", status_code=status.HTTP_201_CREATED)
def create_permission(
    name: str,
    module: str,
    action: str,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_superuser),
):
    """Create a new permission (superuser only)."""
    existing = db.query(Permission).filter(Permission.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Permission already exists")
    perm = Permission(name=name, module=module, action=action)
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


@router.get("/users/{user_id}/permissions/")
def get_user_permissions(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_superuser),
):
    """Get permissions assigned to a user (superuser only)."""
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.permissions if hasattr(user, "permissions") else []


@router.post("/users/{user_id}/permissions/{permission_id}")
def assign_permission(
    user_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_superuser),
):
    """Assign a permission to a user (superuser only)."""
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    perm = db.query(Permission).filter(Permission.id == permission_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    if perm not in user.permissions:
        user.permissions.append(perm)
        db.commit()
    return {"message": "Permission assigned"}


@router.delete("/users/{user_id}/permissions/{permission_id}")
def remove_permission(
    user_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_superuser),
):
    """Remove a permission from a user (superuser only)."""
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    perm = db.query(Permission).filter(Permission.id == permission_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    if perm in user.permissions:
        user.permissions.remove(perm)
        db.commit()
    return {"message": "Permission removed"}


# ===== BACKUP & RESTORE =====

@router.post("/backups/create", status_code=status.HTTP_201_CREATED)
def create_backup(
    current_user: user_model.User = Depends(get_current_superuser),
):
    """Create a system backup (database + uploads)."""
    service = BackupService()
    try:
        filename = service.create_backup()
        return {"message": "Respaldo creado exitosamente", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear respaldo: {str(e)}")


@router.get("/backups/", response_model=List[dict])
def list_backups(
    current_user: user_model.User = Depends(get_current_superuser),
):
    """List all available backups."""
    service = BackupService()
    return service.list_backups()


@router.get("/backups/download/{filename}")
def download_backup(
    filename: str,
    current_user: user_model.User = Depends(get_current_superuser),
):
    """Download a backup file."""
    service = BackupService()
    try:
        path = service.get_backup_path(filename)
        return FileResponse(
            path,
            media_type="application/zip",
            filename=path.name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")


@router.post("/backups/restore/{filename}")
def restore_backup(
    filename: str,
    current_user: user_model.User = Depends(get_current_superuser),
):
    """Restore the system from a backup file."""
    service = BackupService()
    try:
        service.restore_backup(filename)
        return {"message": "Sistema restaurado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al restaurar: {str(e)}")


@router.delete("/backups/{filename}")
def delete_backup(
    filename: str,
    current_user: user_model.User = Depends(get_current_superuser),
):
    """Delete a backup file."""
    service = BackupService()
    try:
        if service.delete_backup(filename):
            return {"message": "Respaldo eliminado"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    raise HTTPException(status_code=404, detail="Archivo no encontrado")
