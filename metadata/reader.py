"""Metadata reader for music files."""

from typing import Dict, Any, Optional
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wave import WAVE
from mutagen.m4a import M4A
from mutagen.oggvorbis import OggVorbis
from pathlib import Path


class MetadataReader:
    """Read metadata from audio files."""

    SUPPORTED_FORMATS = {
        'mp3': MP3,
        'flac': FLAC,
        'wav': WAVE,
        'm4a': M4A,
        'ogg': OggVorbis,
    }

    @staticmethod
    def read(filepath: str) -> Dict[str, Any]:
        """
        Read metadata from audio file.

        Args:
            filepath: Path to audio file

        Returns:
            Dictionary of metadata
        """
        extension = Path(filepath).suffix.lower().lstrip('.')

        if extension not in MetadataReader.SUPPORTED_FORMATS:
            raise ValueError(f'Unsupported audio format: {extension}')

        try:
            audio_class = MetadataReader.SUPPORTED_FORMATS[extension]
            audio = audio_class(filepath)

            metadata = MetadataReader._extract_metadata(audio, extension)
            return metadata

        except Exception as e:
            raise Exception(f'Failed to read metadata from {filepath}: {str(e)}')

    @staticmethod
    def _extract_metadata(audio: Any, format_type: str) -> Dict[str, Any]:
        """
        Extract metadata from audio object.

        Args:
            audio: Mutagen audio object
            format_type: Audio format type

        Returns:
            Dictionary of metadata
        """
        metadata = {}

        # Extract common metadata
        if hasattr(audio, 'tags') and audio.tags:
            tags = audio.tags

            # ID3 tags (MP3)
            if hasattr(tags, 'get'):
                metadata['title'] = MetadataReader._get_tag(tags, 'TIT2')
                metadata['artist'] = MetadataReader._get_tag(tags, 'TPE1')
                metadata['album'] = MetadataReader._get_tag(tags, 'TALB')
                metadata['genre'] = MetadataReader._get_tag(tags, 'TCON')
                metadata['date'] = MetadataReader._get_tag(tags, 'TDRC')
                metadata['track_number'] = MetadataReader._get_tag(tags, 'TRCK')

            # Vorbis comments (FLAC, OGG, etc.)
            elif isinstance(tags, dict):
                metadata['title'] = MetadataReader._get_vorbis_tag(tags, 'title')
                metadata['artist'] = MetadataReader._get_vorbis_tag(tags, 'artist')
                metadata['album'] = MetadataReader._get_vorbis_tag(tags, 'album')
                metadata['genre'] = MetadataReader._get_vorbis_tag(tags, 'genre')
                metadata['date'] = MetadataReader._get_vorbis_tag(tags, 'date')
                metadata['track_number'] = MetadataReader._get_vorbis_tag(tags, 'tracknumber')

            # M4A tags
            else:
                metadata['title'] = MetadataReader._get_m4a_tag(tags, '\xa9nam')
                metadata['artist'] = MetadataReader._get_m4a_tag(tags, '\xa9ART')
                metadata['album'] = MetadataReader._get_m4a_tag(tags, '\xa9alb')
                metadata['genre'] = MetadataReader._get_m4a_tag(tags, '\xa9gen')
                metadata['date'] = MetadataReader._get_m4a_tag(tags, '\xa9day')
                metadata['track_number'] = MetadataReader._get_m4a_tag(tags, 'trkn')

        return metadata

    @staticmethod
    def _get_tag(tags: Any, tag_name: str) -> Optional[str]:
        """Get ID3 tag value."""
        if tag_name in tags:
            return str(tags[tag_name].text[0]) if tags[tag_name].text else None
        return None

    @staticmethod
    def _get_vorbis_tag(tags: Dict, tag_name: str) -> Optional[str]:
        """Get Vorbis comment tag value."""
        if tag_name in tags:
            value = tags[tag_name]
            return str(value[0]) if isinstance(value, list) and value else str(value)
        return None

    @staticmethod
    def _get_m4a_tag(tags: Any, tag_name: str) -> Optional[str]:
        """Get M4A tag value."""
        if tag_name in tags:
            value = tags[tag_name]
            if isinstance(value, list) and value:
                return str(value[0])
            return str(value)
        return None
