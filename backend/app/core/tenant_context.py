from contextvars import ContextVar
from sqlalchemy import event
from sqlalchemy.orm import Session, with_loader_criteria

from app.core.database import Base

current_tenant_id: ContextVar[int | None] = ContextVar(
    "current_tenant_id", default=None
)

# ponytail: User and AuditLog have company_id but are scoped by the auth/admin
# layer (not auto-filtered) — User queries resolve identity, AuditLog is admin-only.
_EXCLUDE_FROM_AUTO_FILTER = {"User", "AuditLog"}


@event.listens_for(Session, "do_orm_execute")
def _tenant_auto_filter(execute_state):
    """Safety net: auto-filter all SELECT queries on tenant-scoped models.

    Applies company_id == current_tenant_id to every ORM query on models that
    have a company_id column (except User and AuditLog, scoped by the
    auth/admin layer).  When current_tenant_id is None (platform-admin,
    scripts, startup, tests via direct session), no filter is applied.

    ponytail: SELECT-only — services use select-then-modify, so UPDATE/DELETE
    without prior SELECT is not a concern.  Add if bulk operations appear.
    """
    if not execute_state.is_select:
        return

    tenant_id = current_tenant_id.get()
    if tenant_id is None:
        return

    def _criteria(cls):
        if not hasattr(cls, "company_id"):
            return None
        if cls.__name__ in _EXCLUDE_FROM_AUTO_FILTER:
            return None
        return cls.company_id == tenant_id

    execute_state.statement = execute_state.statement.options(
        with_loader_criteria(
            Base, _criteria, propagate_to_loaders=True, track_closure_variables=False
        )
    )