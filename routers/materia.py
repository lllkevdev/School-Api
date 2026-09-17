from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.dependencies import get_db

from schemas.materia import (
    Materia, 
    MateriaRespuesta, 
    MateriaActualizar as MateriaActualizarSchema
)

from services.materia_service import (
    crear_materia,
    obtener_materias,
    buscar_materia,
    actualizar_materia,
    actualizar_materia_parcialmente,
    eliminar_materia
)


router = APIRouter(
    prefix="/materias",
    tags=["Materias"]
)


@router.post(
    "/",
    response_model=MateriaRespuesta,
    status_code=status.HTTP_201_CREATED
)
def crear(materia: Materia, db: Session = Depends(get_db)):

    try:
        return crear_materia(db, materia)

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una materia con ese nombre"
        )


@router.get(
    "/",
    response_model=list[MateriaRespuesta]
)
def obtener(db: Session = Depends(get_db)):
    return obtener_materias(db)



@router.get(
    "/{materia_id}",
    response_model=MateriaRespuesta
)
def obtener_por_id(materia_id: int, db: Session = Depends(get_db)):
    materia = buscar_materia(db, materia_id)
    if not materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    return materia




@router.put(
    "/{materia_id}",
    response_model=MateriaRespuesta
)
def actualizar_materia_put(
    materia_id: int, 
    materia: Materia, db: Session = Depends(get_db)
):
    try:
        materia_actualizada = actualizar_materia(db, materia_id, materia)

        if not materia_actualizada:
            raise HTTPException(status_code=404, detail="Materia no encontrada")
        return materia_actualizada
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una materia con ese nombre"
        )



@router.patch(
    "/{materia_id}",
    response_model=MateriaRespuesta
)
def actualizar_materia_patch(
    materia_id: int, 
    materia: MateriaActualizarSchema, 
    db: Session = Depends(get_db)
):
    try:
        materia_actualizada, error = actualizar_materia_parcialmente(
            db, 
            materia_id, 
            materia
        )
        
        if error == "materia":
            raise HTTPException(
                status_code=404, 
                detail="Materia no encontrada"
            )

        if error == "sin_cambios":
            raise HTTPException(
                status_code=400,
                detail="Debe proporcionar al menos un campo para actualizar"
            )
        
        return materia_actualizada
    
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una materia con ese nombre"
        )




@router.delete(
    "/{materia_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar(
    materia_id: int, 
    db: Session = Depends(get_db)
):
    materia_eliminada, error = eliminar_materia(db, materia_id)

    if error == "materia":
        raise HTTPException(
            status_code=404,
            detail="Materia no encontrada"
        )

    if error == "tiene_calificaciones":
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar la materia porque tiene calificaciones asociadas"
        )

    return 