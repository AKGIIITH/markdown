"""One instrumented Groq call. The caller owns the retry and stage policy."""

import json
import time
from urllib import error, request


def complete(body, key, run, attempt):
    request_bytes = json.dumps(body).encode("utf-8")
    run.write("request-body.json", request_bytes.decode("utf-8"))
    req = request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=request_bytes,
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "User-Agent": "autose-a3-baseline/1",
        },
    )
    run.event("request_start", attempt=attempt)
    start = time.monotonic()
    transport_error = None
    try:
        with request.urlopen(req, timeout=90) as response:
            raw = response.read().decode("utf-8", errors="replace")
            status, headers = response.status, response.headers
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        status, headers = exc.code, exc.headers
    except (error.URLError, TimeoutError) as exc:
        raw, status, headers = "", None, {}
        transport_error = type(exc).__name__

    meta = {
        name.lower(): value for name, value in headers.items()
        if name.lower().startswith("x-ratelimit") or name.lower() in ("retry-after", "x-request-id")
    }
    run.save(f"attempt-{attempt}.json", dict(
        status=status, headers=meta,
        seconds=round(time.monotonic() - start, 3),
        transport_error=transport_error,
    ))
    run.event("request_end", attempt=attempt, status=status, transport_error=transport_error)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    choice = (data.get("choices") or [{}])[0]
    usage = dict(model=data.get("model") or body["model"], id=data.get("id"),
                 finish_reason=choice.get("finish_reason"), usage=data.get("usage"))
    run.save(f"attempt-{attempt}-usage.json", usage)
    if transport_error is not None:
        raise RuntimeError(f"Groq transport failed ({transport_error}). See attempt log.")
    if status != 200:
        run.write(f"attempt-{attempt}-error.txt", raw)
        return status, meta, None, usage

    content = choice.get("message", {}).get("content")
    if not isinstance(content, str):
        run.write(f"attempt-{attempt}-error.txt", raw)
        raise ValueError("Groq returned no text completion")
    run.write(f"attempt-{attempt}-completion.txt", content)
    return status, meta, content, usage
