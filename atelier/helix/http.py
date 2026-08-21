"""Pinned HTTP helpers — credentialed calls never follow redirects."""

from __future__ import annotations

import urllib.error
import urllib.request


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Returning None makes urllib raise HTTPError instead of replaying
        # Authorization headers against an attacker-chosen Location.
        return None


def opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(NoRedirectHandler)


def urlopen_no_redirect(req: urllib.request.Request, timeout: float = 120):
    try:
        return opener().open(req, timeout=timeout)
    except urllib.error.HTTPError as exc:
        if 300 <= int(getattr(exc, "code", 0) or 0) < 400:
            location = ""
            try:
                location = exc.headers.get("Location", "") if exc.headers else ""
            except Exception:
                location = ""
            from .spokes.base import SpokeError

            raise SpokeError(f"Refusing HTTP redirect {exc.code} to {location}") from exc
        raise
