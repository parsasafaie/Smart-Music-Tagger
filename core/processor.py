"""Main file processor."""

from pathlib import Path
from typing import Dict, Any

from ai import GroqClient, MusicMetadata
from metadata import MetadataWriter
from utils import extract_filename_without_extension


class FileProcessor:
    """Process music files: analyze, extract metadata, and update."""

    def __init__(self, ai_client: GroqClient):
        """
        Initialize processor.

        Args:
            ai_client: Groq API client
        """
        self.ai_client = ai_client

    def process_file(self, filepath: str) -> Dict[str, Any]:
        """
        Process a single music file.

        Args:
            filepath: Path to music file

        Returns:
            Processing result dictionary
        """
        result = {
            'filepath': filepath,
            'filename': Path(filepath).name,
            'success': False,
            'metadata': None,
            'errors': [],
        }

        try:
            filename_only = extract_filename_without_extension(filepath)
            metadata = self._analyze_file(filename_only)
            result['metadata'] = metadata
            self._clear_metadata(filepath)
            self._write_metadata(filepath, metadata)
            result['success'] = True

        except Exception as e:
            result['errors'].append(str(e))

        return result

    def _analyze_file(self, filename: str) -> MusicMetadata:
        """
        Analyze file with AI.

        Args:
            filename: Filename to analyze

        Returns:
            Music metadata from AI

        Raises:
            Exception: If AI analysis fails
        """
        return self.ai_client.analyze_filename(filename)

    def _clear_metadata(self, filepath: str) -> None:
        """
        Remove all existing metadata from file.

        Args:
            filepath: Path to music file

        Raises:
            Exception: If clearing fails
        """
        MetadataWriter.clear(filepath)

    def _write_metadata(self, filepath: str, metadata: MusicMetadata) -> None:
        """
        Write metadata to file.

        Args:
            filepath: Path to music file
            metadata: Metadata to write

        Raises:
            Exception: If writing fails
        """
        MetadataWriter.write(
            filepath,
            title=metadata.song_name,
            artists=metadata.artists,
            album=metadata.album,
            album_artist=metadata.album_artist,
            genre=metadata.genre,
            release_year=metadata.release_year,
            track_number=metadata.track_number,
        )
