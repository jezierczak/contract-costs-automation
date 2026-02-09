import os
from pathlib import Path
import json
from uuid import UUID


APP_ENV = os.getenv("APP_ENV", "local")

SESSION_FILE = (
    Path.home()
    / ".contract_costs"
    / APP_ENV
    / "session.json"
)


def save_session(*, user_id: UUID, organization_id: UUID | None = None) -> None:
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(
        json.dumps(
            {
                "user_id": str(user_id),
                "organization_id": str(organization_id) if organization_id else None,
            }
        )
    )


def clear_session() -> None:
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()


def load_session() -> dict | None:
    if not SESSION_FILE.exists():
        return None
    return json.loads(SESSION_FILE.read_text())
