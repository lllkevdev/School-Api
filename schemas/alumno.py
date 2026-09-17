from pydantic import BaseModel, Field, ConfigDict


class Alumno(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    apellido: str = Field(min_length=2, max_length=100)
    edad: int = Field(gt=0, lt=100)


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