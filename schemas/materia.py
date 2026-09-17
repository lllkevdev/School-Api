from pydantic import BaseModel, Field, ConfigDict


class Materia(BaseModel):
    nombre: str = Field(
        min_length=2,
        max_length=100
    )



class MateriaRespuesta(Materia):
    id: int

    model_config = ConfigDict(from_attributes=True)



class MateriaActualizar(BaseModel):
    nombre: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )