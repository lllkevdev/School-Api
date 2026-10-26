import csv
import io
from datetime import date

from openpyxl import Workbook

from core.security import hash_password
from models.alumno import Alumno
from models.curso import Curso
from models.inscripcion import Inscripcion
from models.usuario import Usuario
from schemas.roles import Rol
from services.importacion_service import MAX_BYTES


ENCABEZADO = [
    "nombre",
    "apellido",
    "documento",
    "fecha_nacimiento",
]


def crear_curso(db, docente, activo=True):
    curso = Curso(
        docente_id=docente.id,
        nombre_materia="Matematica",
        division="A",
        anio_lectivo=2026,
        cantidad_periodos=3,
        activo=activo,
    )
    db.add(curso)
    db.commit()
    db.refresh(curso)
    return curso


def crear_otro_docente(db):
    docente = Usuario(
        nombre="Otro",
        email="otro.importacion@test.com",
        password_hash=hash_password("123456"),
        rol=Rol.ADMIN,
        activo=True,
    )
    db.add(docente)
    db.commit()
    db.refresh(docente)
    return docente


def crear_alumno(
    db,
    documento="12345678",
    nombre="Alumno",
    activo=True,
):
    alumno = Alumno(
        nombre=nombre,
        apellido="Existente",
        documento_identidad=documento,
        fecha_nacimiento=date(2008, 4, 12),
        activo=activo,
    )
    db.add(alumno)
    db.commit()
    db.refresh(alumno)
    return alumno


def crear_csv(
    filas,
    encabezado=None,
    delimitador=",",
):
    salida = io.StringIO()
    escritor = csv.writer(
        salida,
        delimiter=delimitador,
        lineterminator="\n",
    )
    escritor.writerow(encabezado or ENCABEZADO)

    for fila in filas:
        escritor.writerow(fila)

    return salida.getvalue().encode("utf-8")


def crear_xlsx(filas, encabezado=None):
    libro = Workbook()
    hoja = libro.active
    hoja.append(encabezado or ENCABEZADO)

    for fila in filas:
        hoja.append(fila)

    salida = io.BytesIO()
    libro.save(salida)
    libro.close()
    salida.seek(0)
    return salida.getvalue()


def importar(
    client,
    headers,
    curso_id,
    contenido,
    nombre="alumnos.csv",
):
    return client.post(
        "/alumnos/importar",
        headers=headers,
        data={"curso_id": str(curso_id)},
        files={
            "archivo": (
                nombre,
                contenido,
                "text/csv" if nombre.endswith(".csv") else (
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
            )
        },
    )


def test_importar_csv_crea_alumnos_e_inscripciones(
    client,
    auth_headers_admin,
    db,
    usuario_admin,
):
    curso = crear_curso(db, usuario_admin)
    contenido = crear_csv(
        [
            ["  ana  ", "  gomez  ", "  IMPORT-001  ", "12/04/2009"],
            ["Luis", "Perez", "IMPORT-002", "2008-03-15"],
        ],
        encabezado=[
            "Nombre",
            "Apellido",
            "Documento de identidad",
            "Fecha de nacimiento",
        ],
        delimitador=";",
    )

    respuesta = importar(
        client,
        auth_headers_admin,
        curso.id,
        contenido,
    )

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["total_filas"] == 2
    assert datos["alumnos_creados"] == 2
    assert datos["alumnos_inscriptos"] == 2
    assert datos["alumnos_omitidos"] == 0
    assert datos["errores"] == []
    assert len(datos["alumnos"]) == 2
    assert len(datos["inscripciones"]) == 2

    ana = db.query(Alumno).filter_by(
        documento_identidad="IMPORT-001"
    ).one()
    assert ana.nombre == "Ana"
    assert ana.apellido == "Gomez"
    assert ana.fecha_nacimiento == date(2009, 4, 12)
    assert db.query(Inscripcion).filter_by(
        alumno_id=ana.id,
        curso_id=curso.id,
    ).count() == 1


def test_importar_reutiliza_perfil_sin_modificarlo(
    client,
    auth_headers_admin,
    db,
    usuario_admin,
):
    curso = crear_curso(db, usuario_admin)
    alumno = crear_alumno(
        db,
        documento="PERFIL-001",
        nombre="Nombre",
    )
    contenido = crear_csv(
        [["Otro", "Nombre", "PERFIL-001", "2007-01-01"]]
    )

    respuesta = importar(
        client,
        auth_headers_admin,
        curso.id,
        contenido,
    )

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["alumnos_creados"] == 0
    assert datos["alumnos_inscriptos"] == 1
    assert len(datos["alumnos"]) == 1

    db.refresh(alumno)
    assert alumno.nombre == "Nombre"
    assert alumno.fecha_nacimiento == date(2008, 4, 12)
    assert db.query(Inscripcion).filter_by(
        alumno_id=alumno.id,
        curso_id=curso.id,
    ).count() == 1


def test_importar_omite_alumno_ya_inscripto(
    client,
    auth_headers_admin,
    db,
    usuario_admin,
):
    curso = crear_curso(db, usuario_admin)
    alumno = crear_alumno(db, documento="YA-INSCRIPTO")
    db.add(Inscripcion(alumno_id=alumno.id, curso_id=curso.id))
    db.commit()
    contenido = crear_csv(
        [["Alumno", "Existente", "YA-INSCRIPTO", "12/04/2008"]]
    )

    respuesta = importar(
        client,
        auth_headers_admin,
        curso.id,
        contenido,
    )

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["alumnos_omitidos"] == 1
    assert datos["alumnos_inscriptos"] == 0
    assert datos["errores"] == []
    assert db.query(Inscripcion).count() == 1


def test_importar_rechaza_alumno_inactivo(
    client,
    auth_headers_admin,
    db,
    usuario_admin,
):
    curso = crear_curso(db, usuario_admin)
    crear_alumno(
        db,
        documento="INACTIVO-001",
        activo=False,
    )
    contenido = crear_csv(
        [["Alumno", "Inactivo", "INACTIVO-001", "12/04/2008"]]
    )

    respuesta = importar(
        client,
        auth_headers_admin,
        curso.id,
        contenido,
    )

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["alumnos_inscriptos"] == 0
    assert len(datos["errores"]) == 1
    assert datos["errores"][0]["fila"] == 2
    assert "desactivado" in datos["errores"][0]["mensaje"]
    assert db.query(Inscripcion).count() == 0


def test_importar_procesa_filas_validas_y_reporta_errores(
    client,
    auth_headers_admin,
    db,
    usuario_admin,
):
    curso = crear_curso(db, usuario_admin)
    contenido = crear_csv(
        [
            ["Valida", "Fila", "VALIDO-001", "12/04/2009"],
            ["", "Sin nombre", "ERROR-001", "12/04/2009"],
            ["Fecha", "Invalida", "ERROR-002", "31/02/2026"],
        ]
    )

    respuesta = importar(
        client,
        auth_headers_admin,
        curso.id,
        contenido,
    )

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["total_filas"] == 3
    assert datos["alumnos_creados"] == 1
    assert datos["alumnos_inscriptos"] == 1
    assert len(datos["errores"]) == 2
    assert [error["fila"] for error in datos["errores"]] == [3, 4]
    assert db.query(Alumno).filter_by(
        documento_identidad="VALIDO-001"
    ).count() == 1


def test_importar_xlsx(client, auth_headers_admin, db, usuario_admin):
    curso = crear_curso(db, usuario_admin)
    contenido = crear_xlsx(
        [["Ana", "Xlsx", "XLSX-001", date(2009, 4, 12)]]
    )

    respuesta = importar(
        client,
        auth_headers_admin,
        curso.id,
        contenido,
        nombre="alumnos.xlsx",
    )

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["alumnos_creados"] == 1
    assert datos["alumnos_inscriptos"] == 1
    assert datos["errores"] == []


def test_importar_falta_columna_obligatoria(
    client,
    auth_headers_admin,
    db,
    usuario_admin,
):
    curso = crear_curso(db, usuario_admin)
    contenido = crear_csv(
        [["Ana", "Gomez", "COL-001"]],
        encabezado=["nombre", "apellido", "documento"],
    )

    respuesta = importar(
        client,
        auth_headers_admin,
        curso.id,
        contenido,
    )

    assert respuesta.status_code == 400
    assert "fecha_nacimiento" in respuesta.json()["detail"]


def test_importar_curso_ajeno(client, auth_headers_admin, db):
    otro = crear_otro_docente(db)
    curso = crear_curso(db, otro)
    contenido = crear_csv(
        [["Ana", "Gomez", "AJENO-001", "12/04/2009"]]
    )

    respuesta = importar(
        client,
        auth_headers_admin,
        curso.id,
        contenido,
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Curso no encontrado"
    assert db.query(Alumno).count() == 0


def test_importar_curso_archivado(
    client,
    auth_headers_admin,
    db,
    usuario_admin,
):
    curso = crear_curso(db, usuario_admin, activo=False)
    contenido = crear_csv(
        [["Ana", "Gomez", "ARCHIVADO-001", "12/04/2009"]]
    )

    respuesta = importar(
        client,
        auth_headers_admin,
        curso.id,
        contenido,
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "El curso está inactivo"


def test_importar_rechaza_extension_no_permitida(
    client,
    auth_headers_admin,
    db,
    usuario_admin,
):
    curso = crear_curso(db, usuario_admin)

    respuesta = importar(
        client,
        auth_headers_admin,
        curso.id,
        b"contenido",
        nombre="alumnos.txt",
    )

    assert respuesta.status_code == 415


def test_importar_rechaza_archivo_demasiado_grande(
    client,
    auth_headers_admin,
    db,
    usuario_admin,
):
    curso = crear_curso(db, usuario_admin)

    respuesta = importar(
        client,
        auth_headers_admin,
        curso.id,
        b"a" * (MAX_BYTES + 1),
    )

    assert respuesta.status_code == 413


def test_importar_rechaza_mas_de_500_filas(
    client,
    auth_headers_admin,
    db,
    usuario_admin,
):
    curso = crear_curso(db, usuario_admin)
    filas = [
        [
            f"Alumno {indice}",
            "Masivo",
            f"M-{indice:04d}",
            "12/04/2009",
        ]
        for indice in range(501)
    ]
    contenido = crear_csv(filas)

    respuesta = importar(
        client,
        auth_headers_admin,
        curso.id,
        contenido,
    )

    assert respuesta.status_code == 400
    assert "500" in respuesta.json()["detail"]


def test_alumno_no_puede_importar(
    client,
    auth_headers_alumno,
    db,
    usuario_admin,
):
    curso = crear_curso(db, usuario_admin)
    contenido = crear_csv(
        [["Ana", "Gomez", "PERMISO-001", "12/04/2009"]]
    )

    respuesta = importar(
        client,
        auth_headers_alumno,
        curso.id,
        contenido,
    )

    assert respuesta.status_code == 403
