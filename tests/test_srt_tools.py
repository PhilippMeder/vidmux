"""Tests for srt_tools."""

from pathlib import Path

import pytest

from vidmux import srt_tools
from vidmux.output import Output

TEST_DATA = [
    # Values: pytest.param(input_text, shift_seconds, target_text, change_count)
    pytest.param(
        # We also test the flexibility of the Regex search, one timestamp has ".TT"
        # instead of ",TTT" for milliseconds. Processing the text should correct this.
        (
            "1\n"
            "01:08:57,200 --> 01:08:59,900\n"
            "Some text...\n\n"
            "2\n"
            "01:09:59.00 --> 01:10:00,200\n"
            "Some other text...\n\n"
        ),
        0.9,
        (
            "1\n"
            "01:08:58,100 --> 01:09:00,800\n"
            "Some text...\n\n"
            "2\n"
            "01:09:59,900 --> 01:10:01,100\n"
            "Some other text...\n\n"
        ),
        2,
        id="full-srt",
    )
]


def test_timestamp_conversion() -> None:
    """Test the conversion from timestamps to milliseconds and vice versa."""
    org_timestamp = "01:08:57,200"
    org_milliseconds = 4137200

    assert (
        srt_tools.timestamp_to_milliseconds(*org_timestamp.replace(",", ":").split(":"))
        == org_milliseconds
    )
    assert srt_tools.timestamp_from_milliseconds(org_milliseconds) == org_timestamp

    # Also test timestamp formats that differ slightly
    org_timestamp = "1:08:57,200".replace(",", ":").split(":")
    assert srt_tools.timestamp_to_milliseconds(*org_timestamp) == org_milliseconds

    org_timestamp = "01:08:57,2".replace(",", ":").split(":")
    assert srt_tools.timestamp_to_milliseconds(*org_timestamp) == org_milliseconds


@pytest.mark.parametrize(
    "input_text, shift_seconds, expected_text, expected_count", TEST_DATA
)
def test_text_processing(
    input_text, shift_seconds, expected_text, expected_count
) -> None:
    """Test the correct shifting of all timestamps in a text."""
    shifted_text, count = srt_tools.process_text(input_text, shift_seconds)

    assert shifted_text == expected_text
    assert count == expected_count


def test_process_file_missing_file(tmp_path: Path, mock_output: Output) -> None:
    """Test process_file raises FileNotFoundError if file is missing."""
    missing = tmp_path / "no_file.txt"

    with pytest.raises(FileNotFoundError):
        srt_tools.process_file(missing, shift_seconds=10, output=mock_output)


@pytest.mark.parametrize(
    "input_text, shift_seconds, expected_text, _expected_count", TEST_DATA
)
def test_process_file_inplace(
    tmp_path: Path,
    mock_output: Output,
    input_text,
    shift_seconds,
    expected_text,
    _expected_count,
) -> None:
    """Test process_file inplace mode."""
    file = tmp_path / "input.txt"
    file.write_text(input_text, encoding="utf-8")

    srt_tools.process_file(
        file,
        shift_seconds=shift_seconds,
        output=mock_output,
        inplace=True,
        show_count=False,
    )

    # original file overwritten
    assert file.read_text() == expected_text

    # backup created
    backup = file.with_suffix(file.suffix + ".bak")
    assert backup.exists()
    assert backup.read_text(encoding="utf-8") == input_text


@pytest.mark.parametrize(
    "input_text, shift_seconds, expected_text, _expected_count", TEST_DATA
)
def test_process_file_output_file(
    tmp_path: Path,
    mock_output: Output,
    input_text,
    shift_seconds,
    expected_text,
    _expected_count,
) -> None:
    """Test process_file normal mode."""
    input_file = tmp_path / "input.srt"
    output_file = tmp_path / "output.srt"

    input_file.write_text(input_text, encoding="utf-8")

    srt_tools.process_file(
        input_file,
        shift_seconds=shift_seconds,
        output=mock_output,
        inplace=False,
        output_file=output_file,
        show_count=False,
    )

    assert input_file.read_text(encoding="utf-8") == input_text
    assert output_file.read_text(encoding="utf-8") == expected_text


@pytest.mark.parametrize(
    "input_text, shift_seconds, expected_text, _expected_count", TEST_DATA
)
def test_process_file_stdout(
    tmp_path: Path,
    mock_output: Output,
    input_text,
    shift_seconds,
    expected_text,
    _expected_count,
) -> None:
    """Test process_file dry run mode."""
    file = tmp_path / "input.srt"
    file.write_text(input_text, encoding="utf-8")

    srt_tools.process_file(
        file,
        shift_seconds=shift_seconds,
        output=mock_output,
        inplace=False,
        output_file=None,
        show_count=False,
    )

    mock_output.success.assert_called()
    calls = [call.args[0] for call in mock_output.success.call_args_list]
    assert any(expected_text in text for text in calls)


MODES = [
    pytest.param(
        {"inplace": True, "output_file": None},
        id="inplace",
    ),
    pytest.param(
        {"inplace": False, "output_file": "output.srt"},
        id="output-file",
    ),
    pytest.param(
        {"inplace": False, "output_file": None},
        id="stdout",
    ),
]


@pytest.mark.parametrize(
    "input_text, shift_seconds, _expected_text, expected_count", TEST_DATA
)
@pytest.mark.parametrize("mode_kwargs", MODES)
def test_process_file_show_count(
    tmp_path: Path,
    mock_output: Output,
    input_text,
    shift_seconds,
    _expected_text,
    expected_count,
    mode_kwargs,
) -> None:
    """Test process_file show_count option."""
    file = tmp_path / "input.srt"
    file.write_text(input_text, encoding="utf-8")

    if mode_kwargs["output_file"]:
        mode_kwargs["output_file"] = tmp_path / mode_kwargs["output_file"]

    srt_tools.process_file(
        file,
        shift_seconds=shift_seconds,
        output=mock_output,
        show_count=True,
        **mode_kwargs,
    )

    expected_text = f"changed timestamps: {expected_count}"

    mock_output.success.assert_called()
    calls = [call.args[0] for call in mock_output.success.call_args_list]
    assert any(expected_text in text.lower() for text in calls)
