"""Module to check the library structure."""

from vidmux.library_structure.core import (
    IssueCode,
    Severity,
    ValidationIssue,
    registry,
    run_validation,
)
from vidmux.library_structure.structure_scan import scan_library_structure


def load_default_rules() -> None:
    """Load and register the default rules."""
    from vidmux.library_structure import rules  # noqa: F401, PLC0415


__all__ = [
    "IssueCode",
    "Severity",
    "ValidationIssue",
    "load_default_rules",
    "registry",
    "run_validation",
    "scan_library_structure",
]
