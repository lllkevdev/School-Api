from pydantic import BaseModel, Field, ConfigDict


class Calificacion(BaseModel):
    alumno_id: int = Field(gt=0)
    materia_id: int = Field(gt=0)
    nota: float = Field(ge=1, le=10)
    periodo: int = Field(ge=1, le=3)



class CalificacionRespuesta(Calificacion):
    id: int

    model_config = ConfigDict(from_attributes=True)



class CalificacionDetalle(BaseModel):
    id: int
    alumno: str
    materia: str
    nota: float
    periodo: int


class CalificacionActualizar(BaseModel):
    alumno_id: int | None = Field(default=None, gt=0)
    materia_id: int | None = Field(default=None, gt=0)
    nota: float | None = Field(default=None, ge=1, le=10)
    periodo: int | None = Field(default=None, ge=1, le=3)


class CalificacionAlumno(BaseModel):
    materia: str
    nota: float
    periodo: int



class AlumnoConCalificaciones(BaseModel):
    id: int
    nombre: str
    apellido: str
    calificaciones: list[CalificacionAlumno]
    promedio: float



class PromedioAlumno(BaseModel):
    alumno: str
    promedio: float



class EstadisticasAlumno(BaseModel):
    alumno: str
    cantidad_calificaciones: int
    promedio: float
    nota_maxima: float
    nota_minima: float