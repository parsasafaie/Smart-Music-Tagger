"""Logging system for Smart Music Tagger."""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class Logger:
    """Handle application logging."""

    def __init__(self, log_dir: str = "logs"):
        """
        Initialize logger.

        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"music_tagger_{timestamp}.log"

        self.entries: List[Dict[str, Any]] = []
        self._write_header()

    def _write_header(self):
        """Write log file header."""
        header = f"""
╔════════════════════════════════════════╗
║     SMART MUSIC TAGGER LOG             ║
║     Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}           ║
╚════════════════════════════════════════╝

"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(header)

    def log_file_processing(
        self,
        original_filename: str,
        new_filename: str,
        metadata: Dict[str, Any],
        success: bool,
        errors: List[str],
    ):
        """
        Log file processing result.

        Args:
            original_filename: Original filename
            new_filename: New filename
            metadata: Extracted metadata
            success: Whether processing was successful
            errors: List of errors if any
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'original_filename': original_filename,
            'new_filename': new_filename,
            'success': success,
            'metadata': metadata,
            'errors': errors,
        }

        self.entries.append(entry)
        self._append_to_file(entry)

    def _append_to_file(self, entry: Dict[str, Any]):
        """Append entry to log file."""
        log_text = f"""
────────────────────────────────────────
File: {entry['original_filename']}
Timestamp: {entry['timestamp']}
Status: {'✓ SUCCESS' if entry['success'] else '✗ FAILED'}

Original Filename:  {entry['original_filename']}
New Filename:       {entry['new_filename']}

Metadata:
  Artist: {', '.join(entry['metadata'].get('artists', ['Unknown'])) if entry['metadata'] else 'N/A'}
  Album: {entry['metadata'].get('album', 'N/A') if entry['metadata'] else 'N/A'}
  Genre: {entry['metadata'].get('genre', 'N/A') if entry['metadata'] else 'N/A'}
  Release Year: {entry['metadata'].get('release_year', 'N/A') if entry['metadata'] else 'N/A'}

"""
        if entry['errors']:
            log_text += "Errors:\n"
            for error in entry['errors']:
                log_text += f"  - {error}\n"

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_text)

    def log_summary(self, total: int, successful: int, failed: int):
        """
        Log processing summary.

        Args:
            total: Total files processed
            successful: Successfully processed files
            failed: Failed files
        """
        summary = f"""

╔════════════════════════════════════════╗
║     PROCESSING SUMMARY                 ║
╚════════════════════════════════════════╝

Total Files: {total}
Successful: {successful}
Failed: {failed}
Success Rate: {(successful/total*100):.1f}%

Completed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(summary)

    def get_log_file_path(self) -> str:
        """Get path to log file."""
        return str(self.log_file)
