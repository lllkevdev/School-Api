# 🏫 School API

REST API desarrollada con **FastAPI** para gestionar alumnos, materias, inscripciones y calificaciones.

El proyecto fue desarrollado como práctica de backend y portfolio, aplicando una arquitectura por capas, validación de datos, relaciones entre entidades, autorización basada en roles, manejo de errores, migraciones con Alembic, PostgreSQL y testing automatizado.

---

## 🚀 Tecnologías

- **Python 3.12**
- **FastAPI**
- **SQLAlchemy**
- **Pydantic**
- **PostgreSQL**
- **psycopg**
- **Alembic**
- **Pytest**
- **Uvicorn**
- **HTTPX**

---

## 📋 Funcionalidades

### 👨‍🎓 Alumnos

- Crear alumnos
- Obtener alumnos
- Buscar alumnos por ID
- Actualizar alumnos mediante `PUT`
- Actualizar parcialmente alumnos mediante `PATCH`
- Eliminar alumnos
- Validación de datos
- Protección de operaciones mediante permisos

### 📚 Materias

- Crear materias
- Obtener materias
- Buscar materias por ID
- Actualizar materias mediante `PUT`
- Actualizar parcialmente materias mediante `PATCH`
- Eliminar materias
- Validación de nombres duplicados
- Asignación de maestro a una materia
- Protección de operaciones mediante permisos

### 👤 Usuarios y roles

La API incorpora un sistema de usuarios con diferentes roles:

- `ADMIN`
- `MAESTRO`
- `ALUMNO`

Los usuarios pueden asociarse a un alumno y las operaciones disponibles dependen de los permisos correspondientes a cada rol.

Las contraseñas no se almacenan en texto plano: se almacenan mediante hashing.

### 📝 Inscripciones

Los alumnos pueden estar inscriptos en materias.

La API controla:

- Creación de inscripciones
- Eliminación de inscripciones
- Existencia del alumno
- Existencia de la materia
- Inscripciones duplicadas
- Permisos para gestionar inscripciones

Existe una restricción que impide que un alumno sea inscripto más de una vez en la misma materia.

Además, las inscripciones están relacionadas con las calificaciones: al eliminar una inscripción, sus calificaciones asociadas también son eliminadas mediante `cascade`.

### 📊 Calificaciones

- Crear calificaciones
- Consultar calificaciones
- Buscar una calificación por ID
- Actualizar calificaciones mediante `PATCH`
- Eliminar calificaciones
- Consultar calificaciones de un alumno
- Consultar promedio
- Consultar estadísticas
- Validar períodos
- Validar rango de notas
- Evitar calificaciones duplicadas para el mismo alumno, materia y período
- Verificar la inscripción del alumno en la materia

Las operaciones sobre calificaciones respetan el alcance correspondiente a cada rol.

---

## 🔐 Roles y autorización

La API utiliza autorización basada en roles y permisos.

### ADMIN

Tiene acceso a las operaciones administrativas del sistema, incluyendo la gestión de:

- Alumnos
- Materias
- Inscripciones
- Calificaciones
- Usuarios

### MAESTRO

Puede gestionar y consultar calificaciones dentro del alcance de las materias que tiene asignadas.

También puede consultar información académica correspondiente a ese alcance.

### ALUMNO

Puede consultar sus propias calificaciones, promedio y estadísticas.

El acceso a las calificaciones de otros alumnos está restringido.

---

## 🏗️ Arquitectura

El proyecto utiliza una arquitectura por capas para separar responsabilidades:

```text
school-api/
│
├── alembic/
│   └── versions/
│
├── app/
│   └── main.py
│
├── core/
│   ├── dependencies.py
│   ├── errores.py
│   └── permisos.py
│
├── database/
│   ├── connection.py
│   └── dependencies.py
│
├── models/
│   ├── alumno.py
│   ├── materia.py
│   ├── calificacion.py
│   ├── inscripcion.py
│   └── usuario.py
│
├── routers/
│   ├── alumno.py
│   ├── materia.py
│   ├── calificacion.py
│   ├── inscripcion.py
│   └── usuario.py
│
├── schemas/
│   ├── alumno.py
│   ├── materia.py
│   ├── calificacion.py
│   ├── inscripcion.py
│   ├── usuario.py
│   └── roles.py
│
├── security/
│   └── password.py
│
├── services/
│   ├── alumno_service.py
│   ├── materia_service.py
│   ├── calificacion_service.py
│   ├── inscripcion_service.py
│   └── usuario_service.py
│
├── tests/
│   ├── conftest.py
│   ├── test_alumno.py
│   ├── test_materia.py
│   ├── test_calificacion.py
│   ├── test_inscripcion.py
│   ├── test_usuario.py
│   └── test_rollback.py
│
├── .gitignore
├── alembic.ini
└── README.md
```

### Separación de responsabilidades

**Routers**

Se encargan de recibir las solicitudes HTTP, gestionar dependencias, permisos y devolver las respuestas correspondientes.

**Services**

Contienen la lógica de negocio y las operaciones relacionadas con la persistencia de datos.

**Schemas**

Definen la estructura y validación de los datos mediante Pydantic.

**Models**

Representan las entidades, tablas y relaciones de la base de datos mediante SQLAlchemy.

**Core**

Contiene componentes centrales de la aplicación:

- dependencies.py: dependencias utilizadas por los endpoints y obtención del usuario actual.

- permisos.py: definición y control de permisos de acceso según el rol.

- errores.py: manejo y conversión centralizada de errores de negocio a respuestas HTTP.

**Security**

Contiene componentes relacionados con seguridad, como el hashing y verificación de contraseñas.

**Database**

Contiene la configuración de SQLAlchemy y la gestión de sesiones de base de datos.

---

## 🗄️ Modelo de datos

Las principales entidades del sistema son:

```text
                    ┌──────────────┐
                    │    Usuario   │
                    └──────┬───────┘
                           │
                           │ alumno_id
                           ▼
                    ┌──────────────┐
                    │    Alumno    │
                    └──────┬───────┘
                           │
                           │
                    ┌──────▼───────┐
                    │ Inscripción  │
                    └──────┬───────┘
                           │
                           │
                    ┌──────▼───────┐
                    │    Materia   │
                    └──────┬───────┘
                           │
                           │
                    ┌──────▼───────┐
                    │ Calificación │
                    └──────────────┘
```

Una **inscripción** relaciona un alumno con una materia.

Una **calificación** pertenece a un alumno y a una materia, y requiere que exista la correspondiente inscripción.

Una materia puede tener un maestro asignado.

Un usuario con rol `ALUMNO` puede estar asociado a un único alumno.

---

## 📌 Reglas de integridad

La API utiliza validaciones de aplicación y restricciones de base de datos.

### Alumno

```text
edad > 0
edad < 100
```

### Calificación

```text
nota >= 1
nota <= 10

periodo >= 1
periodo <= 3
```

### Inscripciones

La combinación:

```text
alumno_id + materia_id
```

debe ser única.

### Calificaciones

La combinación:

```text
alumno_id + materia_id + periodo
```

debe ser única.

Estas restricciones ayudan a garantizar la integridad de los datos incluso cuando las operaciones llegan directamente a la base de datos.

---

## 🔄 Migraciones con Alembic

El proyecto utiliza **Alembic** para gestionar la evolución del esquema de PostgreSQL.

Para ejecutar todas las migraciones:

```bash
alembic upgrade head
```

Para consultar la versión actual:

```bash
alembic current
```

Para revisar el historial:

```bash
alembic history
```

Las migraciones permiten modificar el esquema de la base de datos de forma controlada sin tener que recrear manualmente las tablas.

---

## 🔐 Variables de entorno

La conexión a PostgreSQL se configura mediante una variable de entorno:

```env
DATABASE_URL=postgresql+psycopg://usuario:contraseña@localhost:5432/school_db
```

El archivo `.env` no está incluido en el repositorio.

Cada entorno debe configurar sus propias credenciales de base de datos.

---

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

En Windows:

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

---

## ▶️ Ejecutar la API

Desde la raíz del proyecto:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en:

```text
http://127.0.0.1:8000
```

---

## 📖 Documentación

FastAPI genera automáticamente documentación interactiva.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

Swagger permite consultar y probar los endpoints directamente desde el navegador.

---

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

### Inscripciones

```text
POST   /inscripciones/
DELETE /inscripciones/{inscripcion_id}
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
GET /calificaciones/alumno/{alumno_id}/promedio
GET /calificaciones/alumno/{alumno_id}/estadisticas
```

Endpoints destinados al propio alumno:

```text
GET /calificaciones/alumno/mis-calificaciones
GET /calificaciones/alumno/mi-promedio
GET /calificaciones/alumno/mi-estadisticas
```

Los endpoints disponibles y sus permisos pueden consultarse con mayor detalle en Swagger.

---

## 🧪 Testing

El proyecto cuenta con una suite de tests automatizados utilizando **Pytest**.

Los tests cubren:

- Alumnos
- Materias
- Usuarios
- Inscripciones
- Calificaciones
- Roles y permisos
- Validaciones
- Errores HTTP
- Relaciones entre entidades
- Operaciones `PUT` y `PATCH`
- Eliminaciones
- Inscripciones duplicadas
- Calificaciones duplicadas
- Reglas de acceso por usuario
- Integridad referencial
- Cascades
- Manejo de errores de integridad
- Rollback de transacciones

Para ejecutar toda la suite:

```bash
python -m pytest
```

### Estado actual

```text
Suite completa: todos los tests pasan correctamente
```

---

## 🛡️ Manejo de errores

La API utiliza diferentes códigos HTTP según el tipo de operación o error:

```text
400 Bad Request
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Entity
500 Internal Server Error
```

Ejemplos:

```text
Alumno inexistente              → 404
Materia inexistente             → 404
Calificación inexistente        → 404
Inscripción inexistente         → 404
Operación sin permiso           → 403
Materia duplicada               → 409
Inscripción duplicada           → 409
Calificación duplicada          → 409
Datos inválidos                 → 422
```

Los errores de integridad de base de datos también provocan un `rollback` de la sesión para mantenerla en un estado utilizable.

---

## 🧠 Conceptos aplicados

Durante el desarrollo del proyecto se trabajaron conceptos fundamentales de backend:

- Python
- FastAPI
- APIs REST
- CRUD
- HTTP methods
- HTTP status codes
- Dependency Injection
- Arquitectura por capas
- ORM
- SQLAlchemy
- PostgreSQL
- Pydantic
- Foreign Keys
- Relaciones entre tablas
- Constraints
- Validación de datos
- Roles y permisos
- Autorización
- Hashing de contraseñas
- Manejo de excepciones
- Transacciones
- Rollback
- Consultas con filtros
- JOINs
- Agregaciones
- Migraciones
- Alembic
- Testing
- Pytest
- Git
- GitHub

---

## 📌 Estado del proyecto

### Backend

🟢 **Completado**

La API cuenta actualmente con:

- CRUD de alumnos
- CRUD de materias
- Gestión de usuarios
- Roles y permisos
- Gestión de inscripciones
- Gestión de calificaciones
- Validaciones
- Reglas de integridad
- Migraciones
- Manejo de errores
- Tests automatizados

### Frontend

🔜 **Próximamente**

El siguiente objetivo del proyecto es desarrollar una interfaz web que consuma la API y permita gestionar la información desde el navegador.

---

## 🎯 Objetivo del proyecto

Este proyecto forma parte de mi aprendizaje y portfolio como desarrollador de software, con foco en **backend y desarrollo de APIs REST**.

El objetivo fue construir una API desde cero y aplicar buenas prácticas de desarrollo relacionadas con:

- organización del código
- arquitectura
- persistencia de datos
- validación
- autorización
- manejo de errores
- testing
- migraciones
- control de versiones

El proyecto representa una etapa práctica de mi formación como desarrollador backend.

---

## 👨‍💻 Autor

**Kevin Baez**

GitHub: **@lllkevdev**
