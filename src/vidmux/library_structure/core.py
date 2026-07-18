"""Define core features for the validation, esp. issues and validation results."""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from vidmux.media import (
    BaseMedia,
    CanonicalName,
    get_canonical_name,
    get_media_from_filename,
)


class Severity(Enum):
    """Provide severity."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IssueCode(Enum):
    """Provide issue types."""

    FILE_AND_FOLDER_NAME_DIFFER = "Filename differs from folder"
    FILE_NOT_IN_FOLDER = "File not in its own folder"
    FILE_PARSING_ERROR = "File could not be parsed according to the naming conventions"
    FILE_IN_WRONG_FOLDER = "File is in a wrong folder"
    BAD_CHARACTER_IN_NAME = "Invalid character in filename"
    MISSING_YEAR = "Missing year in title"


class ValidationFile:
    """Container holding the BaseMedia and CanonicalName objects for a path."""

    def __init__(self, filepath: Path) -> None:
        self.path: Path = filepath
        self.media: BaseMedia = get_media_from_filename(filepath.stem)
        self.canonical_name: CanonicalName = get_canonical_name(self.media)


@dataclass
class ValidationIssue:
    """Provide validation issues."""

    path: str
    code: IssueCode
    message: str
    severity: Severity

    def to_dict(self) -> dict:
        """Return a dictionary representation of the instance values."""
        return {
            "path": str(self.path),
            "severity": self.severity.name,
            "code": self.code.name,
            "description": self.code.value,
            "message": self.message,
        }


@dataclass
class CheckResult:
    """Provide check results."""

    path: Path
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_issue(
        self, code: IssueCode, message: str, severity: Severity = Severity.ERROR
    ) -> None:
        """Add an issue to the issue list."""
        self.issues.append(ValidationIssue(self.path, code, message, severity))

    def to_dict(self) -> dict:
        """Return a dictionary representation of the instance values."""
        return {
            "path": str(self.path),
            "issues": [issue.to_dict() for issue in self.issues],
        }


class Rule:
    """Single rule."""

    def __init__(
        self,
        name: str,
        func: Callable[[ValidationFile, dict[str, Any]], list[ValidationIssue]],
        default_enabled: bool = True,
        default_severity: Severity | None = None,
        default_params: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.func = func
        self.default_enabled = default_enabled
        self.default_severity = default_severity
        self.default_params = default_params or {}

    def run(
        self, file: ValidationFile, config: dict[str, Any]
    ) -> list[ValidationIssue]:
        """Run the check of the rule (if active)."""
        rule_config = config.get("rules", {}).get(self.name, {})
        enabled = rule_config.get("enabled", self.default_enabled)
        if not enabled:
            return []

        # Merge Parameters
        params = {**self.default_params, **rule_config.get("params", {})}
        severity_override = rule_config.get("severity", self.default_severity)

        issues = self.func(file, params)

        # Patch severity if necessary
        if severity_override:
            for issue in issues:
                issue.severity = severity_override

        return issues


class RuleRegistry:
    """Save registered rules for checking."""

    def __init__(self) -> None:
        self.rules: dict[str, Rule] = {}

    def register(
        self,
        name: str | None = None,
        default_enabled: bool = True,
        default_severity: Severity | None = None,
        default_params: dict[str, Any] | None = None,
    ) -> Callable:
        """Register a rule."""

        def decorator(func: Callable) -> Callable:
            """Allow decorator syntax to register rules."""
            rule_name = name or func.__name__
            self.rules[rule_name] = Rule(
                rule_name,
                func,
                default_enabled,
                default_severity,
                default_params,
            )

            return func

        return decorator

    def run_all(self, path: Path, config: dict[str, Any]) -> CheckResult:
        """Run a check of all registered rules."""
        try:
            validation_file = ValidationFile(path)
        # TODO: convert parser exceptions into ValidationFileError
        except Exception as err:  # noqa: BLE001 - parser failures are reported as validation issues
            return CheckResult(
                path,
                issues=[
                    ValidationIssue(
                        path,
                        code=IssueCode.FILE_PARSING_ERROR,
                        message=str(err),
                        severity=Severity.ERROR,
                    )
                ],
            )

        result = CheckResult(path)
        for rule in self.rules.values():
            for issue in rule.run(validation_file, config):
                result.issues.append(issue)

        return result


# Global registry instance
registry = RuleRegistry()


def run_validation(
    files: list[Path], config: dict[str, Any] | None = None
) -> list[dict]:
    """Return a check report list of dicts for a list of files."""
    config = config or {}
    results = []
    for file in files:
        result = registry.run_all(file, config)
        results.append(result.to_dict())

    return results
