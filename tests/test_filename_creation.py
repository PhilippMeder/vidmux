"""Provide tests for creating filenames from media information."""

import pytest

from vidmux.media import FilenameCreator


@pytest.fixture(scope="module")
def creator() -> FilenameCreator:
    """Provide the filename parser."""
    return FilenameCreator()


def test_movie_filename_creation(
    creator: FilenameCreator, movie_test_data: dict
) -> None:
    """Test the creation of a movie filename."""
    canonical_name = creator.create(movie_test_data["media"])

    assert canonical_name == movie_test_data["canonical"]


def test_episode_filename_creation(
    creator: FilenameCreator, episode_test_data: dict
) -> None:
    """Test the creation of a episode filename."""
    canonical_name = creator.create(episode_test_data["media"])

    assert canonical_name == episode_test_data["canonical"]
