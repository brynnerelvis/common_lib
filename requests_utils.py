import requests

from typing import Any, Dict, Optional
from common_lib.config import DEFAULT_TIMEOUT
from common_lib.exceptions import ApiError


class ResponseAsserter:
    """
    Assertions/utilities for HTTP responses returned by requests.
    Kept next to the HTTP client to avoid scattering concerns.
    """

    @staticmethod
    def status(resp: requests.Response, expected: int) -> requests.Response:
        if resp.status_code != expected:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            raise ApiError(
                message=f"Expected HTTP {expected}, got {resp.status_code}",
                status_code=resp.status_code,
                url=resp.url,
                method=getattr(resp.request, "method", None),
                payload=getattr(resp.request, "body", None),
                body=body,
            )
        return resp

    @staticmethod
    def json(resp: requests.Response) -> Dict[str, Any]:
        try:
            return resp.json()
        except Exception as e:
            raise ApiError(
                message=f"Response is not valid JSON. Error: {e}",
                status_code=resp.status_code,
                url=resp.url,
                method=getattr(resp.request, "method", None),
                body=resp.text[:300],
            )

    @staticmethod
    def json_has_keys(resp: requests.Response, *keys: str) -> Dict[str, Any]:
        data = ResponseAsserter.json(resp)
        missing = [k for k in keys if k not in data]
        if missing:
            raise ApiError(
                message=f"JSON missing keys: {missing}. Got: {list(data.keys())}",
                status_code=getattr(resp, "status_code", None),
                url=getattr(resp, "url", None),
                method=getattr(getattr(resp, "request", None), "method", None),
                body=data,
            )
        return data

    @staticmethod
    def json_path_equals(data: Dict[str, Any], path: str, expected: Any):
        node = data
        for part in path.split("."):
            if not (isinstance(node, dict) and part in node):
                raise ApiError(message=f"Path '{path}' missing at '{part}'. Got: {node}")
            node = node[part]
        if node != expected:
            raise ApiError(message=f"Expected {path} == {expected!r}, got {node!r}")


class ApiClient:
    """
    Minimal HTTP client with connection pooling (requests.Session)
    and a sane default timeout to avoid hanging tests.
    """

    def __init__(self, base_url: str, timeout: float = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def get(self, path: str, expected: Optional[int] = None, **kwargs) -> requests.Response:
        resp = self.session.get(self._url(path), timeout=self.timeout, **kwargs)
        return ResponseAsserter.status(resp, expected) if expected is not None else resp

    def post(
        self,
        path: str,
        json: Optional[Dict] = None,
        expected: Optional[int] = None,
        **kwargs,
    ) -> requests.Response:
        resp = self.session.post(self._url(path), json=json, timeout=self.timeout, **kwargs)
        return ResponseAsserter.status(resp, expected) if expected is not None else resp

    def put(
        self,
        path: str,
        json: Optional[Dict] = None,
        expected: Optional[int] = None,
        **kwargs,
    ) -> requests.Response:
        resp = self.session.put(self._url(path), json=json, timeout=self.timeout, **kwargs)
        return ResponseAsserter.status(resp, expected) if expected is not None else resp

    def delete(self, path: str, expected: Optional[int] = None, **kwargs) -> requests.Response:
        resp = self.session.delete(self._url(path), timeout=self.timeout, **kwargs)
        return ResponseAsserter.status(resp, expected) if expected is not None else resp
