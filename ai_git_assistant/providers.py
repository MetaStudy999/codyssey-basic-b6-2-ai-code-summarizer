from __future__ import annotations

from abc import ABC, abstractmethod
import json
import socket
from urllib import error, request

from .errors import ProviderError


class AIProvider(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        raise NotImplementedError


class OpenAICompatibleProvider(AIProvider):
    """Minimal REST client for an OpenAI-compatible chat-completions endpoint.

    The endpoint is configurable so the CLI core does not depend on one vendor.
    """

    def __init__(self, *, api_key: str, api_url: str, timeout: float = 30.0) -> None:
        self.api_key = api_key
        self.api_url = api_url
        self.timeout = timeout

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        payload = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.api_url,
            data=data,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace").strip()
            detail = detail[:300] if detail else str(exc.reason)
            raise ProviderError(f"AI API HTTP {exc.code}: {detail}") from exc
        except (error.URLError, TimeoutError, socket.timeout) as exc:
            reason = getattr(exc, "reason", exc)
            raise ProviderError(f"AI API 네트워크/타임아웃 오류: {reason}") from exc
        except OSError as exc:
            raise ProviderError(f"AI API 연결 오류: {exc}") from exc

        try:
            parsed = json.loads(raw)
            content = parsed["choices"][0]["message"]["content"]
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            raise ProviderError("AI API 응답 형식을 해석할 수 없습니다.") from exc
        if not isinstance(content, str) or not content.strip():
            raise ProviderError("AI API 응답 텍스트가 비어 있습니다.")
        return content.strip()
