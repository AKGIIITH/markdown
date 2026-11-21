"""One instrumented Groq call. The caller owns the retry and stage policy."""

import json
import os
from pathlib import Path
import re
import time
from urllib import error, request


def pace(path, run):
    quota = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    calls = quota.get("calls", 0)
    if calls >= int(os.environ.get("AUTOSE_MAX_PROVIDER_CALLS", "30")):
        raise ValueError("The run exhausted its provider call budget")
    delay = max(0, quota.get("reset_at", 0) - time.monotonic())
    if delay:
        run.event("provider_pacing", seconds=round(delay, 3), remaining=quota.get("remaining"))
        time.sleep(delay)
    return calls + 1


def save_quota(path, headers, calls):
    if path is None:
        return
    raw = headers.get("x-ratelimit-remaining-tokens", "")
    match = re.fullmatch(r"(?:(\d+)m)?([\d.]+)s", headers.get("x-ratelimit-reset-tokens", ""))
    reset = int(match[1] or 0) * 60 + float(match[2]) if match else 0
    retry = headers.get("retry-after", "")
    delay = max(60, reset, float(retry) if retry.isdigit() else 0)
    path.write_text(json.dumps(dict(remaining=int(raw) if raw.isdigit() else None,
                                    reset_at=time.monotonic() + delay, calls=calls)),
                    encoding="utf-8")


def completion_room(messages, tools):
    prompt = json.dumps([messages, tools], ensure_ascii=False)
    return 8000 - 400 - (len(prompt.encode("utf-8")) + 2) // 3


def _chat(body, key, run, attempt):
    if os.getenv("AUTOSE_RATE_STATE"):
        # Estimate the prompt from message/tool text and reserve protocol overhead.
        # Groq still owns the exact model tokenizer and has the final say.
        available = completion_room(body["messages"], body.get("tools", []))
        if available < 900:
            raise ValueError("Request exceeds the live prompt budget. Narrow the issue or retrieved excerpts.")
        body = {**body, "max_completion_tokens": min(available, body["max_completion_tokens"])}
        if body["model"].startswith("openai/gpt-oss-"):
            body["reasoning_format"] = "hidden"
            if "tools" in body and not any(
                tool["function"]["name"].startswith("submit_") for tool in body["tools"]
            ):
                body["reasoning_effort"] = "low"
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
    calls = pace(quota_path, run) if quota_path else None
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
    save_quota(quota_path, meta, calls)
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


def chat(body, key, run, attempt):
    if not os.getenv("AUTOSE_RATE_STATE"):
        return _chat(body, key, run, attempt)
    try:
        result = _chat(body, key, run, attempt)
        retry_after = result[1].get("retry-after", "")
        if (result[0] not in (429, 500, 502, 503, 504)
                or retry_after.isdigit() and int(retry_after) > 120):
            return result
    except RuntimeError as exc:
        if not str(exc).startswith("Groq transport failed"):
            raise
    for failure in run.path.glob(f"attempt-{attempt}*"):
        if failure.name == f"attempt-{attempt}.json" or failure.name.startswith(f"attempt-{attempt}-"):
            failure.rename(failure.with_name(failure.name.replace(f"attempt-{attempt}", f"attempt-{attempt}-first", 1)))
    run.event("provider_retry", attempt=attempt)
    return _chat(body, key, run, attempt)


def complete(body, key, run, attempt):
    status, meta, message, usage = chat(body, key, run, attempt)
    if message is None:
        return status, meta, None, usage
    content = message.get("content")
    if not isinstance(content, str):
        raise ValueError("Groq returned no text completion")
    run.write(f"attempt-{attempt}-completion.txt", content)
    return status, meta, content, usage


def provider_error_code(run, attempt):
    path = run.path / f"attempt-{attempt}-error.txt"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("error", {}).get("code")
    except (ValueError, AttributeError):
        return None


def parse_json_answer(text):
    value = text.strip()
    if value.startswith("```") and value.endswith("```"):
        opener, _, body = value.partition("\n")
        if opener.strip().casefold() in ("```", "```json"):
            value = body.removesuffix("```").strip()
    return json.loads(value)
