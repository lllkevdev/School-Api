from pydantic import BaseModel, ConfigDict, Field


class InscripcionCrear(BaseModel):
    alumno_id: int = Field(gt=0)
    curso_id: int = Field(gt=0)


class InscripcionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alumno_id: int
    curso_id: int