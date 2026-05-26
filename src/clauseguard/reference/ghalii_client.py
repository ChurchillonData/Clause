"""HTTP client for polite access to GhaLII."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import cast
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests

DEFAULT_BASE_URL = "https://ghalii.org"
DEFAULT_USER_AGENT = "ClauseGuard/0.1 (research mirror; contact: owura@govaxis.ai)"


class GhaliiClientError(RuntimeError):
    """Raised when a GhaLII request cannot be completed safely."""


class RobotsDisallowedError(GhaliiClientError):
    """Raised when robots.txt disallows a URL."""


@dataclass
class GhaliiClient:
    """Small HTTP client with GhaLII politeness controls."""

    base_url: str = DEFAULT_BASE_URL
    user_agent: str = DEFAULT_USER_AGENT
    session: requests.Session = field(default_factory=requests.Session)
    sleeper: Callable[[float], None] = time.sleep
    robot_parser: RobotFileParser | None = None
    timeout_seconds: float = 30.0
    min_delay_seconds: float = 1.0
    max_retries: int = 2
    max_consecutive_failures: int = 5
    _last_request_at: float | None = None
    _consecutive_failures: int = 0

    def get_text(self, url: str) -> str:
        """Fetch a URL and return response text.

        Args:
            url: Absolute or root-relative URL.

        Returns:
            Response text.

        Raises:
            GhaliiClientError: If the request fails.
            RobotsDisallowedError: If robots.txt disallows the URL.
        """

        absolute_url = self.absolute_url(url)
        self.ensure_allowed(absolute_url)
        response = self._send_with_retries(absolute_url)
        self._consecutive_failures = 0
        return cast(str, response.text)

    def absolute_url(self, url: str) -> str:
        """Return an absolute URL for a root-relative or absolute input."""

        return url if url.startswith("http") else urljoin(self.base_url, url)

    def ensure_allowed(self, url: str) -> None:
        """Abort when robots.txt disallows a URL."""

        parser = self._robots()
        if not parser.can_fetch(self.user_agent, url):
            raise RobotsDisallowedError(f"robots.txt disallows fetch: {url}")

    def _send_with_retries(self, url: str) -> requests.Response:
        """Send a GET request with retry rules."""

        for attempt in range(self.max_retries + 1):
            self._wait_if_needed()
            try:
                return self._send_once(url)
            except requests.ConnectionError as exc:
                self._handle_connection_error(attempt, exc)
        raise GhaliiClientError(f"Failed to fetch after retries: {url}")

    def _send_once(self, url: str) -> requests.Response:
        """Send one GET request and apply status rules."""

        headers = {"User-Agent": self.user_agent}
        response = self.session.get(url, headers=headers, timeout=self.timeout_seconds)
        self._last_request_at = time.monotonic()
        if 400 <= response.status_code < 500:
            self._record_failure()
            raise GhaliiClientError(f"Client error {response.status_code}: {url}")
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            self._record_failure()
            raise GhaliiClientError(f"HTTP error for {url}: {exc}") from exc
        return response

    def _wait_if_needed(self) -> None:
        """Sleep long enough to keep one request per second."""

        if self._last_request_at is None:
            return
        elapsed = time.monotonic() - self._last_request_at
        wait_seconds = self.min_delay_seconds - elapsed
        if wait_seconds > 0:
            self.sleeper(wait_seconds)

    def _handle_connection_error(self, attempt: int, exc: requests.ConnectionError) -> None:
        """Retry connection errors with exponential backoff."""

        self._record_failure()
        if attempt >= self.max_retries:
            raise GhaliiClientError(f"Connection failed after retries: {exc}") from exc
        self.sleeper(2.0 * (2**attempt))

    def _record_failure(self) -> None:
        """Abort if too many consecutive failures occur."""

        self._consecutive_failures += 1
        if self._consecutive_failures > self.max_consecutive_failures:
            raise GhaliiClientError("More than five consecutive GhaLII failures.")

    def _robots(self) -> RobotFileParser:
        """Return a loaded robots.txt parser."""

        if self.robot_parser is None:
            self.robot_parser = RobotFileParser(urljoin(self.base_url, "/robots.txt"))
            self.robot_parser.read()
        return self.robot_parser
