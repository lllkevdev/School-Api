from fastapi import HTTPException


ERRORES_HTTP = {
    "alumno": (404, "Alumno no encontrado"),
    "materia": (404, "Materia no encontrada"),
    "calificacion": (404, "Calificación no encontrada"),

    "alumno_calificacion": (404, "El alumno no existe"),
    "materia_calificacion": (404, "La materia no existe"),

    "calificaciones": (
        404,
        "No se encontraron calificaciones para el alumno"
    ),

    "alumno_inscripcion": (
        404,
        "El alumno no existe"
    ),

    "materia_inscripcion": (
        404,
        "La materia no existe"
    ),

    "inscripcion_calificacion": (
        409,
        "El alumno no esta inscripto en la materia"
    ),

    "conflicto": (
        409,
        "Ya existe una calificación para ese alumno, materia y periodo"
    ),

    "inscripcion_conflicto": (
        409,
        "El alumno ya esta inscripto en la materia"
    ),

    "materia_conflicto": (
        409,
        "Ya existe una materia con ese nombre"
    ),

    "inscripcion_inexistente": (
        404,
        "La inscripcion no existe"
    ),

    "maestro": (
        403,
        "No tiene permiso para modificar esta calificacion"
    ),

    "permiso": (
        403,
        "No tiene permiso para realizar esta acción"
    ),

    "tiene_calificaciones": (
    409,
    "No se puede eliminar la materia porque tiene calificaciones asociadas"
    ),

    "tiene_calificaciones_alumno": (
        409,
        "No se puede eliminar el alumno porque tiene calificaciones asociadas"
    ),

    "sin_cambios": (
    400,
    "Debe proporcionar al menos un campo para actualizar"
),
}


def error_to_http(error: str | None) -> None:
    """Convierte un código de error del service en una HTTPException."""

    if error is None:
        return

    status_code, detail = ERRORES_HTTP.get(error, (400, error))

    raise HTTPException(
        status_code=status_code,
        detail=detail
    )