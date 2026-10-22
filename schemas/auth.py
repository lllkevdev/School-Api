from pydantic import BaseModel, EmailStr, field_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, valor):
        if isinstance(valor, str):
            return valor.strip().lower()
        return valor


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"