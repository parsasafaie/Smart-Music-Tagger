# Smart Music Tagger - README

## Overview

Smart Music Tagger is a production-quality command-line application that automatically:
- Analyzes music filenames using AI (Groq API)
- Extracts accurate music metadata
- Updates file metadata tags
- Renames files in a consistent format

## Features

- AI-powered metadata extraction using Groq API
- Support for MP3, FLAC, WAV, M4A, OGG formats
- Beautiful CLI interface with color-coded output
- Comprehensive logging system
- Modular, extensible architecture
- Configuration via `.env` file

## Installation

### Requirements
- Python 3.8+
- pip

### Setup

1. Clone the repository and enter it:
```bash
git clone https://github.com/parsasafaie/smart-music-tagger.git
cd smart-music-tagger
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create and configure the `.env` file:
```bash
cp .env.example .env
```

4. Fill in your `.env` file with actual values (see [Configuration](#configuration)):
```env
GROQ_API_KEY=your_actual_groq_api_key
GROQ_API_URL=https://api.groq.com/openai/v1
GROQ_MODEL=groq/compound-mini
GROQ_REQUEST_DELAY_SECONDS=3
MUSIC_DIRECTORY=C:/Users/YourName/Music
```

## Usage

Run the application with:
```bash
python main.py
```

The application will:
1. Scan the configured music directory
2. Analyze each filename with AI
3. Extract metadata (artist, album, genre, year)
4. Update file metadata tags
5. Rename files to: `Artist - Song.ext`
6. Generate a detailed log file

## Project Structure

```
Smart Music Tagger/
├── main.py                 # CLI entry point (reads .env, drives TaggerService)
├── config/
│   └── config_loader.py    # .env configuration loader (CLI only)
├── core/
│   ├── service.py           # TaggerService — reusable orchestration layer
│   ├── scanner.py          # File scanning
│   ├── processor.py        # Per-file AI analysis + metadata write
│   └── renamer.py          # File renaming
├── ai/
│   ├── models.py           # Shared metadata models
│   └── groq_client.py      # Groq API integration
├── metadata/
│   ├── reader.py           # Metadata reading
│   └── writer.py           # Metadata writing
├── cli/
│   └── interface.py        # CLI interface (Rich)
├── utils/
│   └── helpers.py          # Utility functions
├── logs/
│   ├── logger.py           # Logging system
│   └── *.log               # Log files (generated)
└── requirements.txt        # Python dependencies
```

## Configuration

### Required Configuration

- **GROQ_API_KEY** - Your Groq API key (get it from https://console.groq.com/keys)
- **GROQ_API_URL** - Groq API endpoint (usually `https://api.groq.com/openai/v1`)
- **GROQ_MODEL** - Groq model name (default: `groq/compound-mini`, lightweight with web search)
- **GROQ_REQUEST_DELAY_SECONDS** - Minimum delay between Groq requests (default: `3`)
- **MUSIC_DIRECTORY** - Path to your music folder

## Output Example

```
╔════════════════════════════════════════╗
║     SMART MUSIC TAGGER                 ║
║     AI-Powered Metadata Management     ║
╚════════════════════════════════════════╝

ℹ Info: Loading configuration...
ℹ Info: Scanning directory: /music

Configuration:
  Music Directory: /music
  Files to Process: 3

[1/3] Processing:
  old_song_name_128kbps.mp3
         ↓
  Artist Name - Song Name.mp3

Metadata updated:
  ✓ Artist: Artist Name
  ✓ Album: Album Name
  ✓ Genre: Pop
  ✓ Release Year: 2024

Processing Complete:
  Total Files:    3
  Successful:     3
  Failed:         0
  Success Rate:   100.0%

ℹ Info: Log file saved to: logs/music_tagger_20240101_120000.log
```

## Supported Audio Formats

- **MP3** - MPEG Audio Layer III
- **FLAC** - Free Lossless Audio Codec
- **WAV** - Waveform Audio File Format
- **M4A** - MPEG-4 Audio
- **OGG** - Ogg Vorbis

## Metadata Extracted

The AI extracts the following metadata:
- Song name
- Artist name(s) (handles multiple artists)
- Album name
- Genre
- Release year
- Album artist (if different)
- Track number

## AI Processing

The AI (`groq/compound-mini`, with web search for verification) processes each filename by:
1. Removing bitrate tags (128kbps, 320kbps, etc.)
2. Removing download website names and source/release-group tags
3. Cleaning up tags like "Official Video", "Lyrics"
4. Identifying the actual song information from the filename
5. Verifying metadata via web search only when needed
6. Returning structured JSON metadata (never guessing unknown fields)

The application then:
1. Clears all existing file metadata
2. Writes the clean, verified standard tags only
3. Renames the file to `Artist - Song.ext`

## Logging

All processing results are logged to `logs/music_tagger_YYYYMMDD_HHMMSS.log`.

Each log entry includes:
- Original filename
- New filename
- Extracted metadata
- Processing status (success/failure)
- Any errors encountered

## Architecture Benefits

The modular architecture enables:
- **Easy testing** — Each module can be tested independently
- **GUI-ready** — All business logic lives in `TaggerService` (`core/service.py`). It takes config as constructor parameters and reports progress via a callback, so a future Flask GUI can drive it directly with form-provided values — no `.env` required.
- **API integration** — Easy to add REST API layer
- **New features** — Batch operations, scheduled runs, plugins
- **Maintenance** — Clear responsibility for each module

## Error Handling

The application:
- Gracefully handles missing or invalid files
- Skips unsupported audio formats
- Logs all errors for troubleshooting
- Continues processing even if individual files fail
- Provides clear error messages in CLI and logs

## Troubleshooting

### Configuration not loading
- Ensure `.env` file exists in the application directory
- Verify all required fields are filled in correctly

### API key errors
- Verify your Groq API key is correct
- Check API URL format
- Ensure you have API quota remaining

### File rename fails
- Ensure you have write permissions to the directory
- Check for duplicate filenames
- Verify filename doesn't contain invalid characters

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please follow the modular architecture design.

## Support

For issues or questions, please check:
1. The logs directory for detailed error information
2. Configuration files for proper setup
3. Groq API documentation for API-related issues
