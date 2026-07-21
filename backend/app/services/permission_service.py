"""Centralized permission assignment for Reload Matrix RBAC.

ADMINISTRADOR gets every permission.  Other roles get a curated subset so
they can actually use the UI without hitting 403s on every endpoint.
"""
from sqlalchemy.orm import Session
from app.models.sql.audit import Permission
from app.models.sql.user import User

# ponytail: role → permission name prefixes.  Each role gets all permissions
# whose name starts with any of the listed prefixes.  The ADMINISTRADOR
# shortcut ("*") grants everything.
ROLE_PERMISSIONS: dict[str, list[str] | None] = {
    "ADMINISTRADOR": None,  # None = all perms
    "CONTADOR": [
        "accounting:", "dashboard:", "partners:", "inventory:read",
        "invoicing:", "wallet:read", "treasury:read", "admin:read", "users:read",
    ],
    "VENDEDOR": [
        "invoicing:", "partners:", "inventory:read", "dashboard:read",
        "wallet:", "repair:read",
    ],
    "BODEGUERO": [
        "inventory:", "purchases:read", "dashboard:read",
    ],
    "TECNICO": [
        "repair:", "inventory:read", "dashboard:read",
    ],
    "FACTURADOR": [
        "invoicing:", "dashboard:read", "partners:read", "inventory:read",
    ],
}

PERMISSION_MATRIX = {
    "company":    ["read", "create", "update"],
    "partners":   ["read", "create", "update", "delete", "manage"],
    "inventory":  ["read", "create", "update", "delete", "manage"],
    "repair":     ["read", "create", "update", "delete", "manage"],
    "invoicing":  ["read", "create", "update", "delete", "cancel", "manage"],
    "purchases":  ["read", "create", "update", "delete", "manage"],
    "wallet":     ["read", "create", "update", "deposit", "withdraw", "manage"],
    "treasury":   ["read", "create", "update", "delete", "transfer", "reconcile", "manage"],
    "accounting": ["read", "create", "update", "delete", "post", "view"],
    "admin":      ["read", "create", "update", "delete", "manage"],
    "users":      ["read", "create", "update", "delete", "manage"],
    "dashboard":  ["read"],
}


def seed_permissions(db: Session) -> list[Permission]:
    """Insert the permission catalog. Idempotent. Returns all Permission rows."""
    added = 0
    for module, actions in PERMISSION_MATRIX.items():
        for action in actions:
            name = f"{module}:{action}"
            if not db.query(Permission).filter(Permission.name == name).first():
                db.add(Permission(name=name, module=module, action=action))
                added += 1
    if added > 0:
        db.commit()
    return db.query(Permission).all()


def assign_all_permissions_to_user(db: Session, user: User) -> int:
    """Grant every permission in the catalog to *user*. Returns count."""
    perms = seed_permissions(db)
    existing = {p.id for p in user.permissions}
    count = 0
    for p in perms:
        if p.id not in existing:
            user.permissions.append(p)
            count += 1
    if count:
        db.commit()
    return count


def backfill_permissions(db: Session) -> dict[str, int]:
    """Assign all permissions to every user with zero permissions.

    Returns ``{username: perm_count}`` for each updated user.
    """
    seed_permissions(db)
    all_perms = db.query(Permission).all()
    results: dict[str, int] = {}
    for user in db.query(User).filter(User.is_active).all():
        if not user.permissions:
            user.permissions = list(all_perms)
            results[user.username] = len(all_perms)
    if results:
        db.commit()
    return results


def assign_role_permissions(db: Session, user: User) -> int:
    """Assign permissions to *user* based on their ``role`` field.

    Returns the number of newly added permissions.
    """
    prefixes = ROLE_PERMISSIONS.get(user.role)

    if prefixes is None:
        # ADMINISTRADOR → grant everything
        perms = db.query(Permission).all()
    else:
        from sqlalchemy import or_
        filters = [Permission.name.startswith(p) for p in prefixes]
        perms = db.query(Permission).filter(or_(*filters)).all()

    existing = {p.id for p in user.permissions}
    count = 0
    for p in perms:
        if p.id not in existing:
            user.permissions.append(p)
            count += 1
    if count:
        db.commit()
    return count
