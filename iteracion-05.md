# Iteración 5 - Nuevas funcionalidades (plazos y ciclo de vida)

## Objetivo
Implementar dos líneas de trabajo paralelas e independientes que amplían el modelo
de datos y el frontend: gestión de plazos con alertas de vencimiento, y expansión
del ciclo de vida del ticket con registro de tiempos por estado.

## Contexto
Depende de IT-1–IT-4.1 (modelo, clasificador, API y frontend ya implementados).
Cada trabajo vive en su propia rama y puede desarrollarse en paralelo sin conflictos.

---

## TRABAJO 1 — Gestión de plazos y alertas de vencimiento
**Rama:** `feature/plazos-tickets`

### Objetivo
Calcular automáticamente fechas límite según la prioridad del ticket, visualizar
alertas en el tablero e identificar tickets retrasados mediante un filtro de URL.

### Tareas

#### `app/models.py`
- [ ] Añadir campo `fecha_limite: datetime` (UTC) al modelo `Ticket`
- [ ] Hook o método que calcule `fecha_limite` al crear un ticket según prioridad:
  - P1 (Alta): `23:59:59` del día de creación (EoD)
  - P2 (Media): `23:59:59` del día siguiente (+24 h)
  - P3 (Baja): `23:59:59` pasado mañana (+48 h)
- [ ] Propiedad `esta_vencido` → `True` si `fecha_limite < utcnow()` y el ticket
  no está en estado de finalización

#### `app/db.py`
- [ ] Añadir columna `fecha_limite` al esquema de la tabla de tickets
- [ ] `create_ticket` y `update_ticket` mapean y persisten `fecha_limite`

#### Handler `GET /tickets`
- [ ] Aceptar parámetro de consulta `?vencidos=true`
- [ ] Si activo, filtrar: `fecha_limite < utcnow()` AND estado no finalizado

#### `templates/index.html`
- [ ] Mostrar `fecha_limite` formateada en la tarjeta del ticket
- [ ] Si `ticket.esta_vencido`, inyectar clase CSS de alerta (fondo/borde rojo suave
  o badge "Vencido")
- [ ] Botón/checkbox de alternancia que filtre vía `?vencidos=true`

---

## TRABAJO 2 — Ciclo de vida del ticket y tiempos de estado
**Rama:** `feature/ciclo-vida-tickets`

### Objetivo
Expandir los estados disponibles, registrar cuándo cambia cada estado y calcular
el tiempo transcurrido en el estado actual. Habilitar la reapertura de incidencias.

### Tareas

#### `app/models.py`
- [ ] Ampliar el enum `status` (o campo `estado`) a cuatro valores:
  `abierto`, `en_curso`, `resuelto`, `cerrado`
- [ ] Añadir campo `fecha_cambio_estado: datetime` (UTC) que registre la última
  modificación de estado
- [ ] Máquina de estados con transiciones libres, incluyendo reapertura explícita
  (`resuelto`/`cerrado` → `abierto`/`en_curso`)
- [ ] Propiedad `tiempo_en_estado_actual` que devuelva texto legible:
  - `"X min"` / `"X h"` / `"X días"` según el tiempo desde `fecha_cambio_estado`

#### `app/db.py`
- [ ] Añadir columna `fecha_cambio_estado` al esquema
- [ ] Toda actualización que cambie `status` debe forzar
  `fecha_cambio_estado = utcnow()`

#### Handler `GET /tickets`
- [ ] Pasar `tiempo_en_estado_actual` a la plantilla para cada ticket

#### `templates/index.html`
- [ ] Reorganizar tablero en cuatro columnas: *Abierto*, *En Curso*, *Resuelto*,
  *Cerrado*
- [ ] Mostrar en cada tarjeta el literal de tiempo (ej. `"En curso desde hace 45 min"`)
- [ ] Botones condicionales por estado:
  - *Abierto* → botón "Comenzar" (muta a `en_curso`)
  - *En Curso* → botón "Resolver" (muta a `resuelto`)
  - *Resuelto* o *Cerrado* → botón "Reabrir" (muta a `abierto`)

---

## Ficheros afectados
- `app/models.py`
- `app/db.py`
- `app/main.py`
- `templates/index.html`

## Criterio de completado
- Trabajo 1: al crear ticket P1, `fecha_limite` es EoD del día; un ticket caducado
  muestra badge "Vencido"; `?vencidos=true` filtra solo tickets retrasados.
- Trabajo 2: cuatro estados disponibles; al cambiar estado, `fecha_cambio_estado`
  se actualiza; las tarjetas muestran el tiempo en estado actual; los botones
  mutan el estado correctamente incluyendo reapertura.

## Estado
PENDIENTE
