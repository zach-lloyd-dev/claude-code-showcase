"""HTTP utilities for last48hours (stdlib only, no dependencies)."""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

DEFAULT_TIMEOUT = 30
DEBUG = os.environ.get("LAST48_DEBUG", "").lower() in ("1", "true", "yes")
MAX_RETRIES = 3
RETRY_DELAY = 2.0
USER_AGENT = "last48hours/1.0 (Zero to Automated Intelligence Briefing)"


class HTTPError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


def _log(msg: str):
    if DEBUG:
        sys.stderr.write(f"[HTTP] {msg}\n")
        sys.stderr.flush()


def request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = MAX_RETRIES,
    raw: bool = False,
) -> Any:
    headers = headers or {}
    headers.setdefault("User-Agent", USER_AGENT)

    data = None
    if json_data is not None:
        data = json.dumps(json_data).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    _log(f"{method} {url}")

    last_error = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = response.read().decode("utf-8")
                if raw:
                    return body
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            body = None
            try:
                body = e.read().decode("utf-8")
            except Exception:
                pass
            last_error = HTTPError(f"HTTP {e.code}: {e.reason}", e.code, body)
            if 400 <= e.code < 500 and e.code != 429:
                raise last_error
            if attempt < retries - 1:
                delay = RETRY_DELAY * (2 ** attempt) + (1 if e.code == 429 else 0)
                time.sleep(delay)
        except urllib.error.URLError as e:
            last_error = HTTPError(f"URL Error: {e.reason}")
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
        except json.JSONDecodeError as e:
            raise HTTPError(f"Invalid JSON response: {e}")
        except (OSError, TimeoutError, ConnectionResetError) as e:
            last_error = HTTPError(f"Connection error: {type(e).__name__}: {e}")
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))

    if last_error:
        raise last_error
    raise HTTPError("Request failed with no error details")


def get(url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Any:
    return request("GET", url, headers=headers, **kwargs)


def post(url: str, json_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None, **kwargs) -> Any:
    return request("POST", url, headers=headers, json_data=json_data, **kwargs)
