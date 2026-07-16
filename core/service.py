"""Reusable orchestration service for tagging music files.

This module is the single entry point shared by both the CLI and a future
GUI (e.g. Flask). It takes all configuration as constructor parameters, so
it does not read ``.env`` or any global state — a GUI can pass form-provided
values directly, and the CLI passes values loaded from ``.env``.

The processing pipeline is reported through an optional ``on_progress``
callback so any frontend (terminal, web UI, SSE stream) can observe progress
without this module knowing about presentation.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from ai import GroqClient
from logs import Logger

from .processor import FileProcessor
from .renamer import FileRenamer
from .scanner import FileScanner

# Progress callback signature: (index, total, result, new_filename)
ProgressCallback = Callable[[int, int, Dict[str, Any], str], None]


class TaggerService:
    """Orchestrate the full tagging pipeline: scan → analyze → write → rename → log."""

    def __init__(
        self,
        api_key: str,
        api_url: str,
        model: str,
        request_delay_seconds: float,
        music_directory: str,
        logger: Optional[Logger] = None,
    ):
        """Initialize the service with explicit configuration.

        Args:
            api_key: Groq API key
            api_url: Groq API base URL
            model: Groq model name to use
            request_delay_seconds: Minimum delay between Groq API requests
            music_directory: Directory containing audio files to process
            logger: Optional Logger instance; if omitted, no log file is written.
                The CLI passes one; a GUI may pass one or omit it.
        """
        self.music_directory = music_directory
        self.logger = logger

        ai_client = GroqClient(
            api_key=api_key,
            api_url=api_url,
            model=model,
            request_delay_seconds=request_delay_seconds,
        )

        self.scanner = FileScanner(music_directory)
        self.processor = FileProcessor(ai_client)

    def scan(self) -> Tuple[List[str], int]:
        """Scan the music directory for supported audio files.

        Returns:
            Tuple of (list of absolute file paths, count).
        """
        audio_files = self.scanner.scan()
        return audio_files, len(audio_files)

    def process_all(self, on_progress: Optional[ProgressCallback] = None) -> Dict[str, Any]:
        """Process every audio file in the configured directory.

        For each file the pipeline runs: AI analysis → clear existing
        metadata → write clean metadata → rename → log. Progress is reported
        after each file through the optional ``on_progress`` callback.

        Args:
            on_progress: Optional callback invoked as
                ``on_progress(index, total, result, new_filename)`` after each
                file. Frontends use this to update their view.

        Returns:
            Summary dict: ``{total, successful, failed, success_rate, log_file}``.
        """
        audio_files, total = self.scan()
        successful = 0
        failed = 0

        for index, filepath in enumerate(audio_files, 1):
            original_filename = Path(filepath).name
            new_filename = original_filename
            result: Dict[str, Any] = {
                'filepath': filepath,
                'filename': original_filename,
                'success': False,
                'metadata': None,
                'errors': [],
            }

            try:
                result = self.processor.process_file(filepath)

                if result['success']:
                    metadata = result['metadata']
                    new_filepath = FileRenamer.rename_file(
                        filepath, metadata.artists, metadata.song_name
                    )
                    new_filename = Path(new_filepath).name
                    successful += 1

                    self._log(
                        original_filename=original_filename,
                        new_filename=new_filename,
                        metadata=metadata.to_dict(),
                        success=True,
                        errors=[],
                    )
                else:
                    failed += 1
                    self._log(
                        original_filename=original_filename,
                        new_filename=original_filename,
                        metadata=None,
                        success=False,
                        errors=result['errors'],
                    )

            except Exception as error:
                error_msg = str(error)
                result = {
                    'filepath': filepath,
                    'filename': original_filename,
                    'success': False,
                    'metadata': None,
                    'errors': [error_msg],
                }
                failed += 1
                self._log(
                    original_filename=original_filename,
                    new_filename=original_filename,
                    metadata=None,
                    success=False,
                    errors=[error_msg],
                )

            if on_progress is not None:
                on_progress(index, total, result, new_filename)

        summary = {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total else 0.0,
            'log_file': self.logger.get_log_file_path() if self.logger else None,
        }

        if self.logger is not None:
            self.logger.log_summary(total, successful, failed)

        return summary

    def _log(self, original_filename: str, new_filename: str,
             metadata: Optional[Dict[str, Any]], success: bool, errors: List[str]) -> None:
        """Write a log entry if a logger is configured."""
        if self.logger is None:
            return
        self.logger.log_file_processing(
            original_filename=original_filename,
            new_filename=new_filename,
            metadata=metadata,
            success=success,
            errors=errors,
        )
