"""Provide CLI output."""

import os
import sys
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import Protocol, TextIO


class CliStyle(StrEnum):
    """Provide CLI styles using ANSI escape codes."""

    RESET = "\033[0m"

    INFO = "\033[0m"  # or cyan: "\033[36m"
    VERBOSE = "\033[2m"  # dim
    SUCCESS = "\033[32m"  # green
    WARNING = "\033[33m"  # yellow
    ERROR = "\033[31;1m"  # bold red
    DEBUG = "\033[90m"  # grey
    COMMAND = "\033[35m"  # magenta


class Verbosity(IntEnum):
    """Output verbosity levels."""

    QUIET = 0
    NORMAL = 1
    VERBOSE = 2
    DEBUG = 3


class Output(Protocol):
    """Protocol for CLI output handlers."""

    def info(self, message: str) -> None:
        """Show an informational message."""
        ...

    def success(self, message: str) -> None:
        """Show a success message."""
        ...

    def warning(self, message: str) -> None:
        """Show a warning message."""
        ...

    def error(self, message: str) -> None:
        """Show an error message."""
        ...

    def verbose(self, message: str) -> None:
        """Show a verbose message."""
        ...

    def debug(self, message: str) -> None:
        """Show a debug message."""
        ...

    def command(self, command: str) -> None:
        """Show a shell command."""
        ...

    def separator(self, title: str | None = None) -> None:
        """Show a separator line."""
        ...

    def newline(self) -> None:
        """Show an empty line."""
        ...

    def exit(self, message: str, code: int = 1) -> None:
        """Show an error message and terminate the process."""
        ...


@dataclass(slots=True)
class CliOutput(Output):
    """
    Terminal output handler for CLI applications.

    This class centralizes all user-facing CLI output and keeps it
    separate from business logic.

    Parameters
    ----------
    verbosity : Verbosity, default=Verbosity.NORMAL
        Controls which messages are shown.

    dry_run : bool, default=False
        Whether the application is running in dry-run mode.

        This flag only affects presentation and messaging.
        It does not enforce dry-run behavior.

    use_colors : bool, default=True
        Whether ANSI terminal colors should be enabled.

    separator_width : int, default=60
        Width of the separator line in characters.
    """

    verbosity: Verbosity = Verbosity.NORMAL
    dry_run: bool = False
    use_colors: bool = True
    separator_width: int = 60

    def __post_init__(self) -> None:
        """Ensure configuration makes sense."""
        if self.use_colors:
            self.use_colors = sys.stdout.isatty() and os.getenv("NO_COLOR") is None

    def info(self, message: str) -> None:
        """
        Show an informational message.

        Parameters
        ----------
        message : str
            Message shown to the user.
        """
        self._write(message, style=CliStyle.INFO, verbosity=Verbosity.NORMAL)

    def success(self, message: str) -> None:
        """
        Show a success message.

        Parameters
        ----------
        message : str
            Message shown to the user.
        """
        self._write(message, style=CliStyle.SUCCESS, verbosity=Verbosity.NORMAL)

    def warning(self, message: str) -> None:
        """
        Show a warning message.

        Parameters
        ----------
        message : str
            Warning shown to the user.
        """
        self._write(
            f"WARNING: {message}",
            style=CliStyle.WARNING,
            stderr=True,
            verbosity=Verbosity.NORMAL,
        )

    def error(self, message: str) -> None:
        """
        Show an error message.

        Parameters
        ----------
        message : str
            Error shown to the user.
        """
        self._write(f"ERROR: {message}", style=CliStyle.ERROR, stderr=True)

    def verbose(self, message: str) -> None:
        """
        Show a verbose message.

        Parameters
        ----------
        message : str
            Verbose message shown to the user.
        """
        self._write(message, style=CliStyle.VERBOSE, verbosity=Verbosity.VERBOSE)

    def debug(self, message: str) -> None:
        """
        Show a debug message.

        Parameters
        ----------
        message : str
            Debug message shown to the user.
        """
        self._write(message, style=CliStyle.DEBUG, verbosity=Verbosity.DEBUG)

    def command(self, command: str) -> None:
        """
        Show a shell command.

        Parameters
        ----------
        command : str
            Command string shown to the user.
        """
        prefix = "[DRY-RUN] " if self.dry_run else ""

        self._write(
            f"{prefix}$ {command}", style=CliStyle.COMMAND, verbosity=Verbosity.NORMAL
        )

    def separator(self, title: str | None = None) -> None:
        """
        Show a separator line.

        Parameters
        ----------
        title : str | None, default=None
            Optional separator title.
        """
        width = self.separator_width

        if title:
            text = f" {title} "
            padding = max(0, width - len(text))
            left = padding // 2
            right = padding - left
            line = f"{'-' * left}{text}{'-' * right}"
        else:
            line = "-" * width

        self._write(line)

    def newline(self) -> None:
        """Show an empty line."""
        self._write("")

    def exit(self, message: str, code: int = 1) -> None:
        """
        Show an error message and terminate the process.

        Parameters
        ----------
        message : str
            Error shown before exiting.

        code : int, default=1
            Process exit code.
        """
        self.error(message)
        raise SystemExit(code)

    def _write(
        self,
        message: str,
        *,
        flush: bool = True,
        style: CliStyle | None = None,
        stderr: bool = False,
        verbosity: Verbosity | None = None,
    ) -> None:
        """
        Provide internal print helper.

        Parameters
        ----------
        message : str
            Message to print.

        flush : bool, default=True
            Whether to flush the output.

        style : CliStyle | None, default=None
            Color/style key.

        stderr : bool, default=False
            Whether to print to stderr.

        verbosity: Verbosity | None, default=None
            Verbosity threshold level to show the message.
        """
        if verbosity is not None and self.verbosity < verbosity:
            return

        stream: TextIO = sys.stderr if stderr else sys.stdout

        if self.use_colors and style:
            message = f"{style.value}{message}{CliStyle.RESET}"

        print(message, file=stream, flush=flush)
