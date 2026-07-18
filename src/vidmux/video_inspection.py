"""Tools for video inspection (format, streams, resolution, ...)."""

import json
import subprocess
from pathlib import Path
from typing import Any


def get_file_info(
    file_path: Path, stream_type: str | None = "all", include_format: bool = True
) -> dict[str, Any]:
    """
    Return the interesting ffprobe info of a file.

    stream_type:
        "all"  = all streams
        "a"    = audio only
        "v"    = video only
        "s"    = subtitles only
        "none" = no streams
    """
    if stream_type and stream_type not in ("all", "none", "a", "v", "s"):
        msg = "Invalid stream_type. Must be 'all', 'none', 'a', 'v' or 's'."
        raise ValueError(msg)

    # Create ffprobe command
    # TODO: Maybe use -show-entries to only read out interesting entries (speed!)
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
    ]
    if include_format:
        cmd.append("-show_format")
    if stream_type and stream_type != "none":
        cmd.append("-show_streams")
        if stream_type != "all":
            cmd.extend(["-select_streams", stream_type])
    cmd.append(str(file_path))

    # Run ffprobe
    # TODO: Better error handling
    # Safe: shell=False. Accepts arbitrary media paths/URLs by design
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)  # noqa: S603
    try:
        info = json.loads(result.stdout)
    except json.JSONDecodeError:
        # TODO: log warning
        info = {}

    return info


def get_format(file_path: Path) -> str:
    """Return the container format of a file (e.g., 'mov,mp4,m4a,3gp,3g2,mj2')."""
    info = get_file_info(file_path, stream_type="none", include_format=True)

    return info.get("format", {}).get("format_name", "")


def get_streams(file_path: Path, stream_type: str) -> list:
    """
    Extract media streams using ffprobe (ffmpeg).

    stream_type: "all" = All streams, "a" = Audio, "v" = Video, "s" = Subtitle
    """
    info = get_file_info(file_path, stream_type=stream_type, include_format=False)

    return info.get("streams", [])


def group_streams_by_types(streams: list[dict]) -> dict[str, list]:
    """Classify streams by their stream type."""
    grouped_streams = {"audio": [], "subtitle": [], "video": []}

    for stream in streams:
        match stream_type := stream.get("codec_type"):
            case "audio":
                grouped_streams["audio"].append(stream)
            case "subtitle":
                grouped_streams["subtitle"].append(stream)
            case "video":
                grouped_streams["video"].append(stream)
            case _:
                print(f"Unkown {stream_type=}")

    return grouped_streams


def get_all_tracks(file_path: Path) -> dict[str, list]:
    """Extract audio, subtitle and video tracks using ffprobe (ffmpeg)."""
    streams = get_streams(file_path, "all")

    return group_streams_by_types(streams)


def get_audio_tracks(file_path: Path) -> list:
    """Extract audio tracks using ffprobe (ffmpeg)."""
    return get_streams(file_path, "a")


def get_subtitles(file_path: Path) -> list:
    """Extract subtitles using ffprobe (ffmpeg)."""
    return get_streams(file_path, "s")


def get_video_tracks(file_path: Path) -> list:
    """Extract video tracks using ffprobe (ffmpeg)."""
    return get_streams(file_path, "v")


def get_video_resolution(path_or_url: str | Path) -> tuple[int, int] | None:
    """Get the video resolution for a file or URL."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=p=0:s=x",
        str(path_or_url),
    ]
    try:
        # Safe: shell=False. Accepting arbitrary file paths and URLs is the intended API
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()  # noqa: S603
        width, height = output.split("x")
        return int(width), int(height)
    except subprocess.CalledProcessError as err:
        print("ffprobe error:", err.output.decode())
        return None
