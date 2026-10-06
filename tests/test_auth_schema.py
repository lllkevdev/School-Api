import pytest 
from pydantic import ValidationError

from schemas.auth import LoginRequest, TokenResponse


def test_login_request_valido():
    login = LoginRequest(
        email="usuario@email.com",
        password="password123",
    )

    assert login.email == "usuario@email.com"
    assert login.password == "password123"


def test_login_request_email_invalido():
    with pytest.raises(ValidationError):
        LoginRequest(
            email="email-invalido",
            password="passowrd123",
        )


def test_token_response():
    token = TokenResponse(
        access_token="token-de-prueba",
        token_type="bearer",
    )

    assert token.access_token == "token-de-prueba"
    assert token.token_type == "bearer"