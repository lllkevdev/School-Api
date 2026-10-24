from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routers.alumno import router as alumno_router
from routers.auth import router as auth_router
from routers.curso import router as curso_router
from routers.evaluacion import router as evaluacion_router
from routers.inscripcion import router as inscripcion_router
from routers.calificacion import router as calificacion_router
from routers.invitacion import router as invitacion_router

app = FastAPI(
    title="School API",
    description="API para gestionar cursos, alumnos y calificaciones",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def manejar_error_general(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
    )


app.include_router(alumno_router)
app.include_router(auth_router)
app.include_router(curso_router)
app.include_router(evaluacion_router)
app.include_router(inscripcion_router)
app.include_router(calificacion_router)
app.include_router(invitacion_router)


@app.get("/")
def inicio():
    return {"mensaje": "School API funcionando"}