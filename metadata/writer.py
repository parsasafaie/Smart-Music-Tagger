"""Metadata writer for music files."""

from typing import List, Optional, Dict, Any
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TPE2, TALB, TCON, TDRC, TRCK
from mutagen.flac import FLAC
from mutagen.wave import WAVE
from mutagen.m4a import M4A
from mutagen.oggvorbis import OggVorbis


class MetadataWriter:
    """Write metadata to audio files."""

    SUPPORTED_FORMATS = {
        'mp3': 'mp3',
        'flac': 'flac',
        'wav': 'wav',
        'm4a': 'm4a',
        'ogg': 'ogg',
    }

    @staticmethod
    def clear(filepath: str) -> None:
        """
        Remove all existing metadata from an audio file.

        Args:
            filepath: Path to audio file

        Raises:
            Exception: If clearing fails
        """
        extension = Path(filepath).suffix.lower().lstrip('.')

        if extension not in MetadataWriter.SUPPORTED_FORMATS:
            raise ValueError(f'Unsupported audio format: {extension}')

        try:
            if extension == 'mp3':
                MetadataWriter._clear_mp3(filepath)
            elif extension == 'flac':
                MetadataWriter._clear_flac(filepath)
            elif extension == 'wav':
                MetadataWriter._clear_wav(filepath)
            elif extension == 'm4a':
                MetadataWriter._clear_m4a(filepath)
            elif extension == 'ogg':
                MetadataWriter._clear_ogg(filepath)
        except Exception as e:
            raise Exception(f'Failed to clear metadata from {filepath}: {str(e)}')

    @staticmethod
    def _clear_mp3(filepath: str) -> None:
        """Remove all ID3 tags from an MP3 file."""
        audio = MP3(filepath)
        audio.delete()
        audio.save()

    @staticmethod
    def _clear_flac(filepath: str) -> None:
        """Remove all Vorbis comments and pictures from a FLAC file."""
        audio = FLAC(filepath)
        audio.clear()
        audio.clear_pictures()
        audio.save()

    @staticmethod
    def _clear_wav(filepath: str) -> None:
        """Remove all ID3 tags from a WAV file."""
        audio = WAVE(filepath)
        try:
            audio.delete()
        except Exception:
            pass
        audio.save()

    @staticmethod
    def _clear_m4a(filepath: str) -> None:
        """Remove all tags from an M4A file."""
        audio = M4A(filepath)
        audio.clear()
        audio.save()

    @staticmethod
    def _clear_ogg(filepath: str) -> None:
        """Remove all Vorbis comments from an OGG file."""
        audio = OggVorbis(filepath)
        audio.clear()
        audio.save()

    @staticmethod
    def write(
        filepath: str,
        title: str,
        artists: List[str],
        album: str,
        album_artist: Optional[str],
        genre: str,
        release_year: str,
        track_number: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Write metadata to audio file.

        Args:
            filepath: Path to audio file
            title: Song title
            artists: List of artist names
            album: Album name
            album_artist: Album artist
            genre: Genre
            release_year: Release year
            track_number: Track number
            additional_metadata: Additional metadata fields

        Returns:
            True if successful

        Raises:
            Exception: If writing fails
        """
        extension = Path(filepath).suffix.lower().lstrip('.')

        if extension not in MetadataWriter.SUPPORTED_FORMATS:
            raise ValueError(f'Unsupported audio format: {extension}')

        artist_string = ', '.join(artists) if artists else 'Unknown Artist'
        album_artist_value = album_artist or artist_string

        try:
            if extension == 'mp3':
                MetadataWriter._write_mp3(
                    filepath, title, artist_string, album, album_artist_value, genre, release_year,
                    track_number
                )
            elif extension == 'flac':
                MetadataWriter._write_flac(
                    filepath, title, artist_string, album, album_artist_value, genre, release_year,
                    track_number
                )
            elif extension == 'wav':
                MetadataWriter._write_wav(
                    filepath, title, artist_string, album, album_artist_value, genre, release_year,
                    track_number
                )
            elif extension == 'm4a':
                MetadataWriter._write_m4a(
                    filepath, title, artist_string, album, album_artist_value, genre, release_year,
                    track_number
                )
            elif extension == 'ogg':
                MetadataWriter._write_ogg(
                    filepath, title, artist_string, album, album_artist_value, genre, release_year,
                    track_number
                )

            return True

        except Exception as e:
            raise Exception(f'Failed to write metadata to {filepath}: {str(e)}')

    @staticmethod
    def _write_mp3(
        filepath: str,
        title: str,
        artist: str,
        album: str,
        album_artist: str,
        genre: str,
        year: str,
        track_number: Optional[str] = None,
    ):
        """Write metadata to MP3 file."""
        try:
            audio = MP3(filepath)
        except Exception:
            audio = MP3(filepath)
            audio.add_tags()

        if audio.tags is None:
            audio.add_tags()

        audio.tags['TIT2'] = TIT2(encoding=3, text=[title])
        audio.tags['TPE1'] = TPE1(encoding=3, text=[artist])
        audio.tags['TPE2'] = TPE2(encoding=3, text=[album_artist])
        audio.tags['TALB'] = TALB(encoding=3, text=[album])
        audio.tags['TCON'] = TCON(encoding=3, text=[genre])
        audio.tags['TDRC'] = TDRC(encoding=3, text=[year])

        if track_number:
            audio.tags['TRCK'] = TRCK(encoding=3, text=[track_number])

        audio.save()

    @staticmethod
    def _write_flac(
        filepath: str,
        title: str,
        artist: str,
        album: str,
        album_artist: str,
        genre: str,
        year: str,
        track_number: Optional[str] = None,
    ):
        """Write metadata to FLAC file."""
        try:
            audio = FLAC(filepath)
        except Exception:
            audio = FLAC(filepath)

        audio['title'] = [title]
        audio['artist'] = [artist]
        audio['albumartist'] = [album_artist]
        audio['album'] = [album]
        audio['genre'] = [genre]
        audio['date'] = [year]

        if track_number:
            audio['tracknumber'] = [track_number]

        audio.save()

    @staticmethod
    def _write_wav(
        filepath: str,
        title: str,
        artist: str,
        album: str,
        album_artist: str,
        genre: str,
        year: str,
        track_number: Optional[str] = None,
    ):
        """Write metadata to WAV file."""
        try:
            audio = WAVE(filepath)
        except Exception:
            audio = WAVE(filepath)
            audio.add_tags()

        if audio.tags is None:
            audio.add_tags()

        audio.tags['TIT2'] = TIT2(encoding=3, text=[title])
        audio.tags['TPE1'] = TPE1(encoding=3, text=[artist])
        audio.tags['TPE2'] = TPE2(encoding=3, text=[album_artist])
        audio.tags['TALB'] = TALB(encoding=3, text=[album])
        audio.tags['TCON'] = TCON(encoding=3, text=[genre])
        audio.tags['TDRC'] = TDRC(encoding=3, text=[year])

        if track_number:
            audio.tags['TRCK'] = TRCK(encoding=3, text=[track_number])

        audio.save()

    @staticmethod
    def _write_m4a(
        filepath: str,
        title: str,
        artist: str,
        album: str,
        album_artist: str,
        genre: str,
        year: str,
        track_number: Optional[str] = None,
    ):
        """Write metadata to M4A file."""
        try:
            audio = M4A(filepath)
        except Exception:
            audio = M4A(filepath)

        audio['\xa9nam'] = [title]
        audio['\xa9ART'] = [artist]
        audio['aART'] = [album_artist]
        audio['\xa9alb'] = [album]
        audio['\xa9gen'] = [genre]
        audio['\xa9day'] = [year]

        if track_number:
            audio['trkn'] = [
                (int(track_number.split('/')[0]), int(track_number.split('/')[1]) if '/' in track_number else 0)
            ]

        audio.save()

    @staticmethod
    def _write_ogg(
        filepath: str,
        title: str,
        artist: str,
        album: str,
        album_artist: str,
        genre: str,
        year: str,
        track_number: Optional[str] = None,
    ):
        """Write metadata to OGG file."""
        try:
            audio = OggVorbis(filepath)
        except Exception:
            audio = OggVorbis(filepath)

        audio['title'] = [title]
        audio['artist'] = [artist]
        audio['albumartist'] = [album_artist]
        audio['album'] = [album]
        audio['genre'] = [genre]
        audio['date'] = [year]

        if track_number:
            audio['tracknumber'] = [track_number]

        audio.save()
