from __future__ import annotations

from io import BytesIO
import json
import socket
import unittest
from unittest.mock import patch
from urllib import error

from ai_git_assistant.errors import ProviderError
from ai_git_assistant.providers import OpenAICompatibleProvider


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.data = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self.data


class ProviderTests(unittest.TestCase):
    def test_parses_success_response(self) -> None:
        provider = OpenAICompatibleProvider(api_key="test-key", api_url="https://example.invalid")
        payload = {"choices": [{"message": {"content": "TITLE: ok\nBODY:\n- change"}}]}
        with patch("ai_git_assistant.providers.request.urlopen", return_value=FakeResponse(payload)):
            output = provider.generate("p", model="m", temperature=0.2, max_tokens=100)
        self.assertIn("TITLE: ok", output)

    def test_reports_auth_http_error(self) -> None:
        provider = OpenAICompatibleProvider(api_key="bad", api_url="https://example.invalid")
        exc = error.HTTPError(
            "https://example.invalid",
            401,
            "Unauthorized",
            hdrs=None,
            fp=BytesIO(b'{"error":"invalid key"}'),
        )
        with patch("ai_git_assistant.providers.request.urlopen", side_effect=exc):
            with self.assertRaisesRegex(ProviderError, "HTTP 401"):
                provider.generate("p", model="m", temperature=0.2, max_tokens=100)

    def test_reports_network_error(self) -> None:
        provider = OpenAICompatibleProvider(api_key="x", api_url="https://example.invalid")
        with patch(
            "ai_git_assistant.providers.request.urlopen",
            side_effect=error.URLError("offline"),
        ):
            with self.assertRaisesRegex(ProviderError, "네트워크"):
                provider.generate("p", model="m", temperature=0.2, max_tokens=100)

    def test_reports_timeout(self) -> None:
        provider = OpenAICompatibleProvider(api_key="x", api_url="https://example.invalid")
        with patch(
            "ai_git_assistant.providers.request.urlopen",
            side_effect=socket.timeout("timed out"),
        ):
            with self.assertRaisesRegex(ProviderError, "타임아웃"):
                provider.generate("p", model="m", temperature=0.2, max_tokens=100)
