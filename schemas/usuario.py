from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from schemas.roles import Rol


def normalizar_texto(valor: str | None) -> str | None:
    if valor is None:
        return None

    return valor.strip()


class UsuarioRegistro(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    apellido: str = Field(min_length=2, max_length=100)
    email: EmailStr
    telefono: str | None = Field(default=None, max_length=30)
    password: str = Field(min_length=8, max_length=100)

    @field_validator("nombre", "apellido", mode="before")
    @classmethod
    def normalizar_nombre(cls, valor):
        return normalizar_texto(valor)

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, valor):
        if isinstance(valor, str):
            return valor.strip().lower()
        return valor

    @field_validator("telefono", mode="before")
    @classmethod
    def normalizar_telefono(cls, valor):
        return normalizar_texto(valor)


class UsuarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str | None
    rol: Rol
    activo: bool


class UsuarioActualizar(BaseModel):
    nombre: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    apellido: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    email: EmailStr | None = None
    telefono: str | None = Field(
        default=None,
        max_length=30,
    )

    @field_validator("nombre", "apellido", mode="before")
    @classmethod
    def normalizar_nombre(cls, valor):
        return normalizar_texto(valor)

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, valor):
        if isinstance(valor, str):
            return valor.strip().lower()
        return valor

    @field_validator("telefono", mode="before")
    @classmethod
    def normalizar_telefono(cls, valor):
        return normalizar_texto(valor)