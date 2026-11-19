"""One instrumented Groq call. The caller owns the retry and stage policy."""

import json
import os
from pathlib import Path
import re
import time
from urllib import error, request


def pace(path, request_size, completion_cap, run):
    if path is None or not path.is_file():
        return
    quota = json.loads(path.read_text(encoding="utf-8"))
    estimated = request_size // 3 + completion_cap
    delay = max(0, quota["reset_at"] - time.monotonic())
    if estimated > quota["remaining"] and delay:
        run.event("provider_pacing", seconds=round(delay, 3), remaining=quota["remaining"])
        time.sleep(delay)


def save_quota(path, headers):
    raw = headers.get("x-ratelimit-remaining-tokens", "")
    match = re.fullmatch(r"(?:(\d+)m)?([\d.]+)s", headers.get("x-ratelimit-reset-tokens", ""))
    if path is not None and raw.isdigit() and match:
        delay = int(match[1] or 0) * 60 + float(match[2])
        path.write_text(json.dumps(dict(remaining=int(raw), reset_at=time.monotonic() + delay + 1)),
                        encoding="utf-8")


def chat(body, key, run, attempt):
    request_bytes = json.dumps(body).encode("utf-8")
    run.write(f"attempt-{attempt}-request.json", request_bytes.decode("utf-8"))
    req = request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=request_bytes,
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "User-Agent": "autose-a3-baseline/1",
        },
    )
    state = os.getenv("AUTOSE_RATE_STATE")
    quota_path = Path(state) if state else None
    pace(quota_path, len(request_bytes), body.get("max_completion_tokens", 0), run)
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
    save_quota(quota_path, meta)
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

    message = choice.get("message")
    if not isinstance(message, dict):
        run.write(f"attempt-{attempt}-error.txt", raw)
        raise ValueError("Groq returned no assistant message")
    run.save(f"attempt-{attempt}-message.json", message)
    return status, meta, message, usage


def complete(body, key, run, attempt):
    status, meta, message, usage = chat(body, key, run, attempt)
    if message is None:
        return status, meta, None, usage
    content = message.get("content")
    if not isinstance(content, str):
        raise ValueError("Groq returned no text completion")
    run.write(f"attempt-{attempt}-completion.txt", content)
    return status, meta, content, usage
