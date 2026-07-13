"""End-to-end onboarding test: platform-admin creates a tenant, tenant-admin logs in."""


class TestOnboardingFlow:
    def test_platform_admin_creates_tenant_with_admin(
        self, client, platform_admin_headers
    ):
        """Platform admin creates a new company with an embedded admin user."""
        company_data = {
            "name": "Nuevo Cliente S.A.S",
            "nit": "900333333",
            "dv": "1",
            "legal_representative": "Carlos Cliente",
            "address": "Av. 80 #45-12",
            "phone": "3112223344",
            "email": "carlos@nuevocliente.com",
            "regimen": "COMUN",
            "fecha_inicio_actividades": "2024-06-01",
            "resolucion_facturacion": "187600000010",
            "admin_user": {
                "email": "admin@nuevocliente.com",
                "username": "admin_cliente",
                "password": "Cliente@1234",
                "full_name": "Admin Cliente",
            },
        }
        resp = client.post(
            "/api/v1/companies/",
            json=company_data,
            headers=platform_admin_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Nuevo Cliente S.A.S"
        assert data["nit"] == "900333333"

    def test_tenant_admin_can_login_after_onboarding(
        self, client, platform_admin_headers
    ):
        """After onboarding, the tenant admin can log in via /auth/token."""
        company_data = {
            "name": "Tienda Tech S.A.S",
            "nit": "900444444",
            "dv": "2",
            "legal_representative": "Maria Tech",
            "address": "Calle 50 #20-15",
            "phone": "3123334455",
            "email": "maria@tiendatech.com",
            "regimen": "SIMPLE",
            "fecha_inicio_actividades": "2024-03-15",
            "resolucion_facturacion": "187600000020",
            "admin_user": {
                "email": "admin@tiendatech.com",
                "username": "admin_tienda",
                "password": "Tienda@1234",
                "full_name": "Admin Tienda",
            },
        }
        # Platform admin creates the tenant
        resp = client.post(
            "/api/v1/companies/",
            json=company_data,
            headers=platform_admin_headers,
        )
        assert resp.status_code == 201

        # Tenant admin logs in
        login_resp = client.post(
            "/api/v1/auth/token",
            data={"username": "admin_tienda", "password": "Tienda@1234"},
        )
        assert login_resp.status_code == 200
        tokens = login_resp.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens

    def test_tenant_admin_can_access_own_company(
        self, client, platform_admin_headers
    ):
        """Tenant admin can view their own company."""
        company_data = {
            "name": "Mi Tienda S.A.S",
            "nit": "900555555",
            "dv": "3",
            "legal_representative": "Pedro Perez",
            "address": "Carrera 70 #30-25",
            "phone": "3134445566",
            "email": "pedro@mitienda.com",
            "regimen": "COMUN",
            "fecha_inicio_actividades": "2024-01-20",
            "resolucion_facturacion": "187600000030",
            "admin_user": {
                "email": "pedro@mitienda.com",
                "username": "pedro_admin",
                "password": "MiTienda@1234",
                "full_name": "Pedro Perez",
            },
        }
        resp = client.post(
            "/api/v1/companies/",
            json=company_data,
            headers=platform_admin_headers,
        )
        company_id = resp.json()["id"]

        # Login as tenant admin
        login_resp = client.post(
            "/api/v1/auth/token",
            data={"username": "pedro_admin", "password": "MiTienda@1234"},
        )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # View own company
        resp = client.get(f"/api/v1/companies/{company_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == company_id

    def test_duplicate_nit_rejected(self, client, platform_admin_headers, test_company):
        """Cannot create two companies with the same NIT."""
        company_data = {
            "name": "Duplicada S.A.S",
            "nit": test_company.nit,  # same NIT
            "dv": test_company.dv,
            "legal_representative": "Dup Rep",
            "address": "Calle Dup",
            "phone": "3000000000",
            "email": "dup@test.com",
            "regimen": "COMUN",
            "fecha_inicio_actividades": "2024-01-01",
            "resolucion_facturacion": "187600000099",
        }
        resp = client.post(
            "/api/v1/companies/",
            json=company_data,
            headers=platform_admin_headers,
        )
        assert resp.status_code == 400
        assert "already exists" in resp.json()["detail"].lower()

    def test_default_chart_of_accounts_created(
        self, client, platform_admin_headers
    ):
        """Onboarding auto-creates the default PUC chart of accounts."""
        company_data = {
            "name": "Contable S.A.S",
            "nit": "900666666",
            "dv": "4",
            "legal_representative": "Ana Contable",
            "address": "Calle Contable",
            "phone": "3145556677",
            "email": "ana@contable.com",
            "regimen": "COMUN",
            "fecha_inicio_actividades": "2024-02-01",
            "resolucion_facturacion": "187600000040",
        }
        resp = client.post(
            "/api/v1/companies/",
            json=company_data,
            headers=platform_admin_headers,
        )
        assert resp.status_code == 201
        company_id = resp.json()["id"]

        # Default chart of accounts should exist
        resp = client.get(
            f"/api/v1/accounting/chart-of-accounts/?company_id={company_id}",
            headers=platform_admin_headers,
        )
        assert resp.status_code == 200
        accounts = resp.json()
        assert len(accounts) > 0