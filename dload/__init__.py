"""
Download helpers for HTTP, FTP, and zip archives.

A python library to simplify download tasks while retaining compatibility
with Python 3.6.
"""

import io
import os
import re
import sys
import time
import zipfile
from cgi import parse_header
from contextlib import closing
from shutil import copyfileobj
from typing import Iterable, List, Optional
from urllib import request
from urllib.parse import unquote, urlparse

import requests

DEFAULT_TIMEOUT = 30


def check_installation(rv: str = "36") -> bool:
    """
    Validate that the current interpreter is compatible with this module.

    :param rv: Two-character version string, i.e. "36" for Python 3.6.
    :return: ``True`` if the interpreter meets the requirement, otherwise
        raises a ``RuntimeError``.
    """

    current_version = sys.version_info
    major, minor = int(rv[0]), int(rv[1])
    if current_version.major == major and current_version.minor >= minor:
        return True

    message = (
        f"[{sys.argv[0]}] - Error: Your Python interpreter must be {major}.{minor} "
        f"or greater (within major version {major})\n"
    )
    raise RuntimeError(message)


check_installation("36")


def _get_caller_dir(namespace: Optional[dict]) -> str:
    """Resolve a caller's directory, falling back to the current working directory."""

    if namespace:
        if "__file__" in namespace and namespace["__file__"]:
            return os.path.dirname(os.path.abspath(namespace["__file__"]))

        # ``_dh`` is set by IPython/Colab to track the current working directory.
        ipython_dirs = namespace.get("_dh")
        if isinstance(ipython_dirs, (list, tuple)) and ipython_dirs:
            first_dir = ipython_dirs[0]
            if isinstance(first_dir, str) and first_dir:
                return os.path.abspath(first_dir)

    return os.getcwd()


def _default_filename(url: str) -> str:
    filename = os.path.basename(urlparse(url).path)
    return filename if filename else f"dload{rand_fn()}"


def _get_caller_namespace() -> Optional[dict]:
    """Retrieve the calling frame's globals, skipping internal wrappers when needed."""

    try:
        caller_frame = sys._getframe(1)
        namespace = caller_frame.f_globals if caller_frame else None
        if (
            namespace
            and namespace.get("__name__") == __name__
            and sys._getframe(2) is not None
        ):
            namespace = sys._getframe(2).f_globals
        return namespace
    except ValueError:
        return None


def _header_filename(content_disposition: Optional[str]) -> str:
    """Extract and sanitize a filename from a Content-Disposition header."""

    if not content_disposition:
        return ""

    try:
        _, params = parse_header(content_disposition)
    except (ValueError, TypeError):
        return ""

    filename = params.get("filename*")
    if filename and "''" in filename:
        _, _, filename = filename.partition("''")
    if not filename:
        filename = params.get("filename")

    if not filename:
        return ""

    filename = unquote(filename.strip().strip("\"'"))
    return os.path.basename(filename)


def bytes(
    url: str,
    timeout: int = DEFAULT_TIMEOUT,
    raise_on_error: bool = True,
) -> bytes:
    """
    Return the remote file as bytes.

    :param url: URL to download.
    :param timeout: Optional request timeout in seconds.
    :param raise_on_error: If ``True`` re-raises download errors; otherwise returns
        ``b""`` on failure.
    :return: Raw response content, or ``b""`` on failure when ``raise_on_error`` is
        ``False``.
    """

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.content
    except (requests.RequestException, ValueError):
        if raise_on_error:
            raise
        return b""


def rand_fn() -> str:
    """
    Provide a random filename when it's impossible to determine one from the URL.
    """

    return str(int(time.time()))[:5]


def save(
    url: str,
    path: str = "",
    overwrite: bool = False,
    timeout: int = DEFAULT_TIMEOUT,
    chunk_size: int = 8192,
    raise_on_error: bool = True,
) -> str:
    """
    Download and save a remote file.

    :param url: File URL to download.
    :param path: Full path to save the file. Defaults to the caller directory and
        the URL filename.
    :param overwrite: If ``True`` the local file will be overwritten; ``False``
        will skip the download if the file already exists.
    :param timeout: Optional request timeout in seconds.
    :param chunk_size: Optional size (in bytes) of streaming chunks written to disk.
    :param raise_on_error: If ``True`` re-raises download errors instead of returning
        an empty string.
    :return: The full path of the downloaded file or an empty string when
        ``raise_on_error`` is ``False``.
    """

    try:
        namespace = _get_caller_namespace()
        base_path = _get_caller_dir(namespace)
        provided_path = path.strip()
        destination: Optional[str] = None

        if provided_path:
            destination = os.path.abspath(os.path.expanduser(provided_path))
            if not overwrite and os.path.isfile(destination):
                return destination

        with requests.get(url, stream=True, timeout=timeout) as response:
            response.raise_for_status()

            if not destination:
                header_filename = _header_filename(
                    response.headers.get("content-disposition")
                )
                filename = header_filename or _default_filename(url)
                destination = os.path.abspath(os.path.join(base_path, filename))
                if not overwrite and os.path.isfile(destination):
                    return destination

            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with open(destination, "wb") as file_handle:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file_handle.write(chunk)
        return destination
    except (OSError, requests.RequestException, ValueError):
        if raise_on_error:
            raise
        return ""


def text(
    url: str,
    encoding: str = "",
    timeout: int = DEFAULT_TIMEOUT,
    raise_on_error: bool = True,
) -> str:
    """
    Return the remote file content as a string.

    :param url: URL to retrieve.
    :param encoding: Optional character encoding.
    :param timeout: Optional request timeout in seconds.
    :param raise_on_error: If ``True`` re-raises download errors; otherwise returns
        an empty string on failure.
    :return: Response text or an empty string on failure when ``raise_on_error`` is
        ``False``.
    """

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        if encoding:
            response.encoding = encoding
        return response.text
    except (requests.RequestException, ValueError):
        if raise_on_error:
            raise
        return ""


def json(url: str, timeout: int = DEFAULT_TIMEOUT, raise_on_error: bool = True):
    """
    Return the remote file as a dictionary.

    :param url: URL to retrieve the JSON content.
    :param timeout: Optional request timeout in seconds.
    :param raise_on_error: If ``True`` re-raises download or parse errors; otherwise
        returns an empty ``dict`` on failure.
    :return: Parsed JSON data or an empty ``dict`` on failure when
        ``raise_on_error`` is ``False``.
    """

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        if raise_on_error:
            raise
        return {}


def headers(
    url: str,
    redirect: bool = True,
    timeout: int = DEFAULT_TIMEOUT,
    raise_on_error: bool = True,
) -> dict:
    """
    Return the reply headers as a dictionary.

    :param url: URL to retrieve the reply headers.
    :param redirect: Should redirects be followed.
    :param timeout: Optional request timeout in seconds.
    :param raise_on_error: If ``True`` re-raises download errors; otherwise returns an
        empty ``dict`` on failure.
    """

    try:
        response = requests.head(url, allow_redirects=redirect, timeout=timeout)
        response.raise_for_status()
        return dict(response.headers)
    except (requests.RequestException, ValueError):
        if raise_on_error:
            raise
        return {}


def ftp(
    ftp_url: str,
    local_path: str = "",
    overwrite: bool = False,
    timeout: int = DEFAULT_TIMEOUT,
    raise_on_error: bool = True,
) -> str:
    """
    Download and save an FTP file.

    :param ftp_url: ``ftp://`` URL, optionally including credentials.
    :param local_path: Local path to save the file.
    :param overwrite: If ``True`` the local file will be overwritten; ``False``
        will skip the download if the file already exists.
    :param timeout: Optional request timeout in seconds.
    :param raise_on_error: If ``True`` re-raises download errors; otherwise returns
        ``""`` on failure.
    :return: Local path of the downloaded file or ``""`` on failure when
        ``raise_on_error`` is ``False``.
    """

    try:
        namespace = sys._getframe(1).f_globals if sys._getframe(1) else None
        base_path = _get_caller_dir(namespace)
        filename = _default_filename(ftp_url)
        destination = local_path.strip() or os.path.join(base_path, filename)
        destination = os.path.abspath(os.path.expanduser(destination))

        if not overwrite and os.path.isfile(destination):
            return destination

        with closing(request.urlopen(ftp_url, timeout=timeout)) as response:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with open(destination, "wb") as file_handle:
                copyfileobj(response, file_handle)
        return destination
    except (OSError, ValueError, request.URLError):
        if raise_on_error:
            raise
        return ""


def save_multi(
    url_list: Iterable[str],
    dir: str = "",
    max_threads: int = 1,
    tsleep: float = 0.05,
    timeout: int = DEFAULT_TIMEOUT,
    raise_on_error: bool = True,
) -> bool:
    """
    Multi-threaded file downloader.

    :param url_list: List of URLs or path to a text file containing URLs.
    :param dir: Directory to save the files; will be created if it does not exist.
    :param max_threads: Maximum number of parallel downloads.
    :param tsleep: Time (seconds) to wait between thread scheduling attempts.
    :param timeout: Optional request timeout in seconds.
    :param raise_on_error: If ``True`` re-raises the first encountered download error;
        otherwise returns ``False`` when any download fails.
    :return: ``True`` when all downloads finish, otherwise ``False`` when
        ``raise_on_error`` is ``False``.
    """

    import threading
    from time import sleep

    try:
        urls: List[str]
        if isinstance(url_list, str):
            with open(url_list) as file_handle:
                urls = [line.rstrip() for line in file_handle if line.strip()]
        else:
            urls = list(url_list)

        destination_dir = os.path.abspath(os.path.expanduser(dir)) if dir else ""
        if destination_dir and not os.path.exists(destination_dir):
            from pathlib import Path

            Path(destination_dir).mkdir(parents=True, exist_ok=True)

        semaphore = threading.Semaphore(max_threads if max_threads > 0 else 1)
        threads: List[threading.Thread] = []

        exceptions: List[BaseException] = []
        exception_lock = threading.Lock()

        def _download(target_url: str, destination_path: str) -> None:
            try:
                save(
                    target_url,
                    destination_path,
                    timeout=timeout,
                    overwrite=False,
                    raise_on_error=raise_on_error,
                )
            except BaseException as error:  # noqa: BLE001
                with exception_lock:
                    exceptions.append(error)
            finally:
                semaphore.release()

        for url in urls:
            if destination_dir:
                filename = _default_filename(url)
                download_path = os.path.join(destination_dir, filename)
            else:
                download_path = ""

            semaphore.acquire()
            thread = threading.Thread(
                target=_download, args=(url, download_path), name="dload", daemon=True
            )
            threads.append(thread)
            thread.start()
            sleep(tsleep)

        for thread in threads:
            thread.join()

        if exceptions:
            if raise_on_error:
                raise exceptions[0]
            return False

        return True
    except (OSError, ValueError) as error:
        if raise_on_error:
            raise
        return False


def down_speed(
    size: int = 5,
    ipv: str = "ipv4",
    port: int = 80,
    raise_on_error: bool = True,
) -> bool:
    """
    Measure download speed by retrieving a test file.

    :param size: Integer in megabytes (5, 10, 20, 50, 100, 200, 512, 1024).
    :param ipv: "ipv4" or "ipv6" host prefix.
    :param port: Port to use for the test URL.
    :param raise_on_error: If ``True`` re-raises download errors; otherwise returns
        ``False`` on failure.
    :return: ``True`` when the test completes, otherwise ``False`` when
        ``raise_on_error`` is ``False``.
    """

    if size == 1024:
        remote_size = "1GB"
    else:
        remote_size = f"{size}MB"

    url = f"http://{ipv}.download.thinkbroadband.com:{port}/{remote_size}.zip"

    try:
        with io.BytesIO() as buffer:
            start = time.perf_counter()
            response = requests.get(url, stream=True, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            total_length = response.headers.get("content-length")
            downloaded = 0

            if total_length is None:
                buffer.write(response.content)
            else:
                for chunk in response.iter_content(1024):
                    downloaded += len(chunk)
                    buffer.write(chunk)
                    if total_length.isdigit():
                        done = int(30 * downloaded / int(total_length))
                        elapsed = time.perf_counter() - start
                        if elapsed > 0:
                            speed = downloaded / elapsed / 100000
                            sys.stdout.write(
                                "\r[%s%s] %s Mbps" % ("=" * done, " " * (30 - done), speed)
                            )

            elapsed = time.perf_counter() - start
            print(f"\n{remote_size} = {elapsed:.2f} seconds")
        return True
    except (requests.RequestException, ValueError):
        if raise_on_error:
            raise
        return False


def save_unzip(
    zip_url: str,
    extract_path: str = "",
    delete_after: bool = False,
    raise_on_error: bool = True,
) -> str:
    """
    Save and extract a remote zip archive.

    :param zip_url: URL of the zip file to download.
    :param extract_path: Path to extract the zip file; defaults to the caller directory.
    :param delete_after: Delete the downloaded zip file after extraction.
    :param raise_on_error: If ``True`` re-raises download or extraction errors;
        otherwise returns an empty string on failure.
    :return: The extraction path or an empty string on failure when
        ``raise_on_error`` is ``False``.
    """

    try:
        namespace = sys._getframe(1).f_globals if sys._getframe(1) else None
        base_path = _get_caller_dir(namespace)
        zip_path = save(zip_url, overwrite=True, raise_on_error=raise_on_error)
        if not zip_path:
            return ""

        folder = os.path.splitext(os.path.basename(zip_path))[0]
        destination = extract_path.strip() or os.path.join(base_path, folder)
        destination = os.path.abspath(os.path.expanduser(destination))

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(destination)

        if delete_after and os.path.isfile(zip_path):
            os.remove(zip_path)
        return destination
    except (zipfile.BadZipFile, OSError, ValueError):
        if raise_on_error:
            raise
        return ""


def git_clone(
    git_url: str,
    clone_dir: str = "",
    raise_on_error: bool = True,
) -> str:
    """
    Clone a git repository by downloading its default branch zip archive.

    :param git_url: Git URL, e.g. ``https://github.com/x011/dload.git``.
    :param clone_dir: Local directory to extract into; defaults to the caller directory
        plus the repository name.
    :param raise_on_error: If ``True`` re-raises download or extraction errors;
        otherwise returns an empty string on failure.
    :return: Path to the local repository directory or an empty string on failure when
        ``raise_on_error`` is ``False``.
    """

    git_url = git_url.strip()
    if not git_url.lower().endswith(".git"):
        if raise_on_error:
            raise ValueError("git_url must end with .git")
        return ""

    try:
        repo_name = re.sub(r"\.git$", "", git_url, 0, re.IGNORECASE | re.MULTILINE)
        default_branch = _github_default_branch(repo_name, raise_on_error=raise_on_error) or "master"
        repo_zip = f"{repo_name}/archive/refs/heads/{default_branch}.zip"
        archive_filename = os.path.basename(urlparse(repo_zip).path)

        if not clone_dir:
            namespace = sys._getframe(1).f_globals if sys._getframe(1) else None
            caller_dir = _get_caller_dir(namespace)
            repo_folder = repo_name.split("/")[-1]
            clone_dir = os.path.join(caller_dir, repo_folder)
        else:
            if not re.search(r"/|\\$", clone_dir, re.IGNORECASE | re.MULTILINE):
                return ""

        if archive_filename and os.path.isfile(archive_filename):
            os.remove(archive_filename)

        return save_unzip(
            repo_zip, clone_dir, delete_after=True, raise_on_error=raise_on_error
        )
    except (OSError, ValueError):
        if raise_on_error:
            raise
        return ""


def _github_default_branch(
    repo_name: str, raise_on_error: bool = True
) -> Optional[str]:
    """Return the default branch name for a GitHub repository when possible."""

    parsed_url = urlparse(repo_name)
    if parsed_url.netloc.lower() != "github.com":
        return None

    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) < 2:
        return None

    repo_path = "/".join(path_parts[:2])
    api_url = f"https://api.github.com/repos/{repo_path}"

    try:
        response = requests.get(api_url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            default_branch = data.get("default_branch")
            if isinstance(default_branch, str) and default_branch.strip():
                return default_branch.strip()
    except requests.RequestException:
        if raise_on_error:
            raise
        return None

    return None
