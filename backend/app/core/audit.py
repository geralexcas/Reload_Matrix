import json
import logging
from functools import wraps
from fastapi import Request

logger = logging.getLogger("app.audit")


def audit_action(entity_type: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            old_values = None
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                logger.warning(
                    f"AUDIT | action=ERROR | entity={entity_type} | error={str(e)}"
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.warning(
                    f"AUDIT | action=ERROR | entity={entity_type} | error={str(e)}"
                )
                raise

        if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:
            return wrapper
        return sync_wrapper

    return decorator


def log_audit(
    db,
    user_id,
    company_id,
    action,
    entity_type,
    entity_id=None,
    old_values=None,
    new_values=None,
    ip_address=None,
):
    from app.models.sql.audit import AuditLog

    entry = AuditLog(
        user_id=user_id,
        company_id=company_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=json.dumps(old_values) if old_values else None,
        new_values=json.dumps(new_values) if new_values else None,
        ip_address=ip_address,
    )
    db.add(entry)
