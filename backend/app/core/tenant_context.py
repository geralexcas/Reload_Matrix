from contextvars import ContextVar
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, with_loader_criteria

from app.core.database import Base

current_tenant_id: ContextVar[int | None] = ContextVar(
    "current_tenant_id", default=None
)


@event.listens_for(Engine, "before_cursor_execute")
def _set_tenant_guc(conn, cursor, statement, parameters, context, executemany):
    """Set app.tenant_id on the PostgreSQL connection before every query so
    RLS policies enforce the tenant even when the ORM auto-filter is bypassed
    (raw SQL, bulk Query.update/delete, or a model missing company_id).

    Reads current_tenant_id (ContextVar set per-request in get_current_user /
    verify_company_membership).  SQLite (tests) is a no-op; the ORM auto-filter
    covers the test path.  When current_tenant_id is None (platform-admin on
    non-tenant endpoints, healthcheck, migrations), RLS denies tenant rows by
    default (app.tenant_id unset → NULL → no match) — that's the safe default.

    ponytail: re-applied before every query so it survives mid-request commits
    (the service layer commits per operation, which would clear a single SET
    LOCAL).  Uses the raw dbapi cursor to SET LOCAL (transaction-scoped,
    auto-clears at commit) without re-firing this SQLAlchemy event.
    """
    if conn.dialect.name != "postgresql":
        return
    tenant_id = current_tenant_id.get()
    if tenant_id is None:
        return
    cursor.execute("SET LOCAL app.tenant_id = %s", (str(tenant_id),))


@event.listens_for(Session, "do_orm_execute")
def _tenant_auto_filter(execute_state):
    """Safety net: auto-filter all SELECT queries on tenant-scoped models.

    Applies company_id == current_tenant_id to every ORM query on models that
    have a company_id column (except User and AuditLog, scoped by the
    auth/admin layer).  When current_tenant_id is None (platform-admin on
    non-tenant endpoints, scripts, startup), no filter is applied — RLS is
    the backstop for those paths.

    ponytail: SELECT-only — services use select-then-modify, so UPDATE/DELETE
    without prior SELECT is not a concern.  Add if bulk operations appear.
    """
    if not execute_state.is_select:
        return

    tenant_id = current_tenant_id.get()
    if tenant_id is None:
        return

    def _criteria(cls):
        try:
            class_name = cls.__name__
        except AttributeError:
            if hasattr(cls, "class_"):
                class_name = cls.class_.__name__
            elif hasattr(cls, "entity"):
                class_name = cls.entity.__name__
            else:
                return None

        # ponytail: `in` operator — SQLAlchemy lambda tracker lo reescribe
        # como SQL contains() cuando cls es una tracked expression.
        if not isinstance(class_name, str) or not hasattr(cls, "company_id"):
            return None
        if class_name == "User" or class_name == "AuditLog":
            return None
        return cls.company_id == tenant_id

    execute_state.statement = execute_state.statement.options(
        with_loader_criteria(
            Base, _criteria, propagate_to_loaders=True, track_closure_variables=False
        )
    )
