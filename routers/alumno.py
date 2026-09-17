from fastapi import HTTPException
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.dependencies import get_db

from schemas.alumno import ( 
    Alumno, 
    AlumnoRespuesta,
    AlumnoActualizar,
)

from schemas.calificacion import ( 
    AlumnoConCalificaciones,
    PromedioAlumno,
    EstadisticasAlumno
)

from services.alumno_service import (
    crear_alumno,
    obtener_alumnos,
    buscar_alumno,
    actualizar_alumno,
    reemplazar_alumno,
    eliminar_alumno,
    obtener_alumno_con_calificaciones,
)


from services.calificacion_service import (
    obtener_promedio_alumno,
    obtener_estadisticas_alumno,
)

router = APIRouter(
    prefix="/alumnos",
    tags=["Alumnos"]
)



@router.post(
    "/",
    response_model=AlumnoRespuesta,
    status_code=status.HTTP_201_CREATED
)
def crear(alumno: Alumno, db: Session = Depends(get_db)):
    return crear_alumno(db, alumno)



@router.get("/", response_model=list[AlumnoRespuesta])
def obtener(db: Session = Depends(get_db)):
    return obtener_alumnos(db)



@router.get(
    "/{alumno_id}/calificaciones",
    response_model=AlumnoConCalificaciones
)
def obtener_con_calificaciones(
    alumno_id: int,
    db: Session = Depends(get_db)
):
    alumno = obtener_alumno_con_calificaciones(
        db,
        alumno_id
    )

    if alumno is None:
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado"
        )

    return alumno




@router.get("/{alumno_id}/promedio", response_model=PromedioAlumno)
def obtener_promedio(
    alumno_id: int,
    periodo: int | None = None,
    db: Session = Depends(get_db)
):
    promedio, error = obtener_promedio_alumno(
        db,
        alumno_id,
        periodo
    )

    if error == "alumno":
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado"
        )

    if error == "calificaciones":
        raise HTTPException(
            status_code=404,
            detail="No se encontraron calificaciones para el alumno"
        )

    if promedio is None:
        raise HTTPException(
            status_code=500,
            detail="No se pudo obtener el promedio"
        )

    return promedio



@router.get(
    "/{alumno_id}/estadisticas",
    response_model=EstadisticasAlumno
)
def obtener_estadisticas(
    alumno_id: int,
    periodo: int | None = None,
    db: Session = Depends(get_db)
):
    estadisticas, error = obtener_estadisticas_alumno(
        db,
        alumno_id,
        periodo
    )

    if error == "alumno":
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado"
        )

    if error == "calificaciones":
        raise HTTPException(
            status_code=404,
            detail="No se encontraron calificaciones para el alumno"
        )

    if estadisticas is None:
        raise HTTPException(
            status_code=500,
            detail="No se pudieron obtener las estadísticas"
        )

    return estadisticas




@router.get(
    "/{alumno_id}",
    response_model=AlumnoRespuesta
)
def obtener_por_id(
    alumno_id: int, 
    db: Session = Depends(get_db)):
    alumno = buscar_alumno(db, alumno_id)

    if alumno is None:
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado"
        )

    return alumno



@router.patch(
    "/{alumno_id}",
    response_model=AlumnoRespuesta
)
def actualizar(
    alumno_id: int,
    datos: AlumnoActualizar,
    db: Session = Depends(get_db)
):
    alumno = actualizar_alumno(
        db, 
        alumno_id, 
        datos
    )

    if alumno is None:
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado"
        )

    return alumno




@router.put(
    "/{alumno_id}",
    response_model=AlumnoRespuesta
)
def actualizar_alumno_put(
    alumno_id: int,
    datos: Alumno,
    db: Session = Depends(get_db)
):
    alumno = reemplazar_alumno(db, alumno_id, datos)

    if alumno is None:
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado"
        )

    return alumno




@router.delete(
    "/{alumno_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar(
    alumno_id: int, 
    forzar: bool = False,
    db: Session = Depends(get_db)
):
    alumno, error = eliminar_alumno(
        db,
        alumno_id,
        forzar
    )

    if error == "alumno":
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado"
        )

    if error == "tiene_calificaciones":
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar el alumno porque tiene calificaciones asociadas"
        )
    
    return


