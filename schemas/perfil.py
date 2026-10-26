from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas.alumno import AlumnoRespuesta
from schemas.usuario import UsuarioRespuesta, normalizar_texto


class PerfilRespuesta(BaseModel):
    usuario: UsuarioRespuesta
    alumno: AlumnoRespuesta | None = None


class PerfilActualizar(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
    telefono: str | None = Field(
        default=None,
        max_length=30,
    )

    @field_validator("nombre", "apellido", mode="before")
    @classmethod
    def validar_nombre_no_nulo(cls, valor):
        if valor is None:
            raise ValueError("El campo no puede ser nulo")

        return normalizar_texto(valor)

    @field_validator("telefono", mode="before")
    @classmethod
    def normalizar_telefono(cls, valor):
        if isinstance(valor, str):
            return valor.strip()

        return valor
