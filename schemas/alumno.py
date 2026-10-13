from pydantic import BaseModel, Field, ConfigDict, field_validator


def normalizar_texto(valor):
    if valor is None:
        return None

    return valor.strip().title()

class Alumno(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    apellido: str = Field(min_length=2, max_length=100)
    edad: int = Field(gt=0, lt=100)

    @field_validator("nombre", "apellido", mode="before")
    @classmethod
    def normalizar_nombre(cls, valor):
        return normalizar_texto(valor)

class AlumnoRespuesta(Alumno):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AlumnoActualizar(BaseModel):
    nombre: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    apellido: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    edad: int | None = Field(
        default=None,
        gt=0,
        lt=100
    )

    @field_validator("nombre", "apellido", mode="before")
    @classmethod
    def normalizar_nombre(cls, valor):
        return normalizar_texto(valor)
