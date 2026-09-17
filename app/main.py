from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from routers.alumno import router as alumno_router
from routers.materia import router as materia_router
from routers.calificacion import router as calificacion_router


app = FastAPI(
    title="School API",
    description="API para gestionar alumnos, materias y calificaciones",
    version="1.0.0"
)


@app.exception_handler(Exception)
async def manejar_error_general(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )


app.include_router(alumno_router)
app.include_router(materia_router)
app.include_router(calificacion_router)


@app.get("/")
def inicio():
    return {"mensaje": "API de alumnos funcionando"}
