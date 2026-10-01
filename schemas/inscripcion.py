from pydantic import BaseModel, Field

class Inscripcion(BaseModel):
    alumno_id: int = Field(gt=0)
    materia_id: int = Field(gt=0)