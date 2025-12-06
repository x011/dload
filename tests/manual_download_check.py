"""
Manual check script for dload helpers.

- Verifies each helper with the provided URLs.
- Stops on first error; otherwise prints concise success info.
- Adds a simple download speed measurement and a concurrent multi-download demo.
"""

import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Iterable, Tuple

import dload


def _log_success(step: str, detail: str) -> None:
    print(f"[{step}] OK: {detail}")


def _log_error(step: str, exc: Exception) -> None:
    print(f"[{step}] ERROR: {exc}")


def _run_step(step: str, func):
    print(f"[{step}] starting...")
    try:
        result = func()
    except Exception as exc:
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


def _download_and_time(url: str, target: str) -> Tuple[str, float]:
    start = time.perf_counter()
    dload.save(url, target, overwrite=True)
    elapsed = time.perf_counter() - start
    return target, elapsed


def _download_many(urls: Iterable[str], dest_dir: str, max_threads: int = 5) -> None:
    os.makedirs(dest_dir, exist_ok=True)
    print(f"[save_multi] downloading {len(list(urls))} files with {max_threads} threads...")
    urls = list(urls)
    with ThreadPoolExecutor(max_workers=max_threads) as pool:
        futures = {
            pool.submit(_download_and_time, url, os.path.join(dest_dir, os.path.basename(url))): url
            for url in urls
        }
        for future in as_completed(futures):
            url = futures[future]
            try:
                path, elapsed = future.result()
                _log_success("save_multi", f"{url} -> {path} ({elapsed:.2f}s)")
            except Exception as exc:
                _log_error(f"save_multi {url}", exc)
                raise


def _down_speed_summary(size: int = 5, ipv: str = "ipv4", port: int = 80) -> str:
    start = time.perf_counter()
    result = dload.down_speed(size=size, ipv=ipv, port=port)
    elapsed = time.perf_counter() - start
    status = "completed" if result else "did not complete"
    return f"{size}MB over {ipv}:{port} {status} in {elapsed:.2f}s"


def main() -> None:
    tmp_dir = tempfile.gettempdir()

    _run_step(
        "save",
        lambda: dload.save(
            "https://example-files.online-convert.com/raster%20image/jpg/example.jpg",
            os.path.join(tmp_dir, "example.jpg"),
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
        lambda: dload.json("https://example-files.online-convert.com/filelist.json"),
    )
    _log_success("json detail", _describe_json(json_payload))

    headers = _run_step(
        "headers",
        lambda: dload.headers("https://example-files.online-convert.com/filelist.json"),
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
            "https://example-files.online-convert.com/archive/zip/example.zip",
            delete_after=True,
        ),
    )
    _log_success("save_unzip dir", unzip_dir)

    _run_step("down_speed", _down_speed_summary)

    # Simple speed check: download a mid-size file and report duration
    target, elapsed = _download_and_time(
        "https://ftp.mozilla.org/pub/firefox/releases/1.0.6/win32/cs-CZ/Firefox%20Setup%201.0.6.exe",
        os.path.join(tmp_dir, "Firefox%20Setup%201.0.6.exe"),
    )
    _log_success("speed_test", f"{target} downloaded in {elapsed:.2f}s")

    # Multi-download example with concurrency
    file_list = [
        "https://ftp.mozilla.org/pub/firefox/releases/0.8/contrib/firefox-0.8-i386-pc-solaris2.8.tar.gz",
        "https://ftp.mozilla.org/pub/firefox/releases/0.8/contrib/firefox-0.8-i386-unknown-netbsdelf1.6.tar.bz2",
        "https://ftp.mozilla.org/pub/firefox/releases/1.0.6/linux-i686/da-DK/firefox-1.0.6.tar.gz",
        "https://ftp.mozilla.org/pub/firefox/releases/1.0.6/linux-i686/da-DK/firefox-1.0.6.installer.tar.gz",
        "https://ftp.mozilla.org/pub/firefox/releases/0.8/contrib/firefox-0.8-i686-pc-linux-gnu-ctl-svg.tar.gz",
        "https://ftp.mozilla.org/pub/firefox/releases/0.8/contrib/firefox-0.8-sparc-sun-solaris2.8-gtk2.tar.gz",
        "https://ftp.mozilla.org/pub/firefox/releases/0.8/contrib/firefox-os2-0.8.zip",
        "https://ftp.mozilla.org/pub/firefox/releases/0.8/FirefoxSetup-0.8.exe",
        "https://ftp.mozilla.org/pub/firefox/releases/0.8/Firefox-0.8.zip",
        "https://ftp.mozilla.org/pub/firefox/releases/0.8/firefox-source-0.8.tar.bz2",
        "https://ftp.mozilla.org/pub/firefox/releases/1.0.6/win32/cs-CZ/Firefox%20Setup%201.0.6.exe",
    ]
    _download_many(file_list, os.path.join(tmp_dir, "dload-multi"), max_threads=10)

    _run_step("git_clone", lambda: dload.git_clone("https://github.com/x011/dload.git"))


if __name__ == "__main__":
    main()
