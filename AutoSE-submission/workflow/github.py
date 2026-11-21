"""Small authenticated GitHub client for trusted workflow jobs."""

import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .trigger import FORK


API = f"/repos/{FORK}"


class GitHubError(RuntimeError):
    def __init__(self, method, path, status, request_id):
        self.status = status
        super().__init__(f"{method} {path} returned HTTP {status} (request {request_id})")


class GitHub:
    def __init__(self, token):
        self.token = token

    def request(self, path, payload=None, *, missing=False):
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = Request("https://api.github.com" + path, data=data, headers={
            "Authorization": "Bearer " + self.token,
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "autose-a3-baseline/1",
        })
        try:
            with urlopen(req, timeout=30) as response:
                return json.load(response)
        except HTTPError as exc:
            if missing and exc.code == 404:
                return None
            raise GitHubError(req.get_method(), path, exc.code, exc.headers.get("x-github-request-id")) from None
