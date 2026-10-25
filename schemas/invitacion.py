from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class InvitacionCrear(BaseModel):
    alumno_id: int = Field(gt=0)
    curso_id: int = Field(gt=0)
    email: EmailStr


class InvitacionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alumno_id: int
    curso_id: int
    email: EmailStr
    expira_en: datetime
    aceptada_en: datetime | None
    revocada: bool


class InvitacionCreadaRespuesta(InvitacionRespuesta):
    token: str


class InvitacionAceptar(BaseModel):
    token: str = Field(min_length=32, max_length=512)
    password: str = Field(min_length=8, max_length=100)