"""Shared AI data models."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class MusicMetadata:
    """Structured music metadata from AI."""

    song_name: str
    artists: List[str]
    album: str
    genre: str
    release_year: str
    album_artist: Optional[str] = None
    track_number: Optional[str] = None
    additional_metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'song_name': self.song_name,
            'artists': self.artists,
            'album': self.album,
            'genre': self.genre,
            'release_year': self.release_year,
            'album_artist': self.album_artist,
            'track_number': self.track_number,
            'additional_metadata': self.additional_metadata or {},
        }
