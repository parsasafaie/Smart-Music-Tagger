"""Groq API client for music metadata extraction."""

import json
import time
from typing import Any, Optional

import requests

from .models import MusicMetadata

# Lightweight Groq model with built-in web search. This project relies on
# web search to verify metadata, so a search-enabled model is required.
DEFAULT_MODEL = 'groq/compound-mini'

_SYSTEM_PROMPT = (
    'Extract music metadata from a filename. Web search allowed when needed; prefer '
    'official, Discogs, MusicBrainz sources; minimize searches. Strip promo text, '
    'source/site names, bitrate/quality/group tags, uploaders, comments. Never guess; '
    'if unsure set the field to "Unknown". '
    'Return JSON only: song_name, artists (list), album, genre, release_year, '
    'album_artist, track_number. Unknown text="Unknown", no artists=[].'
)


class GroqClient:
    """Client for the Groq API."""

    def __init__(
        self,
        api_key: str,
        api_url: str,
        model: str = DEFAULT_MODEL,
        request_delay_seconds: float = 3.0,
    ):
        """Initialize the Groq client.

        Args:
            api_key: Groq API key
            api_url: Groq API base URL
            model: Groq model name to use (defaults to the search-enabled
                ``groq/compound-mini``; do not change unless explicitly requested)
            request_delay_seconds: Minimum delay between API requests
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.model = model or DEFAULT_MODEL
        self.request_delay_seconds = request_delay_seconds
        self._last_request_time = 0.0

    def analyze_filename(self, filename: str) -> MusicMetadata:
        """Analyze a music filename and extract metadata with the Groq API."""
        self._wait_for_rate_limit()
        prompt = self._create_analysis_prompt(filename)
        response = self._call_api(prompt)
        return self._parse_response(response)

    def _wait_for_rate_limit(self) -> None:
        """Enforce minimum delay between consecutive API requests."""
        if self.request_delay_seconds <= 0:
            return

        elapsed = time.monotonic() - self._last_request_time
        if elapsed < self.request_delay_seconds:
            time.sleep(self.request_delay_seconds - elapsed)

        self._last_request_time = time.monotonic()

    @staticmethod
    def _create_analysis_prompt(filename: str) -> str:
        """Create a compact prompt for filename analysis and metadata extraction."""
        return filename

    def _call_api(self, prompt: str) -> str:
        """Send a prompt to the Groq API and return the response text."""
        try:
            request_body = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': _SYSTEM_PROMPT},
                    {'role': 'user', 'content': prompt},
                ],
                # Note: compound models (groq/compound-mini) use a server-preset
                # temperature and reject a custom `temperature` value, so it is omitted.
                'response_format': {'type': 'json_object'},
                'max_completion_tokens': 256,
            }

            response = requests.post(
                f'{self.api_url}/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json=request_body,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

            if not data.get('choices') or not data['choices'][0].get('message'):
                raise ValueError('Invalid API response: no choices or message')

            content = data['choices'][0]['message'].get('content')
            if not content:
                raise ValueError('Invalid API response: empty message content')
            return content

        except requests.HTTPError as error:
            response = error.response
            status_code = response.status_code if response is not None else None
            error_message = response.text if response is not None else str(error)
            if status_code == 401:
                raise Exception('Groq API authentication failed: invalid API key') from error
            if status_code == 429:
                raise Exception(f'Groq API rate limit exceeded: {error_message}') from error
            if status_code == 413:
                raise Exception('Groq API request was too large. Try a smaller model or retry.') from error
            raise Exception(f'Groq API request failed: {error_message}') from error
        except (requests.RequestException, ValueError) as error:
            raise Exception(f'Groq API request failed: {error}') from error

    def _parse_response(self, response_text: str) -> MusicMetadata:
        """Parse the Groq API response into structured music metadata."""
        try:
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            data = json.loads(response_text.strip())

            artists = data.get('artists')
            if not isinstance(artists, list) or not any(str(artist).strip() for artist in artists):
                artists = ['Unknown Artist']
            else:
                artists = [str(artist).strip() for artist in artists if str(artist).strip()]

            return MusicMetadata(
                song_name=self._non_empty_value(data.get('song_name'), 'Unknown Title'),
                artists=artists,
                album=self._non_empty_value(data.get('album'), 'Unknown Album'),
                genre=self._non_empty_value(data.get('genre'), 'Unknown'),
                release_year=self._non_empty_value(data.get('release_year'), 'Unknown'),
                album_artist=self._optional_non_empty_value(data.get('album_artist')),
                track_number=self._optional_non_empty_value(data.get('track_number')),
                additional_metadata=data.get('additional_metadata') or {},
            )
        except json.JSONDecodeError as error:
            raise Exception(
                f'Failed to parse Groq API JSON response: {error}\nResponse: {response_text}'
            ) from error
        except (KeyError, TypeError) as error:
            raise Exception(f'Invalid Groq API response structure: {error}') from error

    @staticmethod
    def _non_empty_value(value: Any, default: str) -> str:
        """Return a trimmed metadata value or a non-empty fallback."""
        text = str(value).strip() if value is not None else ''
        return text or default

    @staticmethod
    def _optional_non_empty_value(value: Any) -> Optional[str]:
        """Return a trimmed optional value, or ``None`` when it is empty."""
        text = str(value).strip() if value is not None else ''
        return text or None
