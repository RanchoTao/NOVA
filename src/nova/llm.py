"""Opt-in OpenAI-compatible chat adapter. Uses standard library only.

NOVA never performs model calls unless the user explicitly chooses --provider model.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class ModelError(RuntimeError):
    pass


class ChatJSONClient:
    def __init__(self, *, base_url: str | None = None, model: str | None = None,
                 api_key: str | None = None, timeout: float = 60.0):
        self.base_url = (base_url or os.environ.get("NOVA_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.model = model or os.environ.get("NOVA_MODEL")
        self.api_key = api_key or os.environ.get("NOVA_API_KEY")
        self.timeout = timeout
        parts = urllib.parse.urlsplit(self.base_url)
        is_local = parts.hostname in {"localhost", "127.0.0.1", "::1"}
        if parts.scheme != "https" and not (parts.scheme == "http" and is_local):
            raise ValueError("NOVA_BASE_URL must be HTTPS or loopback HTTP")
        if not self.model:
            raise ValueError("NOVA_MODEL must be set for --provider model")
        if not self.api_key:
            raise ValueError("NOVA_API_KEY must be set for --provider model")

    def complete_json(self, system: str, user: str) -> dict[str, Any]:
        payload = json.dumps({"model": self.model, "messages": [
            {"role": "system", "content": system}, {"role": "user", "content": user}
        ], "temperature": 0.9, "max_tokens": 1400}).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + "/chat/completions", data=payload, method="POST",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                if int(response.headers.get("Content-Length", "0")) > 1000000:
                    raise ModelError("response too large")
                raw = response.read(1000001)
        except (urllib.error.URLError, TimeoutError) as exc:
            # Never expose exception text: provider errors may contain credentials.
            raise ModelError("model endpoint unavailable; inspect local provider configuration") from None
        if len(raw) > 1000000:
            raise ModelError("response too large")
        try:
            content = json.loads(raw)["choices"][0]["message"]["content"]
            data = json.loads(content)
        except (ValueError, IndexError, TypeError, KeyError) as exc:
            raise ModelError("model did not return a valid JSON object") from None
        if not isinstance(data, dict):
            raise ModelError("model JSON result is not an object")
        return data
