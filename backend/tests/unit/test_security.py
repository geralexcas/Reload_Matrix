import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
)
from app.core.config import settings
from datetime import timedelta
from jose import jwt


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "Secure@Pass123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_wrong_password_fails(self):
        hashed = get_password_hash("Secure@Pass123")
        assert verify_password("WrongPassword@1", hashed) is False

    def test_different_hashes(self):
        password = "Secure@Pass123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2


class TestPasswordValidation:
    def test_valid_password(self):
        is_valid, msg = validate_password_strength("Secure@123")
        assert is_valid is True

    def test_too_short(self):
        is_valid, msg = validate_password_strength("Ab1@")
        assert is_valid is False
        assert "8 characters" in msg

    def test_no_uppercase(self):
        is_valid, msg = validate_password_strength("secure@123")
        assert is_valid is False
        assert "uppercase" in msg

    def test_no_lowercase(self):
        is_valid, msg = validate_password_strength("SECURE@123")
        assert is_valid is False
        assert "lowercase" in msg

    def test_no_number(self):
        is_valid, msg = validate_password_strength("Secure@Pass")
        assert is_valid is False
        assert "number" in msg

    def test_no_special_char(self):
        is_valid, msg = validate_password_strength("SecurePass123")
        assert is_valid is False
        assert "special" in msg


class TestAccessToken:
    def test_create_access_token(self):
        token = create_access_token(data={"sub": "testuser"})
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == "testuser"
        assert "exp" in payload

    def test_access_token_expiry(self):
        token = create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(minutes=5),
        )
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == "testuser"

    def test_expired_token(self):
        token = create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(seconds=-1),
        )
        with pytest.raises(Exception):
            jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


class TestRefreshToken:
    def test_create_refresh_token(self):
        token = create_refresh_token(data={"sub": "testuser"})
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == "testuser"
        assert payload["type"] == "refresh"

    def test_refresh_token_has_longer_expiry(self):
        access = create_access_token(data={"sub": "testuser"})
        refresh = create_refresh_token(data={"sub": "testuser"})
        access_payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        refresh_payload = jwt.decode(
            refresh, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert refresh_payload["exp"] > access_payload["exp"]
