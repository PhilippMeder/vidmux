""" "Provide tests for the library scan."""

from pathlib import Path

import pytest

from vidmux.video_library_scan import suggest_name


@pytest.mark.parametrize(
    "report,expected_name",
    (
        (
            {
                "filename": "Example Movie (2000).mp4",
                "video_tracks": [{}],
                "audio_tracks": [{}],
            },
            "Example Movie (2000)/Example Movie (2000) - [EN].mp4",
        ),
        (
            {
                "filename": "Example Movie (2000)/Example Movie (2000) - Director's Cut [DE+EN].mp4",
                "video_tracks": [{"width": 1920, "height": 1080}],
                "audio_tracks": [{"language": "deu"}, {"language": "und"}],
            },
            "Example Movie (2000)/Example Movie (2000) - [Director's Cut] [DE+EN] [1080p].mp4",
        ),
    ),
)
def test_suggest_name(report: dict, expected_name: str) -> None:
    suggested_name = suggest_name(report, undefined_language="EN")

    assert suggested_name == expected_name
