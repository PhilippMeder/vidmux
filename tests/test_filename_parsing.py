"""Provide tests for parsing media information from filenames."""

import pytest

from vidmux.media import Episode, FilenameParser, Movie


@pytest.fixture
def parser() -> FilenameParser:
    """Provide the filename parser."""
    return FilenameParser()


@pytest.mark.parametrize(
    "filename, expected",
    [
        (
            "Example Movie",
            dict(
                title="Example Movie",
                year=None,
                metadata_provider_id=None,
                part=None,
                version=None,
                version_tokens=[],
            ),
        ),
        (
            "Example Movie (2000)",
            dict(
                title="Example Movie",
                year=2000,
                metadata_provider_id=None,
                part=None,
                version=None,
                version_tokens=[],
            ),
        ),
        (
            "Example Movie (2000) [tmdb-12345]",
            dict(
                title="Example Movie",
                year=2000,
                metadata_provider_id="tmdb-12345",
                part=None,
                version=None,
                version_tokens=[],
            ),
        ),
        (
            "Example Movie (2000) - [DE] [Extended Version]",
            dict(
                title="Example Movie",
                year=2000,
                metadata_provider_id=None,
                part=None,
                version="[DE] [Extended Version]",
                version_tokens=["DE", "Extended Version"],
            ),
        ),
        (
            "Example Movie (2000)-cd1",
            dict(
                title="Example Movie",
                year=2000,
                metadata_provider_id=None,
                part="cd1",
                version=None,
                version_tokens=[],
            ),
        ),
        (
            "Example Movie (2000)-part-1",
            dict(
                title="Example Movie",
                year=2000,
                metadata_provider_id=None,
                part="part1",
                version=None,
                version_tokens=[],
            ),
        ),
        (
            "Example Movie (2000)-disc.1",
            dict(
                title="Example Movie",
                year=2000,
                metadata_provider_id=None,
                part="disc1",
                version=None,
                version_tokens=[],
            ),
        ),
    ],
)
def test_movie_parsing(parser: FilenameParser, filename: str, expected: dict) -> None:
    """Test the parsing of a movie filename."""
    media = parser.parse(filename)

    assert isinstance(media, Movie)
    assert media.media_type == "movie"
    assert media.title == expected["title"]
    assert media.year == expected["year"]
    assert media.metadata_provider_id == expected["metadata_provider_id"]
    assert media.part == expected["part"]
    assert media.version == expected["version"]
    assert media.version_tokens == expected["version_tokens"]


@pytest.mark.parametrize(
    "filename, expected",
    [
        (
            "Example Show S01E01",
            dict(
                series="Example Show",
                title="Example Show",
                season=1,
                episode=1,
                episode_title=None,
                year=None,
                metadata_provider_id=None,
                version=None,
                version_tokens=[],
            ),
        ),
        (
            "Example Show (2000) S02E03 Example Episode",
            dict(
                series="Example Show",
                title="Example Show",
                season=2,
                episode=3,
                episode_title="Example Episode",
                year=2000,
                metadata_provider_id=None,
                version=None,
                version_tokens=[],
            ),
        ),
        (
            "Example Show (2000) [tvdb-999] S02E03 Example Episode - [EN] [1080p]",
            dict(
                series="Example Show",
                title="Example Show",
                season=2,
                episode=3,
                episode_title="Example Episode",
                year=2000,
                metadata_provider_id="tvdb-999",
                version="[EN] [1080p]",
                version_tokens=["EN", "1080p"],
            ),
        ),
    ],
)
def test_show_parsing(parser: FilenameParser, filename: str, expected: dict) -> None:
    """Test the parsing of a series episode filename."""
    media = parser.parse(filename)

    assert isinstance(media, Episode)
    assert media.media_type == "show"

    assert media.series == expected["series"]
    assert media.title == expected["title"]
    assert media.season == expected["season"]
    assert media.episode == expected["episode"]
    assert media.episode_title == expected["episode_title"]
    assert media.year == expected["year"]
    assert media.metadata_provider_id == expected["metadata_provider_id"]
    assert media.version == expected["version"]
    assert media.version_tokens == expected["version_tokens"]


@pytest.mark.parametrize(
    "raw, tokens, normalized",
    [
        (
            "DE [Extended Version]",
            ["DE", "Extended Version"],
            "[DE] [Extended Version]",
        ),
        (
            "[Director's Cut] 4K HDR",
            ["Director's Cut", "4K", "HDR"],
            "[Director's Cut] [4K] [HDR]",
        ),
        ("1080p EN", ["1080p", "EN"], "[1080p] [EN]"),
        ("[DE]", ["DE"], "[DE]"),
        (None, [], None),
    ],
)
def test_version_tokenization_and_normalization(
    parser: FilenameParser, raw: str, tokens: list[str], normalized: str
) -> None:
    """Test internal handling of versions, i.e. tokenization and normalization."""
    assert parser._tokenize_version(raw) == tokens
    assert parser._normalize_version(raw) == normalized
