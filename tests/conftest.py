"""Configuration and fixtures for pytest."""

import pytest
from unittest.mock import patch


@pytest.fixture
def ffmpeg_mock():
    """
    Fixture that patches subprocess.run to capture ffmpeg invocations.

    Usage:
        def test_something(ffmpeg_mock):
            my_function()
            ffmpeg_mock.assert_called_with(expected)
    """
    with patch("subprocess.run") as mock_run:
        yield FfmpegMock(mock_run)


class FfmpegMock:
    """Helper object returned by the ffmpeg_mock fixture."""

    def __init__(self, mock_run):
        self._mock = mock_run

    @property
    def args(self):
        """Return the list of arguments passed to ffmpeg."""
        return self._mock.call_args[0][0] if self._mock.call_args else None

    def assert_called_with(self, expected_args, *, check=True):
        """Assert ffmpeg was called exactly once with expected arguments."""
        self._mock.assert_called_once_with(expected_args, check=check)
        assert self.args == expected_args, (
            "FFmpeg command differs.\n\n"
            f"Expected:\n  {expected_args}\nGot:\n  {self.args}"
        )
