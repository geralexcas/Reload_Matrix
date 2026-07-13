"""Platform admin panel tests: manage tenants, toggle active, cross-tenant users."""


class TestPlatformAdminPanel:

    def test_list_tenants_platform_admin(self, client, test_company, test_company_b, platform_admin_headers):
        """Platform admin sees all tenants."""
        resp = client.get("/api/v1/companies/", headers=platform_admin_headers)
        assert resp.status_code == 200
        companies = resp.json()
        ids = [c["id"] for c in companies]
        assert test_company.id in ids
        assert test_company_b.id in ids

    def test_list_tenants_tenant_user_only_own(
        self, client, test_company, test_company_b, non_super_auth_headers
    ):
        """Tenant user only sees their own company."""
        resp = client.get("/api/v1/companies/", headers=non_super_auth_headers)
        assert resp.status_code == 200
        companies = resp.json()
        assert len(companies) == 1
        assert companies[0]["id"] == test_company.id

    def test_create_tenant_platform_admin(self, client, platform_admin_headers):
        """Platform admin can create a tenant."""
        company_data = {
            "name": "Panel Test S.A.S",
            "nit": "900777777",
            "dv": "5",
            "legal_representative": "Panel Rep",
            "address": "Calle panel",
            "phone": "3156667778",
            "email": "panel@test.com",
            "regimen": "COMUN",
            "fecha_inicio_actividades": "2024-05-01",
            "resolucion_facturacion": "187600000050",
        }
        resp = client.post(
            "/api/v1/companies/",
            json=company_data,
            headers=platform_admin_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "Panel Test S.A.S"

    def test_create_tenant_tenant_admin_forbidden(
        self, client, auth_headers
    ):
        """Tenant-superuser cannot create tenants (only platform admin)."""
        company_data = {
            "name": "Should Fail",
            "nit": "900888888",
            "dv": "6",
            "legal_representative": "Fail",
            "regimen": "COMUN",
            "fecha_inicio_actividades": "2024-01-01",
        }
        resp = client.post(
            "/api/v1/companies/",
            json=company_data,
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_toggle_active_platform_admin(
        self, client, test_company_b, platform_admin_headers
    ):
        """Platform admin can deactivate and reactivate a tenant."""
        original_state = test_company_b.is_active

        # Deactivate
        resp = client.patch(
            f"/api/v1/companies/{test_company_b.id}/toggle-active",
            headers=platform_admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["is_active"] != original_state

        # Reactivate
        resp2 = client.patch(
            f"/api/v1/companies/{test_company_b.id}/toggle-active",
            headers=platform_admin_headers,
        )
        assert resp2.status_code == 200
        assert resp2.json()["is_active"] == original_state

    def test_toggle_active_tenant_admin_forbidden(
        self, client, test_company, auth_headers
    ):
        """Tenant-superuser cannot toggle-active."""
        resp = client.patch(
            f"/api/v1/companies/{test_company.id}/toggle-active",
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_toggle_active_non_existing(self, client, platform_admin_headers):
        """404 for non-existing company."""
        resp = client.patch(
            "/api/v1/companies/99999/toggle-active",
            headers=platform_admin_headers,
        )
        assert resp.status_code == 404

    def test_list_users_cross_tenant(
        self, client, test_company, test_company_b, platform_admin_headers
    ):
        """Platform admin can list users filtered by any company."""
        resp = client.get(
            "/api/v1/admin/users/",
            params={"company_id": test_company_b.id},
            headers=platform_admin_headers,
        )
        assert resp.status_code == 200
        users = resp.json()
        for u in users:
            assert u["company_id"] == test_company_b.id

    def test_read_company_platform_admin(
        self, client, test_company_b, platform_admin_headers
    ):
        """Platform admin can read any company's details."""
        resp = client.get(
            f"/api/v1/companies/{test_company_b.id}",
            headers=platform_admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == test_company_b.id

    # ===== CREATE USER (platform admin → any tenant) =====

    def test_create_user_platform_admin_normal(
        self, client, test_company_b, platform_admin_headers
    ):
        """Platform admin creates a normal user (is_superuser=False) in a tenant."""
        payload = {
            "username": "panel_user1",
            "email": "panel_user1@test.com",
            "full_name": "Panel User One",
            "password": "Test@1234",
            "role": "VENDEDOR",
            "is_superuser": False,
            "company_id": test_company_b.id,
        }
        resp = client.post(
            "/api/v1/admin/users/", json=payload, headers=platform_admin_headers
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["company_id"] == test_company_b.id
        assert body["is_superuser"] is False
        assert body["role"] == "VENDEDOR"

        # User appears in the tenant's user list
        listing = client.get(
            "/api/v1/admin/users/",
            params={"company_id": test_company_b.id},
            headers=platform_admin_headers,
        )
        assert listing.status_code == 200
        usernames = [u["username"] for u in listing.json()]
        assert "panel_user1" in usernames

    def test_create_user_platform_admin_tenant_admin(
        self, client, test_company_b, platform_admin_headers
    ):
        """Platform admin creates a tenant-admin (is_superuser=True) in a tenant."""
        payload = {
            "username": "panel_admin1",
            "email": "panel_admin1@test.com",
            "full_name": "Panel Admin One",
            "password": "Test@1234",
            "role": "ADMINISTRADOR",
            "is_superuser": True,
            "company_id": test_company_b.id,
        }
        resp = client.post(
            "/api/v1/admin/users/", json=payload, headers=platform_admin_headers
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["company_id"] == test_company_b.id
        assert body["is_superuser"] is True
        assert body["role"] == "ADMINISTRADOR"

    def test_create_user_tenant_superuser_forbidden(
        self, client, test_company, auth_headers
    ):
        """Tenant-superuser cannot create users (platform admin only)."""
        payload = {
            "username": "should_fail",
            "email": "should_fail@test.com",
            "full_name": "Should Fail",
            "password": "Test@1234",
            "role": "VENDEDOR",
            "company_id": test_company.id,
        }
        resp = client.post(
            "/api/v1/admin/users/", json=payload, headers=auth_headers
        )
        assert resp.status_code == 403