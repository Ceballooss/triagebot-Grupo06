"""Clasificador LLM de TriageBot.

Único módulo que habla con el LLM. Llama a `openai/gpt-oss-120b` vía OpenRouter
(el SDK de OpenAI es compatible), valida la salida contra los enums del modelo y
aplica un fallback seguro ante cualquier fallo. Nunca propaga excepciones del
SDK al endpoint. Ver `SPEC.md` §5.
"""

from __future__ import annotations

import json
import os

from openai import OpenAI

from app.models import (
    ALLOWED_CATEGORIES,
    ALLOWED_PRIORITIES,
    MAX_TAG_LENGTH,
    MAX_TAGS,
)

FALLBACK_CLASSIFICATION = {"category": "question", "priority": "P3", "tags": []}

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "openai/gpt-oss-120b"
MAX_ATTEMPTS = 2

SYSTEM_PROMPT = (
    "Eres un sistema de clasificación de tickets de soporte técnico. Recibirás "
    "el título y la descripción de un ticket. Devuelve EXCLUSIVAMENTE un JSON "
    "con tres campos: category (uno de: bug, feature_request, question, urgent), "
    "priority (uno de: P1, P2, P3) y tags (lista de máximo 5 strings cortos en "
    "minúscula). No devuelvas explicaciones ni markdown. "
    "P1 = urgente, P2 = importante, P3 = normal."
)


def classify_ticket(title: str, description: str) -> dict:
    """Clasifica un ticket vía LLM; valida la salida y aplica fallback seguro.

    Devuelve siempre un dict con la forma exacta del contrato
    (`category`, `priority`, `tags`). Reintenta una vez ante fallo o salida
    inválida; nunca propaga excepciones del SDK.
    """
    for _ in range(MAX_ATTEMPTS):
        try:
            content = _call_llm(title, description)
            classification = _parse_and_validate(content)
            if classification is not None:
                return classification
        except Exception:
            # No propagar nunca excepciones del SDK: reintentar o caer al fallback.
            continue
    return dict(FALLBACK_CLASSIFICATION)


def _call_llm(title: str, description: str) -> str | None:
    """Llama a OpenRouter y devuelve el contenido textual de la respuesta."""
    client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=os.environ.get("OPENROUTER_API_KEY", ""),
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Título: {title}\nDescripción: {description}",
            },
        ],
        temperature=0,
    )
    return response.choices[0].message.content


def _parse_and_validate(content: str | None) -> dict | None:
    """Parsea el JSON del LLM y valida contra los enums. `None` si es inválido."""
    if not content:
        return None
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None

    category = data.get("category")
    priority = data.get("priority")
    if category not in ALLOWED_CATEGORIES or priority not in ALLOWED_PRIORITIES:
        return None

    return {
        "category": category,
        "priority": priority,
        "tags": _normalize_tags(data.get("tags", [])),
    }


def _normalize_tags(raw: object) -> list[str]:
    """Saneamiento defensivo de tags: como máximo `MAX_TAGS`, cada uno recortado
    a `MAX_TAG_LENGTH`. Garantiza que el modelo `Ticket` nunca rechace la salida.
    """
    if not isinstance(raw, list):
        return []
    tags: list[str] = []
    for tag in raw:
        if not isinstance(tag, str):
            continue
        cleaned = tag.strip()[:MAX_TAG_LENGTH]
        if cleaned:
            tags.append(cleaned)
        if len(tags) >= MAX_TAGS:
            break
    return tags
