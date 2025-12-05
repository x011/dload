import io
import os
import tempfile
import zipfile
from unittest import TestCase, mock

import dload


class DummyResponse:
    def __init__(self, content: bytes, headers=None):
        self._content = content
        self.headers = headers or {}

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size=8192):
        for index in range(0, len(self._content), chunk_size):
            yield self._content[index : index + chunk_size]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class SaveTests(TestCase):
    def test_save_prefers_content_disposition_filename(self):
        url = "http://example.com/download/file.bin"
        header_filename = "nested/header-name.txt"
        expected_name = os.path.basename(header_filename)
        response = DummyResponse(
            b"payload", {"content-disposition": f'attachment; filename="{header_filename}"'}
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            with mock.patch("dload._get_caller_dir", return_value=tmp_dir), mock.patch(
                "dload.requests.get", return_value=response
            ):
                saved_path = dload.save(url, overwrite=True)

            self.assertEqual(saved_path, os.path.join(tmp_dir, expected_name))
            with open(saved_path, "rb") as file_handle:
                self.assertEqual(file_handle.read(), b"payload")

    def test_save_unzip_uses_header_filename_for_destination(self):
        url = "http://example.com/download/archive.bin"
        header_filename = "header-archive.zip"
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr("file.txt", "content")
        response = DummyResponse(
            zip_buffer.getvalue(),
            {"content-disposition": f'attachment; filename="{header_filename}"'},
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            with mock.patch("dload._get_caller_dir", return_value=tmp_dir), mock.patch(
                "dload.requests.get", return_value=response
            ):
                extract_path = dload.save_unzip(url)

            expected_dir = os.path.join(tmp_dir, os.path.splitext(header_filename)[0])
            self.assertEqual(extract_path, expected_dir)
            self.assertTrue(os.path.isdir(extract_path))
            with open(os.path.join(extract_path, "file.txt")) as file_handle:
                self.assertEqual(file_handle.read(), "content")

    def test_save_uses_cwd_when_caller_has_no_file_namespace(self):
        url = "http://example.com/download/file.bin"
        response = DummyResponse(b"payload")

        with tempfile.TemporaryDirectory() as tmp_dir:
            with mock.patch("dload._get_caller_namespace", return_value={}), mock.patch(
                "dload.os.getcwd", return_value=tmp_dir
            ), mock.patch("dload.requests.get", return_value=response):
                saved_path = dload.save(url, overwrite=True)

            expected_path = os.path.join(tmp_dir, os.path.basename(url))
            self.assertEqual(saved_path, expected_path)
            with open(saved_path, "rb") as file_handle:
                self.assertEqual(file_handle.read(), b"payload")

    def test_get_caller_dir_prefers_ipython_working_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            namespace = {"_dh": [tmp_dir]}
            caller_dir = dload._get_caller_dir(namespace)
            self.assertEqual(caller_dir, tmp_dir)
