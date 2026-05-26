"""Tests for the polite GhaLII HTTP client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
import requests

from clauseguard.reference.ghalii_client import (
    DEFAULT_USER_AGENT,
    GhaliiClient,
    GhaliiClientError,
    RobotsDisallowedError,
)


@dataclass
class FakeRobots:
    """Small robots.txt stand-in for tests."""

    allowed: bool = True

    def can_fetch(self, user_agent: str, url: str) -> bool:
        """Return the configured robots decision."""

        return self.allowed


class FakeResponse:
    """Small response object matching the client needs."""

    def __init__(self, status_code: int, text: str = "ok") -> None:
        """Create a fake response."""

        self.status_code = status_code
        self.text = text

    def raise_for_status(self) -> None:
        """Raise for server errors."""

        if self.status_code >= 500:
            raise requests.HTTPError(f"status {self.status_code}")


class FakeSession:
    """Small requests session stand-in."""

    def __init__(self, results: list[FakeResponse | Exception]) -> None:
        """Create a fake session with queued results."""

        self.results = results
        self.calls: list[dict[str, Any]] = []

    def get(self, url: str, headers: dict[str, str], timeout: float) -> FakeResponse:
        """Return the next queued result."""

        self.calls.append({"url": url, "headers": headers, "timeout": timeout})
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def test_get_text_sends_user_agent_and_timeout() -> None:
    """Fetch text with the configured user agent and timeout."""

    session = FakeSession([FakeResponse(200, "hello")])
    client = GhaliiClient(session=session, robot_parser=FakeRobots())

    text = client.get_text("/legislation/")

    assert text == "hello"
    assert session.calls[0]["url"] == "https://ghalii.org/legislation/"
    assert session.calls[0]["headers"]["User-Agent"] == DEFAULT_USER_AGENT
    assert session.calls[0]["timeout"] == 30.0


def test_robots_disallowed_url_aborts_before_request() -> None:
    """Do not fetch URLs blocked by robots.txt."""

    session = FakeSession([FakeResponse(200)])
    client = GhaliiClient(session=session, robot_parser=FakeRobots(allowed=False))

    with pytest.raises(RobotsDisallowedError):
        client.get_text("/blocked/")

    assert session.calls == []


def test_connection_errors_retry_with_backoff() -> None:
    """Retry connection errors twice with exponential backoff."""

    sleeps: list[float] = []
    session = FakeSession(
        [
            requests.ConnectionError("temporary"),
            requests.ConnectionError("temporary"),
            FakeResponse(200, "recovered"),
        ]
    )
    client = GhaliiClient(session=session, robot_parser=FakeRobots(), sleeper=sleeps.append)

    assert client.get_text("/recover/") == "recovered"
    assert sleeps == [2.0, 4.0]
    assert len(session.calls) == 3


def test_client_error_is_not_retried() -> None:
    """Do not retry 4xx responses."""

    session = FakeSession([FakeResponse(404, "missing")])
    client = GhaliiClient(session=session, robot_parser=FakeRobots())

    with pytest.raises(GhaliiClientError, match="Client error 404"):
        client.get_text("/missing/")

    assert len(session.calls) == 1


def test_server_error_raises_client_error() -> None:
    """Wrap server errors in a client error."""

    session = FakeSession([FakeResponse(500)])
    client = GhaliiClient(session=session, robot_parser=FakeRobots())

    with pytest.raises(GhaliiClientError, match="HTTP error"):
        client.get_text("/broken/")


def test_too_many_consecutive_failures_aborts() -> None:
    """Abort after more than five consecutive failures."""

    session = FakeSession([FakeResponse(404) for _ in range(6)])
    client = GhaliiClient(session=session, robot_parser=FakeRobots())

    for _ in range(5):
        with pytest.raises(GhaliiClientError):
            client.get_text("/missing/")

    with pytest.raises(GhaliiClientError, match="More than five"):
        client.get_text("/missing/")


def test_waits_between_successive_requests() -> None:
    """Sleep before a second immediate request."""

    sleeps: list[float] = []
    session = FakeSession([FakeResponse(200), FakeResponse(200)])
    client = GhaliiClient(session=session, robot_parser=FakeRobots(), sleeper=sleeps.append)

    client.get_text("/one/")
    client.get_text("/two/")

    assert sleeps
    assert sleeps[0] <= 1.0


def test_default_robot_parser_is_loaded() -> None:
    """Create and read a default robots parser when one is not supplied."""

    client = GhaliiClient()
    parser = FakeRobots()
    client.robot_parser = parser  # Avoid live robots.txt in this unit test.

    assert client._robots() is parser
