# School API
## ADR-001 — Redefinición del producto y arquitectura

**Estado:** Diseño acordado; pendiente de implementación  
**Versión:** 1.0  
**Fecha:** 17 de octubre de 2026

---

## 1. Objetivo del proyecto

School API será una plataforma para que docentes gestionen sus cursos, alumnos, evaluaciones y calificaciones desde un único lugar.

El sistema permitirá que cada docente administre sus propios cursos y que los alumnos accedan mediante una cuenta personal para consultar su información académica.

El objetivo es simplificar la gestión educativa, reducir la dependencia de planillas dispersas y mantener la información organizada y protegida.

## 2. Alcance del MVP

### Funcionalidades incluidas

- Autenticación mediante JWT.
- Cuentas para docentes y alumnos.
- Creación, edición y archivo de cursos.
- Registro manual e importación de alumnos desde planillas.
- Inscripción de alumnos en cursos.
- Invitaciones para activar cuentas de alumnos.
- Creación de evaluaciones y registro de calificaciones.
- Cálculo de promedios e historial de notas.
- Consulta de información académica según el rol.
- Exportación de información a CSV.

### Funcionalidades fuera del alcance inicial

- Administración global de múltiples docentes.
- Gestión de instituciones educativas como entidades independientes.
- Asistencia y calendario escolar.
- Notificaciones académicas avanzadas.
- Informes estadísticos complejos.
- Configuración de escalas de calificación por curso.

Estas funcionalidades podrán evaluarse en futuras versiones.

## 3. Roles y usuarios

### Docente — `ADMIN`

El rol `ADMIN` representará al docente propietario de sus cursos. No existirá un administrador global en el MVP.

Sus responsabilidades serán:

- Crear y administrar sus cursos.
- Registrar e inscribir alumnos.
- Invitar a los alumnos a activar sus cuentas.
- Crear evaluaciones y registrar calificaciones.
- Consultar promedios e historiales de sus cursos.

El docente solo podrá acceder a los cursos de los que sea propietario.

### Alumno — `ALUMNO`

El alumno tendrá una cuenta propia, vinculada a su perfil académico.

Podrá:

- Iniciar sesión.
- Consultar sus cursos.
- Consultar sus evaluaciones y calificaciones.
- Consultar su historial académico.

No podrá modificar sus calificaciones ni consultar información privada de otros alumnos.

### Rol `MAESTRO`

El rol actual `MAESTRO` será revisado y retirado gradualmente si deja de ser necesario. No se eliminará hasta comprobar sus dependencias en los servicios, permisos, esquemas y pruebas automatizadas.

## 4. Modelo de datos propuesto

### Usuario

Representa una cuenta de acceso.

Campos principales existentes:

- `id`
- `nombre`
- `apellido`
- `email`
- `telefono`
- `password_hash`
- `rol`
- `activo`
- `created_at`
- `alumno_id`, opcional y único

Se conservará la autenticación existente y se adaptará el proceso de creación de cuentas.

### Alumno

Representa el perfil académico reutilizable del estudiante.

Campos actuales:

- `id`
- `nombre`
- `apellido`
- `edad`

Un mismo perfil podrá participar en varios cursos. Su cuenta de usuario se vinculará mediante `Usuario.alumno_id`.

### Curso

Nueva entidad que representará el grupo académico administrado por un docente.

Campos propuestos:

- `id`
- `docente_id`
- `nombre_materia`
- `division`
- `anio_lectivo`
- `activo`

Ejemplo: Matemática — 2.º A — 2026.

La materia, la división y el año lectivo se representarán directamente en el curso durante el MVP. No se mantendrá `Materia` como entidad independiente en el nuevo flujo inicial.

### Inscripcion

Relacionará alumnos con cursos.

Campos propuestos:

- `id`
- `alumno_id`
- `curso_id`

Regla de integridad: un alumno no podrá tener más de una inscripción al mismo curso.

### Evaluacion

Representará un examen, trabajo práctico u otra instancia evaluativa.

Campos propuestos:

- `id`
- `curso_id`
- `titulo`
- `fecha`
- `periodo`

Se conservarán los tres períodos académicos existentes.

### Calificacion

Representará la nota de un alumno en una evaluación específica.

Campos propuestos:

- `id`
- `evaluacion_id`
- `alumno_id`
- `nota`

Reglas:

- La nota deberá estar entre 1 y 10.
- Solo podrá existir una calificación por alumno y evaluación.
- El alumno deberá estar inscripto en el curso al que pertenece la evaluación.

### Invitacion

Entidad nueva para gestionar la activación de cuentas.

Campos propuestos:

- `id`
- `alumno_id`
- `token_hash`
- `expira_at`
- `usada_at`

El proceso deberá asociar la invitación al destinatario correcto, utilizar tokens seguros y de un solo uso, y verificar su vencimiento.

## 5. Arquitectura técnica

Se conservará la arquitectura por capas existente.

**Frontend:** React y Vite.

Responsabilidades: interfaz de usuario, formularios, panel del docente, panel del alumno y consumo de la API.

**API:** FastAPI.

Responsabilidades: endpoints, autenticación, validaciones de entrada y respuestas HTTP.

**Servicios y permisos:** lógica de negocio, comprobaciones de propiedad y reglas académicas.

**Persistencia:** SQLAlchemy y PostgreSQL.

Responsabilidades: modelos, relaciones, claves foráneas, restricciones e integridad de los datos.

**Migraciones y pruebas:** Alembic y pytest.

Responsabilidades: evolución controlada del esquema y validación automatizada de los comportamientos existentes y nuevos.

## 6. Seguridad y reglas de negocio

1. Cada curso tendrá un docente propietario.
2. Un docente solo podrá gestionar sus propios cursos.
3. El rol no será suficiente para autorizar una operación: también se verificará la propiedad del recurso.
4. Un alumno solo podrá consultar su propia información académica.
5. Los alumnos no podrán modificar sus calificaciones.
6. Las notas deberán cumplir la escala de 1 a 10.
7. Se mantendrán los tres períodos académicos.
8. Las inscripciones duplicadas estarán prohibidas mediante una restricción de base de datos.
9. Las calificaciones deberán corresponder a alumnos inscriptos en el curso de la evaluación.
10. Las invitaciones vencidas o utilizadas no podrán volver a activarse.
11. Archivar un curso no eliminará su historial académico.
12. Las contraseñas se almacenarán como hashes seguros, nunca en texto plano.

Las reglas críticas deberán comprobarse en los servicios y reforzarse mediante restricciones de base de datos cuando corresponda.

## 7. Estrategia de migración

Las modificaciones se realizarán en etapas, sin eliminar prematuramente tablas ni relaciones.

### Fase 0 — Auditoría

- Revisar modelos, servicios, routers, esquemas y permisos.
- Inspeccionar las migraciones de Alembic.
- Identificar datos existentes y preparar un respaldo.
- Revisar todos los tests afectados.

### Fase 1 — Cursos

- Crear el modelo y la tabla `Curso`.
- Definir el propietario y sus restricciones.
- Implementar y probar el CRUD de cursos.

### Fase 2 — Inscripciones

- Incorporar `curso_id`.
- Migrar las relaciones existentes cuando corresponda.
- Validar las restricciones de duplicados.
- Retirar la dependencia anterior de `materia_id` cuando sea seguro.

### Fase 3 — Evaluaciones y calificaciones

- Crear `Evaluacion`.
- Rediseñar `Calificacion`.
- Migrar las notas históricas cuando sea posible.
- Mantener las restricciones de integridad y las reglas de nota.

### Fase 4 — Cuentas e invitaciones

- Adaptar el alta de alumnos.
- Implementar la activación segura.
- Verificar la relación entre usuario y perfil académico.
- Revisar roles y permisos.

### Fase 5 — Retirada del modelo anterior

- Eliminar las dependencias restantes de `Materia`.
- Retirar su tabla solo después de validar las migraciones y los datos.
- Adaptar los servicios, routers y frontend.
- Ejecutar la suite completa de pruebas.

## 8. Tratamiento de las calificaciones históricas

El modelo actual permite una calificación por alumno, materia y período. El nuevo diseño permitirá varias evaluaciones dentro de un mismo período.

Por ello, las notas existentes no se convertirán automáticamente en exámenes individuales inexistentes.

Si deben conservarse, se evaluará representarlas mediante una evaluación histórica por materia y período. Antes de migrar, se comprobará el estado real de los datos y se validará el resultado.

## 9. Decisiones pendientes de implementación

Las siguientes cuestiones deberán resolverse durante la auditoría técnica:

- Cómo entregar las invitaciones: envío de correo automático o activación inicial asistida.
- Cómo tratar los alumnos existentes y vincular sus cuentas.
- Cómo mapear las calificaciones históricas.
- Qué servicios, routers y permisos deben adaptarse antes de retirar `Materia`.
- Qué restricciones compuestas conviene incorporar para reforzar la integridad académica.
- Cómo desplegar las migraciones sin perder datos.

Estas cuestiones no invalidan el diseño general; requieren conocer las dependencias reales antes de implementar.

## 10. Criterios de aceptación

El rediseño estará listo cuando:

- Cada docente pueda gestionar cursos propios.
- Dos docentes puedan crear cursos de la misma materia sin conflictos.
- Los alumnos puedan activar sus cuentas de forma segura.
- Los perfiles académicos puedan reutilizarse en varios cursos.
- Las inscripciones y calificaciones respeten las relaciones definidas.
- Los datos de un docente no sean accesibles desde la cuenta de otro.
- Los alumnos solo puedan consultar su información.
- Las migraciones se ejecuten correctamente.
- Los tests automatizados validen los casos correctos y los intentos de acceso no autorizado.

## 11. Principio de implementación

No se reescribirá el proyecto desde cero.

Se conservarán los componentes actuales que sigan siendo adecuados, y cada cambio se diseñará, implementará y probará de manera incremental.

**Este ADR establece la dirección de la arquitectura.** Antes de ejecutar migraciones, se verificará su compatibilidad con el esquema real, las relaciones existentes y los datos almacenados.
