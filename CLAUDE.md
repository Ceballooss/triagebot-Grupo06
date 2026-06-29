# CLAUDE.md

> **Equipo B (Spec-Driven):** este archivo es vuestro. Completadlo con vuestras
> convenciones como parte del trabajo de hoy — es tan importante como el `SPEC.md`
> que vais a escribir. Claude Code lo lee automáticamente al abrir el repo.
>
> **Equipo A (Vibe):** podéis ignorarlo. No estáis obligados a tocarlo.

Este repo es una plantilla docente para construir **TriageBot**, una aplicación
FastAPI que clasifica tickets de soporte con un LLM (gpt-oss-120b vía OpenRouter).

## Stack (innegociable)

- Python 3.11+
- FastAPI
- SQLite
- HTMX + Jinja2
- Tailwind (por CDN)
- SDK de OpenAI (apuntado a OpenRouter)
- pytest
- ruff

## Reglas del taller (para todos los equipos)

Estas reglas no son metodología: son condiciones del bootcamp. Se cumplen seas
del equipo que seas.

1. No modifiques `tests/test_acceptance.py` salvo que el profesor lo indique
   expresamente.
2. Nunca hardcodees una API key en el código.
3. Lee la API key desde la variable de entorno `OPENROUTER_API_KEY`.
4. `.env` nunca se commitea. Comprueba que está en `.gitignore` antes de tu
   primer commit.

## Comandos útiles

```bash
pytest -v
pytest --cov=app
ruff check .
uvicorn app.main:app --reload
```

## Política de ramas (Git workflow)

Estas reglas aplican a todo el equipo y a Claude Code. **Objetivo: `main` siempre
estable y desplegable.**

### Reglas

1. **Nunca commitees ni hagas push directamente sobre `main`.** Todo cambio entra
   vía Pull Request.
2. **Una rama por tarea.** Cada feature, fix o cambio vive en su propia rama; no
   acumules trabajo sin relación en la misma rama.
3. **Parte siempre de `main` actualizado:**
   ```bash
   git switch main && git pull origin main
   git switch -c <tipo>/<descripcion-corta>
   ```
4. **Convención de nombres:** `<tipo>/<descripcion-en-kebab-case>`, corta y
   descriptiva. Tipos permitidos:
   | Prefijo | Uso |
   |---|---|
   | `feat/` | Nueva funcionalidad |
   | `fix/` | Corrección de bug |
   | `docs/` | Documentación |
   | `refactor/` | Refactor sin cambio de comportamiento |
   | `test/` | Solo tests |
   | `chore/` | Mantenimiento, config, dependencias |

   Ejemplos: `feat/post-tickets`, `fix/validacion-titulo`, `docs/nombre-iker`.
5. **Commits pequeños y frecuentes** (cada 20–30 min), con mensajes en formato
   Conventional Commits: `<tipo>: <descripción en imperativo>`.
6. **Sincroniza con `main` a menudo** para evitar conflictos grandes:
   `git switch main && git pull` y luego `git merge main` (o rebase) en tu rama.
7. **Abre el PR contra `main`.** No se mergea hasta que:
   - la CI esté en verde (ruff + pytest), y
   - al menos otra persona del equipo lo haya revisado.
8. **No fuerces el push** (`--force`) sobre ramas compartidas. Si necesitas
   reescribir historia, usa `--force-with-lease` y solo en tu rama propia.
9. **Borra la rama tras el merge:**
   ```bash
   git switch main && git pull
   git branch -d <rama>
   ```

### Comandos del flujo

```bash
git switch -c feat/mi-tarea          # 1. crear rama desde main actualizado
git add . && git commit -m "feat: ..."  # 2. commits pequeños
git push -u origin feat/mi-tarea     # 3. subir la rama
gh pr create --base main --fill      # 4. abrir PR
# 5. CI verde + review -> merge en GitHub -> borrar rama
```
