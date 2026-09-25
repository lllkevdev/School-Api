from pydantic import BaseModel, EmailStr, Field


class UsuarioCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    rol: str


class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: str
    activo: bool

    model_config = {
        "from_attributes": True
    }