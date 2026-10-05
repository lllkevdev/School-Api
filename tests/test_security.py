from jwt import InvalidTokenError
import pytest

from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


SECRET_KEY = "clave-secreta-de-prueba" 


def test_create_access_token():
    token = create_access_token(
        user_id=1,
        secret_key=SECRET_KEY,
        expires_minutes=60,
    )

    assert isinstance(token, str)
    assert token != ""


def test_decode_access_token():
    token = create_access_token(
        user_id=5,
        secret_key=SECRET_KEY,
        expires_minutes=60,
    )

    payload = decode_access_token(
        token,
        secret_key=SECRET_KEY,
    )

    assert payload["sub"] == "5"
    assert "exp" in payload


def test_decode_access_token_invalid():
    token = create_access_token(
        user_id=5,
        secret_key=SECRET_KEY,
        expires_minutes=30,
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(
            token,
            secret_key="otra-clave",
        )

        
def test_hash_password():
    password = "password123"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert hashed_password.startswith("$argon2")


def test_verify_password_correcta():
    password = "password123"

    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password) is True


def test_verify_password_incorrecta():
    password = "password123"
    
    wrong_password = "wrongpassword"

    hashed_password = hash_password(password)

    assert verify_password(wrong_password, hashed_password) is False