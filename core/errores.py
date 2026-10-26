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

    "inscripcion_duplicada": (
        409,
        "El alumno ya está inscripto en el curso"
    ),

    "curso_inexistente": (
        404,
        "Curso no encontrado"
    ),

    "maestro": (
        403,
        "No tiene permiso para modificar esta calificacion"
    ),

    "permiso": (
        403,
        "No tiene permiso para realizar esta acción"
    ),
    
    "credenciales": (
        401,
        "Credenciales inválidas"
    ),

    "email_duplicado": (
        409,
        "Ya existe una cuenta con ese correo"
    ),

    "no_autenticado":(
        401,
        "No autenticado"
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
    "maestro_no_encontrado": (
        404,
        "Maestro no encontrado",
    ),
    "curso_inscripcion": (
        404,
        "Curso no encontrado",
    ),
    "inscripcion_con_calificaciones": (
        409,
        "No se puede eliminar una inscripción con calificaciones asociadas",
    ),
    "documento_duplicado": (
        409,
        "DNI ya registrado",
    ),
    "alumno_inexistente" : (
        404,
        "Alumno no encontrado",
    ),
    "alumno_inactivo" : (
        409,
        "El alumno ya está desactivado"
    ),
    "alumno_compartido": (
        409,
        "El alumno también está inscripto en cursos de otro docente. "
        "Quitá su inscripción de tu curso en lugar de desactivarlo."
    ),
    "invitacion_inexistente": (
        404,
        "Invitación no encontrada",
    ),
    "invitacion_invalida": (
        400,
        "Invitación inválida",
    ),
    "invitacion_expirada": (
        410,
        "La invitación ha expirado",
    ),
    "invitacion_usada": (
        409,
        "La invitación ya fue utilizada",
    ),
    "invitacion_revocada": (
        409,
        "La invitación fue revocada",
    ),
    "invitacion_conflicto": (
        409,
        "El correo ya está asociado a otra cuenta",
    ),
    "curso_inactivo": (
        409,
        "El curso está inactivo",
    ),
    "curso_activo": (
        409,
        "El curso ya está activo",
    ),
    "tiene_inscripciones": (
        409,
        "No se puede eliminar el curso porque tiene inscripciones asociadas",
    ),
    "tiene_evaluaciones": (
        409,
        "No se puede eliminar el curso porque tiene evaluaciones asociadas",
    ),
    "tiene_invitaciones": (
        409,
        "No se puede eliminar el curso porque tiene invitaciones asociadas",
    ),
    "foto_no_encontrada": (
        404,
        "Foto de perfil no encontrada",
    ),
    "foto_muy_grande": (
        413,
        "La foto supera el tamaño máximo permitido",
    ),
    "foto_formato_invalido": (
        415,
        "El formato de la imagen no está permitido",
    ),
    "foto_invalida": (
        400,
        "El archivo no es una imagen válida",
    ),
    "archivo_muy_grande": (
        413,
        "El archivo supera el tamaño máximo permitido",
    ),
    "archivo_formato_invalido": (
        415,
        "El formato del archivo no está permitido",
    ),
    "archivo_invalido": (
        400,
        "El archivo no es válido o no tiene el formato esperado",
    ),
    "archivo_vacio": (
        400,
        "El archivo no contiene alumnos para importar",
    ),
    "demasiadas_filas": (
        400,
        "El archivo supera el máximo de 500 filas",
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