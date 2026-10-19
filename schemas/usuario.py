from pydantic import BaseModel, EmailStr, Field

class UsuarioCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    apellido: str = Field(default="", max_length=100)
    email: EmailStr
    telefono: str | None = Field(default=None, max_length=30)
    password: str = Field(min_length=8, max_length=100)
    rol: str

class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str | None
    rol: str
    activo: bool

    model_config = {"from_attributes": True}


class MaestroCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    apellido: str = Field(min_length=2, max_length=100)
    email: EmailStr
    telefono: str | None = Field(default=None, max_length=30)
    password: str = Field(min_length=8, max_length=100)


class MaestroActualizar(BaseModel):
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