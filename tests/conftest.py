"""Configuration and fixtures for pytest."""

from typing import Generator

import pytest
from unittest.mock import patch

from vidmux.media import CanonicalName, Episode, Movie


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


@pytest.fixture(
    params=(
        {
            "id": "movie_bare",
            "filename": "Example Movie",
            "media": Movie(
                raw="Example Movie",
                title="Example Movie",
                version_tokens=[],
            ),
            "canonical": CanonicalName(
                filename="Example Movie",
                directory="Example Movie",
                version_tokens=[],
            ),
        },
        {
            "id": "movie_with_year",
            "filename": "Example Movie (2000)",
            "media": Movie(
                raw="Example Movie (2000)",
                title="Example Movie",
                year=2000,
                version_tokens=[],
            ),
            "canonical": CanonicalName(
                filename="Example Movie (2000)",
                directory="Example Movie (2000)",
                version_tokens=[],
            ),
        },
        {
            "id": "movie_with_provider",
            "filename": "Example Movie [tmdb-12345]",
            "media": Movie(
                raw="Example Movie [tmdb-12345]",
                title="Example Movie",
                metadata_provider_id="tmdb-12345",
                version_tokens=[],
            ),
            "canonical": CanonicalName(
                filename="Example Movie [tmdb-12345]",
                directory="Example Movie [tmdb-12345]",
                version_tokens=[],
            ),
        },
        {
            "id": "movie_with_year_and_provider",
            "filename": "Example Movie (2000) [tmdb-12345]",
            "media": Movie(
                raw="Example Movie (2000) [tmdb-12345]",
                title="Example Movie",
                year=2000,
                metadata_provider_id="tmdb-12345",
                version_tokens=[],
            ),
            "canonical": CanonicalName(
                filename="Example Movie (2000) [tmdb-12345]",
                directory="Example Movie (2000) [tmdb-12345]",
                version_tokens=[],
            ),
        },
        {
            "id": "movie_with_version",
            "filename": "Example Movie - [DE] [Extended Cut]",
            "media": Movie(
                raw="Example Movie - [DE] [Extended Cut]",
                title="Example Movie",
                version="[DE] [Extended Cut]",
                version_tokens=["DE", "Extended Cut"],
            ),
            "canonical": CanonicalName(
                filename="Example Movie - [DE] [Extended Cut]",
                directory="Example Movie",
                version_tokens=["DE", "Extended Cut"],
            ),
        },
        {
            "id": "movie_with_part",
            "filename": "Example Movie-part-1",
            "media": Movie(
                raw="Example Movie-part-1",
                title="Example Movie",
                part="part1",
                version_tokens=[],
            ),
            "canonical": CanonicalName(
                filename="Example Movie-part1",
                directory="Example Movie",
                version_tokens=[],
            ),
        },
    ),
    ids=lambda test_case: test_case["id"],
)
def movie_test_data(request) -> Generator[dict]:
    """Provide test data for movie filename parsing and creation."""
    yield request.param


@pytest.fixture(
    params=(
        {
            "id": "episode_bare",
            "filename": "Example Show S01E01",
            "media": Episode(
                raw="Example Show S01E01",
                title="Example Show",
                series="Example Show",
                season=1,
                episode=1,
                version_tokens=[],
            ),
            "canonical": CanonicalName(
                filename="Example Show S01E01",
                directory="Example Show/Season 01",
                version_tokens=[],
            ),
        },
        {
            "id": "episode_with_year",
            "filename": "Example Show (2000) S01E01",
            "media": Episode(
                raw="Example Show (2000) S01E01",
                title="Example Show",
                series="Example Show",
                year=2000,
                season=1,
                episode=1,
                version_tokens=[],
            ),
            "canonical": CanonicalName(
                filename="Example Show (2000) S01E01",
                directory="Example Show (2000)/Season 01",
                version_tokens=[],
            ),
        },
        {
            "id": "episode_with_provider",
            "filename": "Example Show [tvdb-999] S01E01",
            "media": Episode(
                raw="Example Show [tvdb-999] S01E01",
                title="Example Show",
                series="Example Show",
                metadata_provider_id="tvdb-999",
                season=1,
                episode=1,
                version_tokens=[],
            ),
            "canonical": CanonicalName(
                filename="Example Show [tvdb-999] S01E01",
                directory="Example Show [tvdb-999]/Season 01",
                version_tokens=[],
            ),
        },
        {
            "id": "episode_with_title",
            "filename": "Example Show S01E01 Episode Title",
            "media": Episode(
                raw="Example Show S01E01 Episode Title",
                title="Example Show",
                series="Example Show",
                season=1,
                episode=1,
                episode_title="Episode Title",
                version_tokens=[],
            ),
            "canonical": CanonicalName(
                filename="Example Show S01E01 Episode Title",
                directory="Example Show/Season 01",
                version_tokens=[],
            ),
        },
    ),
    ids=lambda test_case: test_case["id"],
)
def episode_test_data(request) -> Generator[dict]:
    """Provide test data for episode filename parsing and creation."""
    yield request.param
