"""File renamer."""

from pathlib import Path
from typing import List
from utils import sanitize_filename, format_artists_for_filename


class FileRenamer:
    """Rename music files to standard format."""

    STANDARD_FORMAT = "{artist} - {title}.{ext}"

    @staticmethod
    def rename_file(filepath: str, artists: List[str], title: str) -> str:
        """
        Rename file to standard format.

        Args:
            filepath: Path to file
            artists: List of artist names
            title: Song title

        Returns:
            New filename (full path)

        Raises:
            Exception: If renaming fails
        """
        path = Path(filepath)
        directory = path.parent
        extension = path.suffix.lstrip('.')

        # Format artist names
        artist_string = format_artists_for_filename(artists)

        # Create new filename
        new_filename = FileRenamer.STANDARD_FORMAT.format(
            artist=sanitize_filename(artist_string),
            title=sanitize_filename(title),
            ext=extension.lower(),
        )

        new_filepath = directory / new_filename

        # Check if file already exists with that name
        if new_filepath.exists() and str(new_filepath) != filepath:
            raise Exception(f'File already exists: {new_filepath}')

        try:
            if str(new_filepath) != filepath:
                path.rename(new_filepath)
            return str(new_filepath)

        except Exception as e:
            raise Exception(f'Failed to rename file: {str(e)}')

    @staticmethod
    def get_new_filename(artists: List[str], title: str, extension: str) -> str:
        """
        Get new filename without renaming.

        Args:
            artists: List of artist names
            title: Song title
            extension: File extension

        Returns:
            New filename (without path)
        """
        artist_string = format_artists_for_filename(artists)

        return FileRenamer.STANDARD_FORMAT.format(
            artist=sanitize_filename(artist_string),
            title=sanitize_filename(title),
            ext=extension.lower(),
        )
