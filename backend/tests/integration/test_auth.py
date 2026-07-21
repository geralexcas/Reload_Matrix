import pytest


class TestAuthFlow:
    def test_register_and_login(self, client, test_company):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@test.com",
                "username": "newuser",
                "password": "Secure@1234",
                "full_name": "New User",
                "role": "VENDEDOR",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@test.com"

        response = client.post(
            "/api/v1/auth/token",
            data={"username": "newuser", "password": "Secure@1234"},
        )
        assert response.status_code == 200
        tokens = response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "Wrong@1234"},
        )
        assert response.status_code == 401

    def test_login_inactive_user(self, client, db_session, test_company):
        from app.models.sql.user import User
        from app.core import security

        user = User(
            email="inactive@test.com",
            username="inactive",
            hashed_password=security.get_password_hash("Secure@1234"),
            full_name="Inactive User",
            is_active=False,
            is_superuser=False,
            company_id=test_company.id,
        )
        db_session.add(user)
        db_session.commit()

        response = client.post(
            "/api/v1/auth/token",
            data={"username": "inactive", "password": "Secure@1234"},
        )
        assert response.status_code == 403

    def test_refresh_token_flow(self, client, test_user):
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "Test@1234"},
        )
        assert response.status_code == 200
        refresh_token = response.json()["refresh_token"]

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        new_tokens = response.json()
        assert "access_token" in new_tokens

    def test_logout_invalidates_refresh_token(self, client, test_user):
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "Test@1234"},
        )
        refresh_token = response.json()["refresh_token"]

        response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 401

    def test_weak_password_rejected(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@test.com",
                "username": "weakuser",
                "password": "123",
                "full_name": "Weak User",
            },
        )
        assert response.status_code == 422

    def test_protected_endpoint_without_auth(self, client, test_company):
        response = client.get(f"/api/v1/inventory/?company_id={test_company.id}")
        assert response.status_code == 401

    def test_protected_endpoint_with_auth(self, client, auth_headers, test_company):
        response = client.get(
            f"/api/v1/inventory/?company_id={test_company.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_refresh_token_rejected_as_access(self, client, test_user):
        """audit C3: refresh token must NOT be usable as access token."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "Test@1234"},
        )
        assert response.status_code == 200
        refresh_token = response.json()["refresh_token"]

        # Using the refresh token as Bearer must be rejected by get_current_user.
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert response.status_code == 401

    def test_logout_revokes_access_token(self, client, test_user, test_company):
        """audit C4: logout must revoke the access token via jti denylist."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "Test@1234"},
        )
        assert response.status_code == 200
        access_token = response.json()["access_token"]
        refresh_token = response.json()["refresh_token"]

        # Access token works before logout.
        assert client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        ).status_code == 200

        # Logout sends both tokens.
        response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token, "access_token": access_token},
        )
        assert response.status_code == 200

        # Access token must now be rejected (jti revoked).
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 401
        assert "revoked" in response.json()["detail"].lower()
