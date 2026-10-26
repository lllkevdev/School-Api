# School API

API REST desarrollada con FastAPI para gestionar cursos, alumnos, inscripciones, evaluaciones, calificaciones, invitaciones y perfiles.

El proyecto aplica una arquitectura por capas, autenticación con JWT, autorización por roles, validación con Pydantic, persistencia con SQLAlchemy, migraciones con Alembic y testing automatizado con Pytest.

## Stack

- Python 3.12
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- psycopg
- Alembic
- PyJWT
- Argon2
- Pillow
- openpyxl
- Pytest
- Uvicorn

## Funcionalidades

### Autenticación y usuarios

- Registro público de docentes.
- Inicio de sesión con JWT.
- Consulta del usuario autenticado.
- Roles `admin` y `alumno`.
- Permisos por rol y por alcance del curso.
- Vinculación de alumnos mediante invitaciones.

### Cursos

- Crear, listar, consultar y actualizar cursos.
- Archivar y reactivar cursos.
- Eliminar cursos de forma segura.
- Aislamiento de cursos por docente.
- El alumno puede consultar sus propios cursos.

Un curso archivado queda fuera de las consultas del alumno y no permite nuevas inscripciones, evaluaciones ni calificaciones. El docente puede reactivarlo.

La eliminación se bloquea si el curso tiene inscripciones, evaluaciones o invitaciones asociadas.

### Alumnos

- Listar y consultar alumnos dentro del alcance del docente.
- Registrar un alumno e inscribirlo en un curso en una sola operación.
- Confirmar la reutilización de un perfil existente antes de inscribirlo.
- Importar alumnos desde CSV o XLSX.
- Desactivar alumnos.
- Consultar el perfil académico del alumno autenticado.

La importación admite archivos de hasta 5 MB y 500 filas. Informa errores por fila, reutiliza perfiles existentes sin modificarlos y omite alumnos ya inscriptos.

Un alumno compartido con cursos de otro docente no puede desactivarse globalmente; primero debe quitarse la inscripción del curso correspondiente.

### Inscripciones

- Inscribir alumnos en cursos.
- Listar inscripciones por curso.
- Consultar las inscripciones del alumno autenticado.
- Quitar inscripciones.
- Evitar inscripciones duplicadas.

### Evaluaciones

- Crear, listar, consultar, actualizar y eliminar evaluaciones.
- Listar evaluaciones por curso.
- Consultar las evaluaciones del alumno autenticado.
- Validar el período según la configuración del curso.

### Calificaciones

- Registrar, consultar, actualizar y eliminar calificaciones.
- Validar que el alumno esté inscripto en el curso.
- Evitar calificaciones duplicadas para el mismo alumno y evaluación.
- Consultar promedio por curso y promedio general del alumno.
- Consultar historial académico.
- Exportar las calificaciones de un curso a CSV.
- Aplicar el alcance correspondiente al docente o al alumno autenticado.

### Invitaciones

- Crear invitaciones para alumnos.
- Listar y revocar invitaciones.
- Aceptar una invitación y obtener un token de acceso.
- Controlar vencimiento, uso y revocación.

### Perfil

- Consultar y actualizar el perfil propio.
- Subir, obtener y eliminar foto de perfil.
- Validar tamaño y formato de la imagen.

## Roles y autorización

### Admin / docente

Puede gestionar sus cursos y todo el contenido académico asociado:

- Alumnos e inscripciones.
- Evaluaciones y calificaciones.
- Invitaciones.
- Exportaciones.
- Su propio perfil.

Las operaciones sobre cursos y alumnos respetan la propiedad del docente.

### Alumno

Puede consultar:

- Sus cursos e inscripciones.
- Sus evaluaciones.
- Sus calificaciones, promedio e historial.
- Su perfil académico.

También puede actualizar sus datos personales y su foto de perfil.

## Arquitectura

```text
school-api/
├── alembic/
│   └── versions/
├── app/
│   └── main.py
├── core/
│   ├── config.py
│   ├── dependencies.py
│   ├── errores.py
│   ├── permisos.py
│   └── security.py
├── database/
│   ├── connection.py
│   └── dependencies.py
├── models/
│   ├── alumno.py
│   ├── calificacion.py
│   ├── curso.py
│   ├── evaluacion.py
│   ├── inscripcion.py
│   ├── invitacion.py
│   └── usuario.py
├── routers/
│   ├── alumno.py
│   ├── auth.py
│   ├── calificacion.py
│   ├── curso.py
│   ├── evaluacion.py
│   ├── inscripcion.py
│   ├── invitacion.py
│   └── perfil.py
├── schemas/
├── services/
├── tests/
├── alembic.ini
├── requirements.txt
└── README.md
```

### Separación de responsabilidades

- **Routers:** reciben solicitudes, resuelven dependencias, verifican permisos y devuelven respuestas HTTP.
- **Services:** contienen la lógica de negocio y las operaciones de persistencia.
- **Schemas:** definen contratos de entrada y salida, normalización y validaciones con Pydantic.
- **Models:** representan tablas y relaciones con SQLAlchemy.
- **Core:** configuración, seguridad, dependencias, permisos y conversión centralizada de errores.
- **Database:** configuración del engine y de las sesiones.

## Modelo de datos

```text
Usuario ──> Alumno
Curso ──> Inscripción <── Alumno
Curso ──> Evaluación ──> Calificación <── Alumno
Curso ──> Invitación
```

Reglas principales:

- Un curso pertenece a un docente.
- Un alumno no puede estar inscripto dos veces en el mismo curso.
- Una calificación requiere una inscripción previa y es única por alumno y evaluación.
- Las notas deben estar entre 1 y 10.
- La cantidad de períodos de un curso debe estar entre 1 y 12.

## Variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=postgresql+psycopg://usuario:contraseña@localhost:5432/school_db
SECRET_KEY=una_clave_larga_y_segura
ACCES_TOKEN_EXPIRES_MINUTES=30
MEDIA_ROOT=media
MAX_FOTO_BYTES=2097152
FOTO_MAX_DIMENSION=1024
FOTO_MAX_PIXELES=25000000
```

`DATABASE_URL` y `SECRET_KEY` son obligatorias. Las demás variables tienen valores por defecto.

## Instalación

Crear y activar el entorno virtual en Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

Configurar PostgreSQL y el archivo `.env`.

Aplicar las migraciones:

```powershell
alembic upgrade head
```

## Ejecutar la API

```powershell
uvicorn app.main:app --reload
```

La API queda disponible en:

```text
http://127.0.0.1:8000
```

Documentación interactiva:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
```

CORS está habilitado para el frontend en `http://localhost:5173`.

## Testing

La suite usa Pytest y, por defecto, una base SQLite local para poder ejecutarse sin un PostgreSQL preconfigurado.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Para usar otra base de tests:

```powershell
$env:TEST_DATABASE_URL="postgresql+psycopg://usuario:contraseña@localhost:5432/school_test_db"
.\.venv\Scripts\python.exe -m pytest -q
```

Los tests cubren autenticación, permisos, cursos, alumnos, importaciones, inscripciones, evaluaciones, calificaciones, invitaciones, perfiles y manejo de errores.

## Endpoints principales

### Autenticación

```text
GET  /auth/me
POST /auth/login
POST /auth/registro
```

### Alumnos

```text
GET   /alumnos/
GET   /alumnos/me
GET   /alumnos/{alumno_id}
POST  /alumnos/con-inscripcion
POST  /alumnos/importar
PATCH /alumnos/{alumno_id}/desactivar
```

`POST /alumnos/importar` recibe `multipart/form-data` con los campos `curso_id` y `archivo`.

### Cursos

```text
GET    /cursos/
GET    /cursos/mis-cursos
GET    /cursos/{curso_id}
POST   /cursos/
PATCH  /cursos/{curso_id}
PUT    /cursos/{curso_id}
PATCH  /cursos/{curso_id}/archivar
PATCH  /cursos/{curso_id}/reactivar
DELETE /cursos/{curso_id}
```

### Inscripciones

```text
GET    /inscripciones/mis-inscripciones
GET    /inscripciones/curso/{curso_id}
POST   /inscripciones/
DELETE /inscripciones/{inscripcion_id}
```

### Evaluaciones

```text
GET    /evaluaciones/curso/{curso_id}
GET    /evaluaciones/mis-evaluaciones
GET    /evaluaciones/{evaluacion_id}
POST   /evaluaciones/
PATCH  /evaluaciones/{evaluacion_id}
PUT    /evaluaciones/{evaluacion_id}
DELETE /evaluaciones/{evaluacion_id}
```

### Calificaciones

```text
GET    /calificaciones/curso/{curso_id}
GET    /calificaciones/curso/{curso_id}/promedio
GET    /calificaciones/curso/{curso_id}/export
GET    /calificaciones/mis-calificaciones
GET    /calificaciones/mi-promedio
GET    /calificaciones/mi-historial
POST   /calificaciones/
PATCH  /calificaciones/{calificacion_id}
DELETE /calificaciones/{calificacion_id}
```

### Invitaciones

```text
GET  /invitaciones/
POST /invitaciones/
POST /invitaciones/{invitacion_id}/revocar
POST /invitaciones/aceptar
```

### Perfil

```text
GET    /perfil/me
PATCH  /perfil/me
GET    /perfil/me/foto
POST   /perfil/me/foto
DELETE /perfil/me/foto
```

## Manejo de errores

La API utiliza respuestas HTTP consistentes:

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
410 Gone
413 Payload Too Large
415 Unsupported Media Type
422 Unprocessable Entity
500 Internal Server Error
```

Los errores de negocio se centralizan en `core/errores.py`. Los conflictos de integridad de base de datos provocan `rollback` para mantener la sesión utilizable.

## Frontend

El frontend se encuentra en un repositorio separado:

```text
https://github.com/lllkevdev/School-Frontend
```

Consumir esta API configurando `VITE_API_URL` en el archivo `.env` del frontend.

## Autor

Kevin Baez

GitHub: [@lllkevdev](https://github.com/lllkevdev)
