from typing import Any, Dict, Optional


class ApiError(Exception):
    """
    Raised when an HTTP response does not meet expectations.
    Useful to catch in tests (e.g., teardown deletes) without masking real failures.
    """
    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        url: Optional[str] = None,
        method: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        body: Optional[Any] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.url = url
        self.method = method
        self.payload = payload
        self.body = body

    def __str__(self) -> str:
        base = super().__str__()
        meta = []
        if self.method:
            meta.append(f"{self.method}")
        if self.url:
            meta.append(self.url)
        if self.status_code is not None:
            meta.append(f"[HTTP {self.status_code}]")
        meta_str = " ".join(meta)
        return f"{base} {meta_str}".strip()


class ConfigError(FileNotFoundError):
    """
    Raised when the ./config.yml cannot be found or loaded properly.
    Keep it explicit so test output is self-explanatory.
    """
    pass
