"""Provide tests for parsing media information from filenames."""

import pytest

from vidmux.media import FilenameParser


@pytest.fixture(scope="module")
def parser() -> FilenameParser:
    """Provide the filename parser."""
    return FilenameParser()


def test_movie_parsing(parser: FilenameParser, movie_test_data: dict) -> None:
    """Test the parsing of a movie filename."""
    media = parser.parse(movie_test_data["filename"])

    assert media == movie_test_data["media"]

    # Test __call__
    media_call = parser(movie_test_data["filename"])
    assert media_call == movie_test_data["media"]


def test_episode_parsing(parser: FilenameParser, episode_test_data: dict) -> None:
    """Test the parsing of a episode filename."""
    media = parser.parse(episode_test_data["filename"])

    assert media == episode_test_data["media"]


def test_unkown_parsing(parser: FilenameParser) -> None:
    """Test the parsing of a filename without proper structure."""
    # Currently the movie parser as a fallback catches everything else
    media = parser.parse("")

    assert media is None


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


@pytest.mark.parametrize(
    "input_part, expected",
    [
        # standard numeric cases
        ("cd1", "cd1"),
        ("CD1", "cd1"),
        ("dvd2", "dvd2"),
        ("part3", "part3"),
        ("pt4", "pt4"),
        ("disc5", "disc5"),
        ("disk6", "disk6"),
        # with separators
        ("cd-1", "cd1"),
        ("cd_1", "cd1"),
        ("cd.1", "cd1"),
        ("cd 1", "cd1"),
        # letter parts (a-d)
        ("cdA", "cdA"),
        ("ptb", "ptb"),
        ("discC", "discC"),
        ("disk-d", "diskd"),
        # mixed case + separator
        ("DVD-B", "dvdB"),
        ("Part_c", "partc"),
        # leading zeros
        ("cd01", "cd01"),
        # invalid patterns
        ("episode1", None),
        ("cda1", None),  # wrong structure
        ("random", None),
        ("cd", None),
        ("1cd", None),
        # None / empty
        (None, None),
        ("", None),
    ],
)
def test_part_normalization(
    parser: FilenameParser, input_part: str, expected: str
) -> None:
    """Test the part normalization."""
    assert parser._normalize_part(input_part) == expected
