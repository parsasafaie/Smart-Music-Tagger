"""Utility helper functions."""

import os
import re
from pathlib import Path
from typing import List, Tuple


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for filesystem compatibility.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '', filename)

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')

    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]

    return sanitized


def get_file_extension(filepath: str) -> str:
    """
    Get file extension.

    Args:
        filepath: Path to file

    Returns:
        File extension (lowercase, without dot)
    """
    return Path(filepath).suffix.lower().lstrip('.')


def is_supported_audio_format(filepath: str) -> bool:
    """
    Check if file is a supported audio format.

    Args:
        filepath: Path to file

    Returns:
        True if file is supported
    """
    supported_formats = {'mp3', 'flac', 'wav', 'm4a', 'ogg'}
    return get_file_extension(filepath) in supported_formats


def get_audio_files_in_directory(directory: str) -> List[str]:
    """
    Get all audio files in directory (non-recursive).

    Args:
        directory: Path to directory

    Returns:
        List of absolute paths to audio files
    """
    audio_files = []
    directory_path = Path(directory)

    if not directory_path.exists():
        return audio_files

    for file in directory_path.iterdir():
        if file.is_file() and is_supported_audio_format(str(file)):
            audio_files.append(str(file))

    return sorted(audio_files)


def split_artist_names(artist_string: str, max_artists: int = 5) -> List[str]:
    """
    Split artist names from a string.

    Args:
        artist_string: Artist string (can be single or multiple separated by various separators)
        max_artists: Maximum number of artists to extract

    Returns:
        List of artist names
    """
    if not artist_string:
        return []

    # Split by common separators
    separators = [' and ', ' & ', ', ', '; ', ' feat. ', ' ft. ', ' feat ', ' ft ']
    artists = [artist_string]

    for sep in separators:
        new_artists = []
        for artist in artists:
            new_artists.extend([a.strip() for a in artist.split(sep)])
        artists = new_artists

    # Remove empty strings and limit
    artists = [a for a in artists if a][:max_artists]

    return artists


def format_artists_for_filename(artists: List[str]) -> str:
    """
    Format artist list for filename.

    Args:
        artists: List of artist names

    Returns:
        Formatted string (e.g., "Artist 1 and Artist 2")
    """
    if not artists:
        return "Unknown Artist"

    if len(artists) == 1:
        return artists[0]

    return " and ".join(artists)


def extract_filename_without_extension(filepath: str) -> str:
    """
    Extract filename without extension.

    Args:
        filepath: Path to file

    Returns:
        Filename without extension
    """
    return Path(filepath).stem


def create_backup_path(filepath: str) -> str:
    """
    Create backup file path.

    Args:
        filepath: Original file path

    Returns:
        Backup file path
    """
    path = Path(filepath)
    return str(path.parent / f"{path.stem}.bak{path.suffix}")
