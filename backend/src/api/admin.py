"""Admin settings API — persists to JSON file."""

import json
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from ..config import PROJECT_DIR

router = APIRouter(prefix="/api", tags=["admin"])

SETTINGS_FILE = PROJECT_DIR / "data" / "settings.json"

DEFAULT_SETTINGS = {
    "orgName": "KPC Inuka Foundation",
    "reportingFrequency": "quarterly",
    "emailNotifications": True,
    "defaultPeriod": "Q3 2026",
}


def _load() -> dict:
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULT_SETTINGS.copy()


def _save(data: dict) -> None:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


class SettingsUpdate(BaseModel):
    orgName: str | None = None
    reportingFrequency: str | None = None
    emailNotifications: bool | None = None
    defaultPeriod: str | None = None


@router.get("/admin/settings")
def get_settings():
    return _load()


@router.put("/admin/settings")
def update_settings(body: SettingsUpdate):
    current = _load()
    updates = body.model_dump(exclude_unset=True)
    current.update(updates)
    _save(current)
    return current
