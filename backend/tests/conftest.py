import os
import pytest
from datetime import datetime, timedelta, timezone
from app.models.sql.fiscal_period import FiscalPeriod
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.core import security

# ponytail: SQLite en memoria por defecto (rapido, sin RLS). Si TEST_DB=postgres
# (CI), usar DATABASE_URL y aplicar politicas RLS para ejercer la Capa 2 en
# TestRLSBypassBlocked. AGENTS.md describe la limitacion SQLite/RLS.
TEST_DB = os.getenv("TEST_DB", "").lower()

if TEST_DB == "postgres":
    SQLALCHEMY_DATABASE_URL = os.getenv(
        "DATABASE_URL", "postgresql://test_user:test_pass@localhost:5432/test_db"
    )
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Tablas tenant-scoped con RLS (espejo de alembic/versions/9f8e7d6c5b4a)
# ponytail: en lugar de correr alembic upgrade head, inyectamos el SQL de RLS
# inline tras create_all cuando TEST_DB=postgres. Permite reset por test sin
# pelear con la tabla alembic_version.
_RLS_TENANT_TABLES = [
    "products", "product_price_history", "inventory_movements", "partners",
    "fiscal_periods", "invoices", "invoice_resolutions", "credit_debit_notes",
    "wallets", "dian_billing_ranges", "repair_orders", "warranties",
    "technicians", "purchases", "chart_of_accounts", "journal_entries",
    "treasury_transactions", "cash_accounts", "bank_accounts",
    "bank_reconciliations", "check_register",
]


def _apply_rls_policies(eng):
    """Habilita + fuerza RLS y crea la politica tenant_isolation en cada tabla
    tenant-scoped. Idempotente (DROP POLICY IF EXISTS antes de CREATE)."""
    with eng.begin() as conn:
        for table in _RLS_TENANT_TABLES:
            conn.execute(text(f"DROP POLICY IF EXISTS tenant_isolation ON {table}"))
            conn.execute(text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))
            conn.execute(text(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY"))
            conn.execute(text(
                f"CREATE POLICY tenant_isolation ON {table} "
                f"USING (company_id::text = current_setting('app.tenant_id', true))"
            ))


def _drop_rls_policies(eng):
    with eng.begin() as conn:
        for table in _RLS_TENANT_TABLES:
            conn.execute(text(f"DROP POLICY IF EXISTS tenant_isolation ON {table}"))


@pytest.fixture(scope="function")
def db_session():
    # ponytail: reset tenant ContextVar so a prior test that set it (via auth
    # flow or directly) can't leak into a test that uses db_session without client.
    from app.core.tenant_context import current_tenant_id
    current_tenant_id.set(None)
    Base.metadata.create_all(bind=engine)
    if TEST_DB == "postgres":
        _apply_rls_policies(engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        if TEST_DB == "postgres":
            _drop_rls_policies(engine)
        Base.metadata.drop_all(bind=engine)
        current_tenant_id.set(None)


@pytest.fixture(scope="function")
def client(db_session):
    # Disable rate limiting during tests (limiter persists across test calls)
    from app.main import limiter as main_limiter
    from app.api.v1.routers.auth import limiter as auth_limiter
    main_limiter.enabled = False
    auth_limiter.enabled = False

    # Reset tenant context to avoid leakage between tests
    from app.core.tenant_context import current_tenant_id
    current_tenant_id.set(None)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    current_tenant_id.set(None)


@pytest.fixture
def test_company(db_session):
    from app.models.sql.company import Company

    company = Company(
        name="Test Company S.A.S",
        nit="900123456",
        dv="7",
        legal_representative="Juan Perez",
        address="Calle 123 #45-67",
        phone="3001234567",
        email="test@company.com",
        regimen="COMUN",
        fecha_inicio_actividades=date(2024, 1, 1),
        resolucion_facturacion="187600000001",
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def test_user(db_session, test_company):
    from app.models.sql.user import User

    user = User(
        email="admin@test.com",
        username="admin",
        hashed_password=security.get_password_hash("Test@1234"),
        full_name="Admin User",
        role="ADMINISTRADOR",
        is_active=True,
        is_superuser=True,
        company_id=test_company.id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def chart_of_accounts(db_session, test_company):
    from app.services.accounting_service import AccountingService
    service = AccountingService(db_session)
    service.create_default_chart_of_accounts(test_company.id)
    # Create a default open fiscal period covering +/- 1 year from now
    now = datetime.now(timezone.utc)
    fp = FiscalPeriod(
        company_id=test_company.id,
        start_date=now - timedelta(days=365),
        end_date=now + timedelta(days=365),
        is_closed=False,
    )
    db_session.add(fp)
    db_session.commit()


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "Test@1234"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_company_b(db_session):
    """Second company for cross-tenant tests."""
    from app.models.sql.company import Company

    company = Company(
        name="Other Company S.A.S",
        nit="900987654",
        dv="3",
        legal_representative="Ana Lopez",
        address="Carrera 45 #12-34",
        phone="3109876543",
        email="other@company.com",
        regimen="SIMPLE",
        fecha_inicio_actividades=date(2024, 1, 1),
        resolucion_facturacion="187600000002",
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def test_user_non_super(db_session, test_company):
    """Non-superuser (regular tenant user) for isolation tests."""
    from app.models.sql.user import User

    user = User(
        email="vendedor@test.com",
        username="vendedor1",
        hashed_password=security.get_password_hash("Test@1234"),
        full_name="Vendedor User",
        role="VENDEDOR",
        is_active=True,
        is_superuser=False,
        company_id=test_company.id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_non_super_b(db_session, test_company_b):
    """Non-superuser in company B."""
    from app.models.sql.user import User

    user = User(
        email="vendedor@other.com",
        username="vendedor2",
        hashed_password=security.get_password_hash("Test@1234"),
        full_name="Vendedor Other",
        role="VENDEDOR",
        is_active=True,
        is_superuser=False,
        company_id=test_company_b.id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def non_super_auth_headers(client, test_user_non_super):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "vendedor1", "password": "Test@1234"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def non_super_b_auth_headers(client, test_user_non_super_b):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "vendedor2", "password": "Test@1234"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def platform_admin_user(db_session):
    """Platform admin: superuser WITHOUT company_id."""
    from app.models.sql.user import User

    user = User(
        email="platform@admin.com",
        username="platform_admin",
        hashed_password=security.get_password_hash("Test@1234"),
        full_name="Platform Admin",
        role="ADMINISTRADOR",
        is_active=True,
        is_superuser=True,
        company_id=None,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def platform_admin_headers(client, platform_admin_user):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "platform_admin", "password": "Test@1234"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
