"""Capa de persistencia: engine SQLite y sesiones.

La URL de la base de datos se lee de `DATABASE_URL` (los tests la usan para
aislar la BD); por defecto un archivo local `triagebot.db` (SPEC §2).
"""

from __future__ import annotations

import os
from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

# Importa los modelos para que queden registrados en `SQLModel.metadata`
# antes de crear las tablas.
from app import models  # noqa: F401

DEFAULT_DATABASE_URL = "sqlite:///triagebot.db"


def _database_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


def _make_engine(url: str):
    # `check_same_thread=False` es necesario para usar SQLite con el
    # TestClient de FastAPI (varios hilos comparten la conexión).
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


# Cache de engines por URL: la suite de aceptación fija un `DATABASE_URL`
# distinto por test (sin recargar este módulo), así que el engine debe
# resolverse según la URL vigente en cada petición para garantizar el
# aislamiento entre tests.
_engines: dict = {}


def get_engine():
    """Devuelve el engine asociado al `DATABASE_URL` vigente (cacheado por URL)."""

    url = _database_url()
    eng = _engines.get(url)
    if eng is None:
        eng = _make_engine(url)
        _engines[url] = eng
    return eng


# Atributo de módulo para compatibilidad: refleja la URL vigente al
# importar/recargar `db` (lo usa `tests/test_models.py`).
engine = get_engine()


def create_db_and_tables() -> None:
    """Crea todas las tablas declaradas en los modelos SQLModel."""

    SQLModel.metadata.create_all(get_engine())


def get_session() -> Iterator[Session]:
    """Provee una sesión de base de datos (dependencia de FastAPI)."""

    eng = get_engine()
    # El TestClient de la suite de aceptación no usa el context manager, por lo
    # que los eventos de startup pueden no dispararse: aseguramos las tablas
    # aquí de forma idempotente.
    SQLModel.metadata.create_all(eng)
    with Session(eng) as session:
        yield session
