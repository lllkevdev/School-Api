from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EvaluacionCrear(BaseModel):
    curso_id: int = Field(gt=0)
    titulo: str = Field(min_length=1, max_length=150)
    fecha: date
    periodo: int = Field(ge=1)

    @field_validator("titulo", mode="before")
    @classmethod
    def normalizar_titulo(cls, valor):
        if isinstance(valor, str):
            return valor.strip()
        return valor


class EvaluacionActualizar(BaseModel):
    titulo: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    fecha: date | None = None
    periodo: int | None = Field(default=None, ge=1)

    @field_validator("titulo", mode="before")
    @classmethod
    def normalizar_titulo(cls, valor):
        if isinstance(valor, str):
            return valor.strip()
        return valor


class EvaluacionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    curso_id: int
    titulo: str
    fecha: date
    periodo: int