"""Collection of CLI programs."""

import argparse
from pathlib import Path

import vidmux.srt_tools as srt_tools
from vidmux.video_library_scan import scan_mode


def get_scan_library_parser(
    subparsers: argparse._SubParsersAction | None = None,
    prog: str | None = None,
    formatter_class: type | None = None,
) -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for 'scan'.

    This function can either add a subparser to an existing ArgumentParser
    (via `subparsers`) or create a standalone parser when called independently.
    Useful for modular CLI designs.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction, optional
        Subparsers object from the main parser to which this parser should be added.
        If None, a standalone ArgumentParser is created instead.
    prog : str, optional
        The program name used in standalone mode. Ignored if `subparsers` is provided.
    formatter_class : type, optional
        The formatter class to be used for argument help formatting. Defaults to
        argparse.ArgumentDefaultsHelpFormatter.

    Returns
    -------
    argparse.ArgumentParser
        The configured argument parser (necessary esp. for standalone mode).
    """
    parser_options = {
        "description": "Scan videos of a library, e.g. for audio and subtitle tracks.",
        "formatter_class": formatter_class or argparse.ArgumentDefaultsHelpFormatter,
    }
    if subparsers:
        parser = subparsers.add_parser(
            "scan", help=parser_options["description"], **parser_options
        )
    else:
        parser = argparse.ArgumentParser(prog=prog, **parser_options)

    parser.add_argument(
        "library",
        type=Path,
        help="Path to the video library directory.",
    )
    parser.add_argument(
        "--extensions",
        metavar="EXTENSION",
        nargs="+",
        default=[".mp4", ".mkv", ".avi", ".mov"],
        help="File extensions to include.",
    )
    parser.add_argument(
        "--print",
        dest="show",
        action="store_true",
        help="Print results to the console.",
    )
    parser.add_argument(
        "--json", metavar="FILE", type=Path, help="Path to output JSON file."
    )
    parser.add_argument(
        "--csv", metavar="FILE", type=Path, help="Path to output CSV file."
    )

    return parser


def get_srt_tool_parser(
    subparsers: argparse._SubParsersAction | None = None,
    prog: str | None = None,
    formatter_class: type | None = None,
) -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for 'srt-tools'.

    This function can either add a subparser to an existing ArgumentParser
    (via `subparsers`) or create a standalone parser when called independently.
    Useful for modular CLI designs.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction, optional
        Subparsers object from the main parser to which this parser should be added.
        If None, a standalone ArgumentParser is created instead.
    prog : str, optional
        The program name used in standalone mode. Ignored if `subparsers` is provided.
    formatter_class : type, optional
        The formatter class to be used for argument help formatting. Defaults to
        argparse.ArgumentDefaultsHelpFormatter.

    Returns
    -------
    argparse.ArgumentParser
        The configured argument parser (necessary esp. for standalone mode).
    """
    parser_options = {
        "description": "Shift timestamps of a SRT file.",
        "formatter_class": formatter_class or argparse.ArgumentDefaultsHelpFormatter,
    }
    if subparsers:
        parser = subparsers.add_parser(
            "srt-tools", help=parser_options["description"], **parser_options
        )
    else:
        parser = argparse.ArgumentParser(prog=prog, **parser_options)

    parser.add_argument("input_file", help="Original SRT file.")
    parser.add_argument(
        "-s",
        "--shift",
        metavar="SECONDS",
        type=float,
        required=True,
        help="Timeshift in seconds (e.g. 1.5 or -0.8).",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        dest="output_file",
        help="Output SRT file (if not provided: stdout or --inplace).",
    )
    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Overwrite original file (a backup will be created).",
    )
    parser.add_argument(
        "--show-count",
        action="store_true",
        help="Show number of changed timestamps.",
    )

    return parser


def main() -> None:
    """Run main CLI programm."""
    formatter_class = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(
        prog="vidmux",
        description="Inspect and modify video/audio/subtitle tracks using FFmpeg.",
        formatter_class=formatter_class,
    )
    subparsers = parser.add_subparsers(dest="feature")

    feature_parsers = (
        get_scan_library_parser,
        get_srt_tool_parser,
    )
    for feature_parser in feature_parsers:
        feature_parser(subparsers, formatter_class=formatter_class)

    args = parser.parse_args()
    match args.feature:
        case "scan":
            scan_mode(
                args.library,
                args.extensions,
                show=args.show,
                json_file=args.json,
                csv_file=args.csv,
            )
        case "srt-tools":
            srt_tools.process_file(
                args.input_file,
                args.shift,
                inplace=args.inplace,
                output_file=args.output_file,
                show_count=args.show_count,
            )
        case _:
            parser.print_help()
            parser.exit(message="Run again and specify a supported command.")
