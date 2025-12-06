from unittest import TestCase, mock

import dload


class RaiseOnErrorTests(TestCase):
    def test_bytes_raises_by_default(self):
        with mock.patch("dload.requests.get", side_effect=dload.requests.RequestException):
            with self.assertRaises(dload.requests.RequestException):
                dload.bytes("http://example.com")

    def test_bytes_suppresses_when_disabled(self):
        with mock.patch("dload.requests.get", side_effect=dload.requests.RequestException):
            self.assertEqual(b"", dload.bytes("http://example.com", raise_on_error=False))

    def test_save_multi_propagates_first_error(self):
        with mock.patch("dload.save", side_effect=ValueError("boom")):
            with self.assertRaises(ValueError):
                dload.save_multi(["http://example.com/file.bin"], raise_on_error=True)

    def test_save_multi_suppresses_errors_when_disabled(self):
        with mock.patch("dload.save", side_effect=ValueError("boom")):
            result = dload.save_multi(["http://example.com/file.bin"], raise_on_error=False)
        self.assertFalse(result)

    def test_git_clone_raises_on_invalid_url(self):
        with self.assertRaises(ValueError):
            dload.git_clone("not-a-git-url", raise_on_error=True)

    def test_git_clone_suppresses_when_disabled(self):
        self.assertEqual("", dload.git_clone("not-a-git-url", raise_on_error=False))
