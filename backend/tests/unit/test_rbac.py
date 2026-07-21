"""Tests RBAC: require_permission + the platform-admin-only bypass (audit C2)."""
import pytest


class TestRBAC:
    def test_user_without_permission_denied(self, client, db_session, test_company):
        """A user without any permission must get 403 on a protected endpoint."""
        from app.models.sql.user import User
        from app.core import security

        u = User(
            email="nope@test.com",
            username="nope",
            hashed_password=security.get_password_hash("Test@1234"),
            full_name="No Perm",
            role="VENDEDOR",
            is_active=True,
            is_superuser=False,
            company_id=test_company.id,
        )
        db_session.add(u)
        db_session.commit()

        r = client.post(
            "/api/v1/auth/token",
            data={"username": "nope", "password": "Test@1234"},
        )
        assert r.status_code == 200
        headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

        # Inventory read needs `inventory:read`; user has no perms → 403.
        r = client.get(
            f"/api/v1/inventory/?company_id={test_company.id}",
            headers=headers,
        )
        assert r.status_code == 403
        assert "Permission denied" in r.json()["detail"]

    def test_tenant_superuser_without_perm_still_denied(
        self, client, db_session, test_company
    ):
        """audit C2: a tenant-superuser (with company_id) MUST NOT bypass
        require_permission. Only platform-admin (no company_id) bypasses."""
        from app.models.sql.user import User
        from app.core import security

        u = User(
            email="supnope@test.com",
            username="supnope",
            hashed_password=security.get_password_hash("Test@1234"),
            full_name="Sup No Perm",
            role="ADMINISTRADOR",
            is_active=True,
            is_superuser=True,            # superuser
            company_id=test_company.id,   # but tied to a tenant
        )
        db_session.add(u)
        db_session.commit()

        r = client.post(
            "/api/v1/auth/token",
            data={"username": "supnope", "password": "Test@1234"},
        )
        assert r.status_code == 200
        headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

        # Even superuser tied to a tenant should be denied without the perm.
        r = client.get(
            f"/api/v1/inventory/?company_id={test_company.id}",
            headers=headers,
        )
        assert r.status_code == 403

    def test_platform_admin_bypasses_permissions(
        self, client, platform_admin_user, test_company, platform_admin_headers
    ):
        """audit C2: platform-admin (superuser WITHOUT company_id) does bypass."""
        # Inventory read needs `inventory:read`. Platform admin has no perms
        # at all but must be allowed because it operates cross-tenant.
        # verify_company_membership requires company_id as query param.
        r = client.get(
            f"/api/v1/inventory/?company_id={test_company.id}",
            headers=platform_admin_headers,
        )
        # Either 200 (allowed, empty result) — must NOT be 403 RBAC.
        assert r.status_code != 403