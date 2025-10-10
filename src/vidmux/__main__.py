"""Main entry point for vidmux."""

from vidmux.cli import main as cli_mode


def main():
    """Entry point for "vidmux"and "python -m vidmux"."""
    cli_mode()


if __name__ == "__main__":
    main()
