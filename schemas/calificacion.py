from pydantic import BaseModel, ConfigDict, Field

from schemas.curso import CursoResumenRespuesta
from schemas.evaluacion import EvaluacionRespuesta


class CalificacionCrear(BaseModel):
    alumno_id: int = Field(gt=0)
    evaluacion_id: int = Field(gt=0)
    nota: float = Field(ge=1, le=10)


class CalificacionActualizar(BaseModel):
    nota: float = Field(ge=1, le=10)


class CalificacionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alumno_id: int
    evaluacion_id: int
    curso_id: int
    nota: float


class CalificacionAlumnoRespuesta(CalificacionRespuesta):
    curso: CursoResumenRespuesta
    evaluacion: EvaluacionRespuesta