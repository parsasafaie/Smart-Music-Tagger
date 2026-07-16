"""File scanner for music files."""

from pathlib import Path
from typing import List
from utils import get_audio_files_in_directory


class FileScanner:
    """Scan directories for music files."""

    def __init__(self, directory: str):
        """
        Initialize scanner.

        Args:
            directory: Directory path to scan
        """
        self.directory = directory

    def scan(self) -> List[str]:
        """
        Scan directory for audio files.

        Args:
            Returns list of absolute file paths
        """
        return get_audio_files_in_directory(self.directory)

    def get_stats(self) -> dict:
        """
        Get scan statistics.

        Returns:
            Dictionary with stats
        """
        files = self.scan()
        return {
            'total_files': len(files),
            'supported_formats': self._count_by_format(files),
        }

    @staticmethod
    def _count_by_format(files: List[str]) -> dict:
        """Count files by format."""
        counts = {}
        for file in files:
            ext = Path(file).suffix.lower()
            counts[ext] = counts.get(ext, 0) + 1
        return counts
