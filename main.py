#!/usr/bin/env python3
"""
Smart Music Tagger - Main Entry Point (CLI)

AI-powered music file metadata cleaning and organization.
Analyzes filenames, extracts metadata, updates tags, and renames files.

This is a thin CLI wrapper: configuration is read from ``.env``, then handed
to the shared ``TaggerService`` which owns all business logic. The same
service can later be driven by a Flask GUI with form-provided config.
"""

import sys
import io
import os

# Windows UTF-8 Console Encoding Fix
# Must be done BEFORE any other imports to ensure Rich and other libraries
# can properly output Unicode characters (box drawing, symbols, emojis)
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import ConfigLoader
from core import TaggerService
from cli import CLIInterface
from logs import Logger


def _run_cli():
    """Load config from .env, run the tagging pipeline, and print results."""
    cli = CLIInterface()
    cli.print_header()

    cli.print_info("Loading configuration from .env file...")
    config = ConfigLoader()
    config.validate()

    music_dir = config.get('music_directory')
    logger = Logger()

    cli.print_info("Initializing Groq API client...")
    service = TaggerService(
        api_key=config.get('groq_api_key'),
        api_url=config.get('groq_api_url'),
        model=config.get('groq_model'),
        request_delay_seconds=float(config.get('groq_request_delay_seconds', 3)),
        music_directory=music_dir,
        logger=logger,
    )

    cli.print_info(f"Scanning directory: {music_dir}")
    _, file_count = service.scan()

    if file_count == 0:
        cli.print_warning("No audio files found in the specified directory")
        return

    cli.print_config_info(music_dir, file_count)

    # Bridge service progress events to CLI output.
    def on_progress(index, total, result, new_filename):
        cli.print_processing_start(result['filename'], index, total)
        cli.print_processing_result(result, new_filename)

    summary = service.process_all(on_progress=on_progress)

    cli.print_summary(summary['total'], summary['successful'], summary['failed'])
    if summary.get('log_file'):
        cli.print_info(f"Log file saved to: {summary['log_file']}")


def main():
    """Main application entry point."""
    try:
        _run_cli()
    except FileNotFoundError as e:
        print("\n" + "="*60, file=sys.stderr)
        print("ERROR: Configuration file not found", file=sys.stderr)
        print("="*60, file=sys.stderr)
        print(str(e), file=sys.stderr)
        print("\nQuick setup:", file=sys.stderr)
        print("  1. Copy configuration template:", file=sys.stderr)
        print("     cp .env.example .env", file=sys.stderr)
        print("  2. Edit .env with your settings:", file=sys.stderr)
        print("     - GROQ_API_KEY: your Groq API key", file=sys.stderr)
        print("     - GROQ_API_URL: Groq API endpoint", file=sys.stderr)
        print("     - GROQ_MODEL: Groq model name", file=sys.stderr)
        print("     - GROQ_REQUEST_DELAY_SECONDS: delay between Groq API requests", file=sys.stderr)
        print("     - MUSIC_DIRECTORY: path to your music folder", file=sys.stderr)
        print("  3. Run again:", file=sys.stderr)
        print("     python main.py", file=sys.stderr)
        print("="*60, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
