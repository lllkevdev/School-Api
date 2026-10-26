from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from schemas.inscripcion import InscripcionRespuesta


def normalizar_texto(valor: str | None) -> str | None:
    if valor is None:
        return None

    return valor.strip().title()


def normalizar_documento(valor: str | None) -> str | None:
    if valor is None:
        return None

    return valor.strip()


class AlumnoCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    apellido: str = Field(min_length=2, max_length=100)
    documento_identidad: str = Field(min_length=5, max_length=20)
    fecha_nacimiento: date

    @field_validator("nombre", "apellido", mode="before")
    @classmethod
    def normalizar_nombre(cls, valor):
        return normalizar_texto(valor)

    @field_validator("documento_identidad", mode="before")
    @classmethod
    def normalizar_documento_identidad(cls, valor):
        return normalizar_documento(valor)

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_fecha_nacimiento(cls, valor: date) -> date:
        if valor > date.today():
            raise ValueError("La fecha de nacimiento no puede ser futura")

        return valor


class AlumnoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellido: str
    documento_identidad: str
    fecha_nacimiento: date
    activo: bool


class AlumnoConInscripcionCrear(AlumnoCrear):
    curso_id: int = Field(gt=0)
    confirmar_existente: bool = False


class AlumnoConInscripcionRespuesta(BaseModel):
    alumno: AlumnoRespuesta
    inscripcion: InscripcionRespuesta | None
    requiere_confirmacion: bool


class AlumnoActualizar(BaseModel):
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
    documento_identidad: str | None = Field(
        default=None,
        min_length=5,
        max_length=20,
    )
    fecha_nacimiento: date | None = None

    @field_validator("nombre", "apellido", mode="before")
    @classmethod
    def normalizar_nombre(cls, valor):
        return normalizar_texto(valor)

    @field_validator("documento_identidad", mode="before")
    @classmethod
    def normalizar_documento_identidad(cls, valor):
        return normalizar_documento(valor)

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_fecha_nacimiento(
        cls,
        valor: date | None,
    ) -> date | None:
        if valor is not None and valor > date.today():
            raise ValueError("La fecha de nacimiento no puede ser futura")

        return valor