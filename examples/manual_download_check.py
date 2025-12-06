"""Manual script to exercise dload helpers with real URLs.

Run locally to verify that downloads work end-to-end without modifying the
library. Each step reports success and stops immediately on the first error.
"""

import os
import tempfile
from typing import Any

import dload


def _log_success(step: str, detail: str) -> None:
    print(f"[{step}] OK: {detail}")


def _log_error(step: str, exc: Exception) -> None:
    print(f"[{step}] ERROR: {exc}")


def _run_step(step: str, func):
    print(f"[{step}] starting...")
    try:
        result = func()
    except Exception as exc:  # pragma: no cover - manual script
        _log_error(step, exc)
        raise
    _log_success(step, result)
    return result


def _describe_json(payload: Any) -> str:
    if isinstance(payload, dict):
        sample_keys = list(payload.keys())[:5]
        return f"dict with {len(payload)} keys; sample={sample_keys}"
    if isinstance(payload, list):
        return f"list with {len(payload)} items"
    return f"{type(payload).__name__}: {payload!r}"


def main() -> None:
    tmp_dir = tempfile.gettempdir()

    _run_step(
        "save",
        lambda: dload.save(
            "https://examplefiles.org/files/images/jpg-example-file-download-2048x2048.jpg",
            os.path.join(tmp_dir, "jpg-example-file-download-2048x2048.jpg"),
            overwrite=True,
        ),
    )

    _run_step(
        "ftp",
        lambda: dload.ftp(
            "https://ftp.mozilla.org/pub/firefox/releases/52.9.0esr/firefox-52.9.0esr.win64.sdk.zip",
            os.path.join(tmp_dir, "firefox-52.9.0esr.win64.sdk.zip"),
            overwrite=True,
        ),
    )

    data = _run_step(
        "bytes",
        lambda: dload.bytes("https://example-files.online-convert.com/document/txt/example.txt"),
    )
    _log_success("bytes length", str(len(data)))

    json_payload = _run_step(
        "json",
        lambda: dload.json("https://microsoftedge.github.io/Demos/json-dummy-data/256KB.json"),
    )
    _log_success("json detail", _describe_json(json_payload))

    headers = _run_step(
        "headers",
        lambda: dload.headers(
            "https://support.oneskyapp.com/hc/en-us/article_attachments/202761627/example_1.json"
        ),
    )
    _log_success("Content-Type", headers.get("Content-Type", "<missing>"))

    text = _run_step(
        "text",
        lambda: dload.text("https://example-files.online-convert.com/document/txt/example.txt"),
    )
    _log_success("text sample", text[:60].replace("\n", " "))

    unzip_dir = _run_step(
        "save_unzip",
        lambda: dload.save_unzip(
            "https://file-examples.com/wp-content/uploads/2017/02/zip_2MB.zip",
            delete_after=True,
        ),
    )
    _log_success("save_unzip dir", unzip_dir)

    _run_step("git_clone", lambda: dload.git_clone("https://github.com/x011/dload.git"))


if __name__ == "__main__":  # pragma: no cover - manual script
    main()
