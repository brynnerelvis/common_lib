import uuid

from typing import Any, Dict


def unique_hex() -> str:
    """Return a fresh 32-char hex string."""
    return uuid.uuid4().hex


def unique_user(prefix: str = "test_user") -> str:
    """Generate a unique user_id."""
    return f"{prefix}_{unique_hex()}"


def unique_content(prefix: str = "content") -> str:
    """Generate a unique content string."""
    return f"{prefix}: {unique_hex()}"


def new_task_payload(
    *,
    user_id: str | None = None,
    content: str | None = None,
    is_done: bool = False,
) -> Dict[str, Any]:
    """
    Build a valid 'create task' payload with sensible defaults.
    """
    return {
        "user_id": user_id or unique_user(),
        "content": content or unique_content(),
        "is_done": is_done,
    }


def update_task_payload(
    *,
    task_id: str,
    user_id: str | None = None,
    content: str | None = None,
    is_done: bool | None = None,
) -> Dict[str, Any]:
    """
    Build an 'update task' payload. Only include fields that are provided,
    leaving others untouched server-side (if the API supports partial updates).
    """
    payload: Dict[str, Any] = {"task_id": task_id}
    if user_id is not None:
        payload["user_id"] = user_id
    if content is not None:
        payload["content"] = content
    if is_done is not None:
        payload["is_done"] = is_done
    return payload
