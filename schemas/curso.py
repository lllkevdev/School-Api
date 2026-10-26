from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalizar_texto(valor: str | None) -> str | None:
    if valor is None:
        return None

    return valor.strip()


class CursoCrear(BaseModel):
    nombre_materia: str = Field(min_length=2, max_length=100)
    division: str = Field(min_length=1, max_length=30)
    anio_lectivo: int = Field(ge=2000, le=2100)
    cantidad_periodos: int = Field(default=3, ge=1, le=12)

    @field_validator("nombre_materia", "division", mode="before")
    @classmethod
    def normalizar_campos_texto(cls, valor):
        return normalizar_texto(valor)


class CursoActualizar(BaseModel):
    nombre_materia: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    division: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )
    anio_lectivo: int | None = Field(
        default=None,
        ge=2000,
        le=2100,
    )
    cantidad_periodos: int | None = Field(
        default=None,
        ge=1,
        le=12,
    )

    @field_validator("nombre_materia", "division", mode="before")
    @classmethod
    def normalizar_campos_texto(cls, valor):
        return normalizar_texto(valor)


class CursoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    docente_id: int
    nombre_materia: str
    division: str
    anio_lectivo: int
    cantidad_periodos: int
    activo: bool


class CursoResumenRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre_materia: str
    division: str
    anio_lectivo: int
    activo: bool