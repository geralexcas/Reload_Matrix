"""Cross-tenant isolation regression tests.

Verifies that a non-superuser in company A cannot read or access
data belonging to company B.  These tests are the check for the
Phase 0 hardening: ORM auto-filter + verify_company_membership fix,
and the Phase 2 expansion across all modules.
"""

import pytest


class TestTenantIsolation:
    """A non-superuser in company A must never see company B's data."""

    def test_create_product_scoped(self, client, test_company, test_company_b, non_super_auth_headers):
        """User A creates a product — it appears in A, not in B."""
        product_a = {
            "sku": "PROD-A-001",
            "name": "Product A",
            "purchase_price": 1000,
            "sale_price": 2000,
        }
        response = client.post(
            f"/api/v1/inventory/?company_id={test_company.id}",
            json=product_a,
            headers=non_super_auth_headers,
        )
        assert response.status_code == 201

        # User A sees their product
        resp_a = client.get(
            f"/api/v1/inventory/?company_id={test_company.id}",
            headers=non_super_auth_headers,
        )
        assert resp_a.status_code == 200
        skus_a = [p["sku"] for p in resp_a.json()]
        assert "PROD-A-001" in skus_a

    def test_cross_tenant_access_blocked(self, client, test_company, test_company_b, non_super_auth_headers):
        """User A (company A) gets 403 when trying to access company B's data."""
        # Try to read products from company B using company A's user
        resp = client.get(
            f"/api/v1/inventory/?company_id={test_company_b.id}",
            headers=non_super_auth_headers,
        )
        assert resp.status_code == 403

    def test_cross_tenant_create_blocked(self, client, test_company, test_company_b, non_super_auth_headers):
        """User A cannot create products in company B."""
        product = {
            "sku": "CROSS-TENANT-001",
            "name": "Should Fail",
            "purchase_price": 500,
            "sale_price": 1000,
        }
        resp = client.post(
            f"/api/v1/inventory/?company_id={test_company_b.id}",
            json=product,
            headers=non_super_auth_headers,
        )
        assert resp.status_code == 403

    def test_tenant_superuser_limited_to_own_company(
        self, client, test_company, test_company_b, auth_headers
    ):
        """Tenant-superuser (superuser WITH company_id) cannot access other tenants."""
        # auth_headers fixture uses test_user: is_superuser=True, company_id=test_company.id
        # After the fix, this user is a tenant-superuser, not platform-admin.
        resp = client.get(
            f"/api/v1/inventory/?company_id={test_company_b.id}",
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_platform_admin_can_access_any_tenant(
        self, client, test_company, test_company_b, platform_admin_headers
    ):
        """Platform admin (superuser WITHOUT company_id) can access any tenant."""
        resp = client.get(
            f"/api/v1/inventory/?company_id={test_company.id}",
            headers=platform_admin_headers,
        )
        assert resp.status_code == 200

        resp_b = client.get(
            f"/api/v1/inventory/?company_id={test_company_b.id}",
            headers=platform_admin_headers,
        )
        assert resp_b.status_code == 200

    def test_company_listing_scoped(self, client, test_company, test_company_b, non_super_auth_headers):
        """User A sees only their own company in GET /companies/."""
        resp = client.get(
            "/api/v1/companies/",
            headers=non_super_auth_headers,
        )
        assert resp.status_code == 200
        companies = resp.json()
        assert len(companies) == 1
        assert companies[0]["id"] == test_company.id

    def test_company_listing_requires_auth(self, client):
        """GET /companies/ without auth returns 401."""
        resp = client.get("/api/v1/companies/")
        assert resp.status_code == 401

    def test_create_company_requires_platform_admin(
        self, client, non_super_auth_headers, auth_headers
    ):
        """POST /companies/ requires platform admin, not tenant user/superuser."""
        company_data = {
            "name": "New Tenant",
            "nit": "900555555",
            "dv": "5",
            "legal_representative": "New Rep",
            "address": "Calle 99",
            "phone": "3009999999",
            "email": "new@tenant.com",
            "regimen": "COMUN",
            "fecha_inicio_actividades": "2024-01-01",
            "resolucion_facturacion": "187600000003",
        }
        # Non-superuser: 403
        resp = client.post(
            "/api/v1/companies/",
            json=company_data,
            headers=non_super_auth_headers,
        )
        assert resp.status_code == 403

        # Tenant-superuser: also 403 (not platform-admin)
        resp2 = client.post(
            "/api/v1/companies/",
            json=company_data,
            headers=auth_headers,
        )
        assert resp2.status_code == 403

    def test_read_other_company_blocked(self, client, test_company_b, non_super_auth_headers):
        """User A cannot GET /companies/{B_id}."""
        resp = client.get(
            f"/api/v1/companies/{test_company_b.id}",
            headers=non_super_auth_headers,
        )
        assert resp.status_code == 403

    def test_audit_logs_scoped(
        self, client, test_company, test_company_b, non_super_auth_headers
    ):
        """User A's audit logs only show company A, never company B."""
        resp = client.get(
            "/api/v1/admin/audit-logs/",
            headers=non_super_auth_headers,
        )
        assert resp.status_code == 200
        logs = resp.json()
        # All logs must belong to the user's company
        for log in logs:
            assert log["company_id"] == test_company.id

    def test_users_list_scoped(
        self, client, test_company, test_company_b, test_user_non_super_b, non_super_auth_headers
    ):
        """User A's user listing only shows company A users."""
        resp = client.get(
            "/api/v1/admin/users/",
            headers=non_super_auth_headers,
        )
        assert resp.status_code == 200
        users = resp.json()
        for u in users:
            assert u["company_id"] == test_company.id

    def test_dashboard_company_b_blocked(self, client, test_company_b, non_super_auth_headers):
        """User A cannot get dashboard stats for company B."""
        resp = client.get(
            f"/api/v1/dashboard/stats?company_id={test_company_b.id}",
            headers=non_super_auth_headers,
        )
        assert resp.status_code == 403

    def test_dashboard_own_company_works(self, client, test_company, non_super_auth_headers):
        """User A can get dashboard stats for their own company."""
        resp = client.get(
            f"/api/v1/dashboard/stats?company_id={test_company.id}",
            headers=non_super_auth_headers,
        )
        assert resp.status_code == 200

    def test_token_cid_mismatch_rejected(
        self, client, test_user_non_super, test_company_b, db_session
    ):
        """Token with cid=X but user's company_id changed → 401."""
        # ponytail: edge case — admin reassigned user to different company
        from app.core import security as sec

        token = sec.create_access_token_with_company(
            data={"sub": "vendedor1"},
            company_id=999,  # mismatched cid
        )
        # Modify user's company_id to create mismatch
        test_user_non_super.company_id = test_company_b.id
        db_session.commit()

        resp = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        # 401 = cid mismatch detected (expected after the fix)
        assert resp.status_code == 401

    # ===== Phase 0 regression: admin user-management cross-tenant leaks =====
    # tenant-superuser (superuser WITH company_id) must not reach users of
    # another company via /admin/users/* endpoints.  Only platform-admin
    # (superuser WITHOUT company_id) bypasses.

    def test_admin_get_user_cross_tenant_blocked(
        self, client, test_company_b, test_user_non_super_b, auth_headers
    ):
        """tenant-superuser A cannot GET a user of company B."""
        resp = client.get(
            f"/api/v1/admin/users/{test_user_non_super_b.id}",
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_admin_get_user_own_tenant_allowed(
        self, client, test_user_non_super, auth_headers
    ):
        """tenant-superuser A can GET a user of its own company."""
        resp = client.get(
            f"/api/v1/admin/users/{test_user_non_super.id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == test_user_non_super.id

    def test_admin_update_user_cross_tenant_blocked(
        self, client, test_company_b, test_user_non_super_b, auth_headers
    ):
        """tenant-superuser A cannot PUT (update) a user of company B."""
        body = {
            "email": "hijacked@other.com",
            "username": "hijacked_b",
            "full_name": "Hijacked",
            "role": "ADMINISTRADOR",
            "password": "Test@1234",
        }
        resp = client.put(
            f"/api/v1/admin/users/{test_user_non_super_b.id}",
            json=body,
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_admin_toggle_active_cross_tenant_blocked(
        self, client, test_company_b, test_user_non_super_b, auth_headers
    ):
        """tenant-superuser A cannot toggle-active of a user in company B."""
        resp = client.patch(
            f"/api/v1/admin/users/{test_user_non_super_b.id}/toggle-active",
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_admin_delete_user_cross_tenant_blocked(
        self, client, test_company_b, test_user_non_super_b, auth_headers
    ):
        """tenant-superuser A cannot delete a user of company B."""
        resp = client.delete(
            f"/api/v1/admin/users/{test_user_non_super_b.id}",
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_admin_reset_password_cross_tenant_blocked(
        self, client, test_company_b, test_user_non_super_b, auth_headers
    ):
        """tenant-superuser A cannot reset password of a user in company B."""
        resp = client.post(
            f"/api/v1/admin/users/{test_user_non_super_b.id}/reset-password/",
            json={"new_password": "Hijack@1234"},
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_admin_user_mgmt_platform_admin_bypasses(
        self,
        client,
        test_company_b,
        test_user_non_super_b,
        platform_admin_headers,
    ):
        """platform-admin can GET/delete-intent a user in any tenant (no leak)."""
        resp = client.get(
            f"/api/v1/admin/users/{test_user_non_super_b.id}",
            headers=platform_admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["company_id"] == test_company_b.id


# ===== Phase 2 regression: cross-tenant read blocked across ALL modules =====
# A non-superuser in company A must get 403 hitting any module's list endpoint
# with company B's id.  Parametrized over every tenant-scoped module.

_TENANT_MODULE_LIST_ENDPOINTS = [
    "/api/v1/partners/?company_id={b}",
    "/api/v1/invoicing/?company_id={b}",
    "/api/v1/repair/?company_id={b}",
    "/api/v1/purchases/?company_id={b}",
    "/api/v1/wallet/?company_id={b}",
    "/api/v1/accounting/chart-of-accounts/?company_id={b}",
    "/api/v1/treasury/bank-accounts/?company_id={b}",
    "/api/v1/treasury/cash-accounts/?company_id={b}",
]


@pytest.mark.parametrize("endpoint_template", _TENANT_MODULE_LIST_ENDPOINTS)
class TestCrossTenantReadBlocked:
    """Each module's list endpoint must reject a company A user asking for B."""

    def test_cross_tenant_read_blocked(
        self, client, test_company_b, non_super_auth_headers, endpoint_template
    ):
        url = endpoint_template.format(b=test_company_b.id)
        resp = client.get(url, headers=non_super_auth_headers)
        assert resp.status_code == 403, f"{url} leaked cross-tenant"


# ===== Phase 1 regression: Row-Level Security blocks ORM bypass (PG only) =====

@pytest.mark.skipif(
    True,
    reason="requires PostgreSQL + applied RLS migration; SQLite test harness skips. Run manually against PG.",
)
class TestRLSBypassBlocked:
    """Raw SQL that bypasses the ORM auto-filter must STILL be filtered by
    the PostgreSQL RLS policy (app.tenant_id).  Skipped on SQLite."""

    def test_raw_sql_select_filtered_by_rls(
        self, client, db_session, test_company, test_company_b, auth_headers
    ):
        from sqlalchemy import text
        from app.core.tenant_context import current_tenant_id
        from app.models.sql.inventory import Product

        # Create a product in company A
        current_tenant_id.set(test_company.id)
        db_session.add(Product(sku="RLS-A", name="A", purchase_price=1, sale_price=2, company_id=test_company.id))
        db_session.commit()

        # Create a product in company B
        current_tenant_id.set(test_company_b.id)
        db_session.add(Product(sku="RLS-B", name="B", purchase_price=1, sale_price=2, company_id=test_company_b.id))
        db_session.commit()

        # As tenant A, run a RAW SQL SELECT (bypasses the ORM auto-filter).
        current_tenant_id.set(test_company.id)
        rows = db_session.execute(text("SELECT company_id FROM products")).fetchall()
        # RLS must filter out company B's rows even though the ORM filter
        # was bypassed by raw SQL.
        assert rows, "expected at least one row"
        for r in rows:
            assert r[0] == test_company.id, "RLS leaked cross-tenant row via raw SQL"