"""Define the high-level API."""

import csv
import json
from pathlib import Path

from vidmux.library_structure import rules  # noqa: F401
from vidmux.library_structure.core import run_validation
from vidmux.output import Output


def save_json(results: list[dict], path: Path) -> None:
    """Save results to a JSON file."""
    with path.open(mode="w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)


def save_csv(results: list[dict], path: Path) -> None:
    """Save results to a CSV file."""
    with path.open(mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["filename", "type", "code", "description", "message"])
        for report in results:
            for issue in report["issues"]:
                writer.writerow(
                    [
                        issue["path"],
                        issue["severity"],
                        issue["code"],
                        issue["description"],
                        issue["message"],
                    ]
                )


def make_issue_string(issue: dict) -> str:
    """Convert an issue to a string."""
    return (
        f"[{issue['severity']}] {issue['code']} ({issue['description']}): "
        f"{issue['message']}"
    )


def print_to_terminal(results: list[dict], *, output: Output) -> None:
    """Print results to terminal."""
    issues = []

    for report in results:
        if report["issues"]:
            msg = f"Issues for {report['path']}:\n\t"
            msg = msg + "\n\t".join(
                make_issue_string(issue) for issue in report["issues"]
            )
            issues.append(msg)

    if not issues:
        output.success("Found no issues in the library")
        return

    output.warning("There are issues in the library:")
    for issue in issues:
        output.info(issue)  # TODO: Can be improved by using the issue severity


def scan_library_structure(
    library: Path,
    extensions: list[str],
    *,
    output: Output,
    show: bool = True,
    json_file: Path | None = None,
    csv_file: Path | None = None,
) -> bool:
    """Run the scan and save/show the output."""
    if not (show or json_file or csv_file):
        output.error("No output specified. Use --print, --json or --csv.")
        return False

    files = [file for file in library.rglob("*") if file.suffix.lower() in extensions]
    result = run_validation(files)

    if show:
        print_to_terminal(result, output=output)

    if json_file:
        save_json(result, json_file)
        output.success(f"Saved library structure scan results to JSON '{json_file}'")

    if csv_file:
        save_csv(result, csv_file)
        output.success(f"Saved library structure scan results to CSV '{csv_file}'")

    return True
