# 🏫 School API

REST API desarrollada con **FastAPI** para gestionar alumnos, materias y calificaciones.

El proyecto fue desarrollado como práctica de backend, aplicando una arquitectura por capas, validaciones, relaciones entre entidades, manejo de errores, migraciones con Alembic y testing automatizado.

## 🚀 Tecnologías

- **Python 3.12**
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy**
- **Pydantic**
- **Alembic**
- **psycopg**
- **Pytest**
- **Uvicorn**

## 📋 Funcionalidades

### 👨‍🎓 Alumnos

- Crear alumnos
- Obtener todos los alumnos
- Buscar un alumno por ID
- Actualizar completamente un alumno mediante `PUT`
- Actualizar parcialmente un alumno mediante `PATCH`
- Eliminar alumnos
- Obtener un alumno junto con sus calificaciones
- Calcular el promedio de un alumno
- Obtener estadísticas de sus calificaciones

### 📚 Materias

- Crear materias
- Obtener todas las materias
- Buscar una materia por ID
- Actualizar completamente una materia
- Actualizar parcialmente una materia
- Eliminar materias
- Validación de nombres duplicados

### 📝 Calificaciones

- Crear calificaciones
- Obtener todas las calificaciones
- Buscar una calificación por ID
- Actualizar calificaciones mediante `PATCH`
- Eliminar calificaciones
- Consultar calificaciones de un alumno
- Filtrar calificaciones por período
- Obtener calificaciones mediante consultas con relaciones (`JOIN`)
- Obtener promedio de un alumno
- Obtener estadísticas:
  - Cantidad de calificaciones
  - Promedio
  - Nota máxima
  - Nota mínima

## 🏗️ Arquitectura

El proyecto utiliza una separación por responsabilidades:

```text
school-api/
│
├── alembic/
│   └── versions/
│
├── app/
│   └── main.py
│
├── database/
│   ├── connection.py
│   └── dependencies.py
│
├── models/
│   ├── alumno.py
│   ├── materia.py
│   └── calificacion.py
│
├── routers/
│   ├── alumno.py
│   ├── materia.py
│   └── calificacion.py
│
├── schemas/
│   ├── alumno.py
│   ├── materia.py
│   └── calificacion.py
│
├── services/
│   ├── alumno_service.py
│   ├── materia_service.py
│   └── calificacion_service.py
│
├── tests/
│   ├── conftest.py
│   ├── test_alumno.py
│   ├── test_materia.py
│   ├── test_calificacion.py
│   └── test_rollback.py
│
├── .gitignore
├── alembic.ini
└── README.md
```

### Separación de responsabilidades

**Routers**

Se encargan de recibir las solicitudes HTTP, validar parámetros y devolver las respuestas correspondientes.

**Services**

Contienen la lógica de negocio y las operaciones con la base de datos.

**Schemas**

Definen la validación y estructura de los datos mediante Pydantic.

**Models**

Representan las tablas y relaciones de PostgreSQL mediante SQLAlchemy.

**Database**

Contiene la configuración de SQLAlchemy y la dependencia utilizada para administrar las sesiones de base de datos.

## 🗄️ Modelo de datos

La API utiliza tres entidades principales:

```text
Alumno
   │
   │ 1:N
   ▼
Calificacion
   ▲
   │ N:1
   │
Materia
```

Una `Calificacion` pertenece a un `Alumno` y a una `Materia`.

Cada calificación contiene:

- `alumno_id`
- `materia_id`
- `nota`
- `periodo`

### Restricciones de base de datos

Además de las validaciones realizadas mediante Pydantic, PostgreSQL cuenta con restricciones `CHECK`:

```text
edad > 0 AND edad < 100

nota >= 1 AND nota <= 10

periodo >= 1 AND periodo <= 3
```

Las relaciones entre las tablas utilizan claves foráneas.

## 🔄 Migraciones con Alembic

El proyecto utiliza **Alembic** para controlar los cambios del esquema de la base de datos.

Migraciones incluidas:

```text
605e5c5357a5
Agregar periodo a calificaciones

        ↓

b8253f2d882e
Agregar checks a calificaciones

        ↓

ffdba5543a54
Agregar check de edad a alumnos
```

Para ejecutar las migraciones:

```bash
alembic upgrade head
```

Para comprobar la versión actual:

```bash
alembic current
```

## 🔐 Variables de entorno

La conexión a PostgreSQL se configura mediante una variable de entorno:

```env
DATABASE_URL=postgresql+psycopg://usuario:contraseña@localhost:5432/school_db
```

El archivo `.env` **no está incluido en el repositorio**.

Cada desarrollador debe crear su propio archivo `.env` localmente.

## ⚙️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/lllkevdev/School-Api.git
```

Entrar al proyecto:

```bash
cd School-Api
```

### 2. Crear el entorno virtual

Windows:

```bash
python -m venv .venv
```

Activarlo:

```bash
.venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install fastapi uvicorn sqlalchemy psycopg[binary] pydantic alembic python-dotenv pytest httpx
```

### 4. Configurar PostgreSQL

Crear una base de datos llamada:

```text
school_db
```

Después crear el archivo `.env`:

```env
DATABASE_URL=postgresql+psycopg://usuario:contraseña@localhost:5432/school_db
```

### 5. Ejecutar las migraciones

```bash
alembic upgrade head
```

## ▶️ Ejecutar la API

Desde la raíz del proyecto:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en:

```text
http://127.0.0.1:8000
```

## 📖 Documentación

FastAPI genera automáticamente la documentación interactiva.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

Desde Swagger se pueden probar los endpoints directamente.

## 🛣️ Principales endpoints

### Alumnos

```text
GET    /alumnos/
POST   /alumnos/
GET    /alumnos/{alumno_id}
PUT    /alumnos/{alumno_id}
PATCH  /alumnos/{alumno_id}
DELETE /alumnos/{alumno_id}
```

### Materias

```text
GET    /materias/
POST   /materias/
GET    /materias/{materia_id}
PUT    /materias/{materia_id}
PATCH  /materias/{materia_id}
DELETE /materias/{materia_id}
```

### Calificaciones

```text
GET    /calificaciones/
POST   /calificaciones/
GET    /calificaciones/detalle
GET    /calificaciones/{calificacion_id}
PATCH  /calificaciones/{calificacion_id}
DELETE /calificaciones/{calificacion_id}
```

Consultas relacionadas con alumnos:

```text
GET /calificaciones/alumno/{alumno_id}
GET /calificaciones/alumno/{alumno_id}/join
GET /calificaciones/alumno/{alumno_id}/promedio
GET /calificaciones/alumno/{alumno_id}/estadisticas
```

También es posible filtrar determinadas consultas por período:

```text
GET /calificaciones/alumno/{alumno_id}?periodo=1
```

## 🧪 Testing

El proyecto cuenta con tests automatizados utilizando **Pytest**.

Los tests cubren funcionalidades de:

- Alumnos
- Materias
- Calificaciones
- Validaciones
- Errores HTTP
- Relaciones entre entidades
- Actualizaciones `PUT` y `PATCH`
- Eliminaciones
- Consultas y estadísticas
- Manejo de errores de integridad
- Rollback de transacciones

Ejecutar todos los tests:

```bash
python -m pytest
```

Estado actual:

```text
65 tests passed
```

## 🛡️ Manejo de errores

La API implementa diferentes respuestas HTTP según el problema:

```text
400 Bad Request
404 Not Found
409 Conflict
422 Unprocessable Entity
500 Internal Server Error
```

Ejemplos:

- Alumno inexistente → `404`
- Materia inexistente → `404`
- Calificación inexistente → `404`
- Materia duplicada → `409`
- Datos inválidos → `422`
- Error inesperado del servidor → `500`

También se realiza `rollback` de la sesión cuando ocurre un error de integridad en la base de datos.

## 🧠 Conceptos aplicados

Durante el desarrollo se trabajaron conceptos fundamentales de backend:

- Arquitectura por capas
- APIs REST
- CRUD
- HTTP methods
- HTTP status codes
- Dependency Injection
- ORM
- SQLAlchemy
- Relaciones entre tablas
- Foreign Keys
- Constraints
- PostgreSQL
- Pydantic
- Validación de datos
- Manejo de excepciones
- Transacciones
- Rollback
- Consultas con filtros
- JOINs
- Agregaciones
- Migraciones
- Alembic
- Testing
- Git
- GitHub

## 📌 Estado del proyecto

### Backend

🟢 Completado

### Frontend

🔜 Próximamente

El siguiente objetivo es desarrollar una interfaz web que consuma esta API y permita gestionar alumnos, materias y calificaciones desde el navegador.

## 🎯 Objetivo del proyecto

Este proyecto forma parte de mi aprendizaje y portfolio como desarrollador de software, con foco en **backend y desarrollo de APIs REST**.

El objetivo principal fue construir una API desde cero y aplicar buenas prácticas de organización, validación, persistencia de datos, testing y control de versiones.

## 👨‍💻 Autor

**Kevin Baez**

GitHub: [@lllkevdev](https://github.com/lllkevdev)
