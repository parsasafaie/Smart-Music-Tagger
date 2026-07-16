# Smart Music Tagger - Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure with .env File

Copy the example configuration:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```
GROQ_API_KEY=your_groq_api_key
GROQ_API_URL=https://api.groq.com/openai/v1
GROQ_MODEL=groq/compound-mini
GROQ_REQUEST_DELAY_SECONDS=3
MUSIC_DIRECTORY=C:/Users/YourName/Music
```

**Important**: Keep `.env` private - it contains your API key!

### 3. Run
```bash
python main.py
```

Done! The application will:
- Scan your music directory
- Analyze filenames with AI
- Extract metadata
- Update file tags
- Rename files
- Generate logs

## Example Output

```
╔════════════════════════════════════════╗
║     SMART MUSIC TAGGER                 ║
║     AI-Powered Metadata Management     ║
╚════════════════════════════════════════╝

ℹ Info: Loading configuration...
ℹ Info: Scanning directory: C:/Users/YourName/Music

Configuration:
  Music Directory: C:/Users/YourName/Music
  Files to Process: 5

[1/5] Processing:
  eminem_lose_yourself_320kbps.mp3
         ↓
  Eminem - Lose Yourself.mp3

Metadata updated:
  ✓ Artist: Eminem
  ✓ Album: 8 Mile
  ✓ Genre: Hip Hop
  ✓ Release Year: 2002

Processing Complete:
  Total Files:    5
  Successful:     5
  Failed:         0
  Success Rate:   100.0%

ℹ Info: Log file saved to: logs/music_tagger_20240115_143022.log
```

## File Naming Results

Before and after examples:

### Before Processing:
- `Eminem - Lose Yourself 320kbps.mp3`
- `scorpions - wind of change (Official Video).flac`
- `the_beatles_let_it_be.wav`
- `Dua Lipa - Levitating (Lyrics Video) (128).m4a`
- `The Weeknd - Blinding Lights [Official] (2020).ogg`

### After Processing:
- `Eminem - Lose Yourself.mp3`
- `Scorpions - Wind Of Change.flac`
- `The Beatles - Let It Be.wav`
- `Dua Lipa - Levitating.m4a`
- `The Weeknd - Blinding Lights.ogg`

## Supported Formats

| Format | Extension | Support |
|--------|-----------|---------|
| MP3 | .mp3 | Full |
| FLAC | .flac | Full |
| WAV | .wav | Full |
| M4A | .m4a | Full |
| OGG | .ogg | Full |

## What Gets Updated

For each file, the application updates:

### Metadata Tags
- Title / Song Name
- Artist(s)
- Album
- Genre
- Release Year
- Track Number (if available)

### File Name
- Format: `Artist - Song.extension`
- Sanitizes special characters
- Handles multiple artists: `Artist 1 and Artist 2 - Song.mp3`

## Logs

After processing, find your log file in the `logs/` directory:

- **Location**: `logs/music_tagger_YYYYMMDD_HHMMSS.log`
- **Contains**:
  - Original filename
  - New filename
  - Extracted metadata
  - Success/failure status
  - Any errors encountered
  - Processing summary

## Troubleshooting

### "Configuration validation failed"
```
Missing required configuration: groq_api_key, groq_api_url, groq_model, music_directory
```

**Solution**: Edit `.env` with all required settings.

### "Groq API request failed: 401"
```
Unauthorized - Invalid API key
```

**Solution**: Check your `GROQ_API_KEY` is correct and has valid API quota.

### "Music directory does not exist"
```
Music directory does not exist: C:/NonExistent/Path
```

**Solution**: Update `MUSIC_DIRECTORY` to a valid folder path.

### "No audio files found"
```
⚠ Warning: No audio files found in the specified directory
```

**Solution**:
- Check the directory contains MP3, FLAC, WAV, M4A, or OGG files
- Verify the path is correct

### Files not renamed
- Check file permissions in the directory
- Ensure you have write access
- Check the new filename doesn't already exist

## Architecture Overview

The application is modular and extensible:

```
User Input (config)
        ↓
    main.py
        ↓
    ┌───┴───────────────────────┐
    ↓           ↓               ↓
FileScanner GroqClient   FileProcessor
    ↓           ↓               ↓
  (scan)    (AI API)    (process files)
            ↓               ↓
         Metadata        FileRenamer
         (read/write)      (rename)
         ↓
    Logger (log results)
         ↓
    CLI Interface (display)
```

## Configuration Reference

### Required Settings
```env
GROQ_API_KEY=your-groq-api-key
GROQ_API_URL=https://api.groq.com/openai/v1
GROQ_MODEL=groq/compound-mini
GROQ_REQUEST_DELAY_SECONDS=3
MUSIC_DIRECTORY=/path/to/music
```

### Keeping Your API Key Secure
- Never commit `.env` to version control (it's in `.gitignore`)
- Use `.env.example` as a template
- Keep your API key confidential

## Support & Issues

For detailed information, see:
- `README.md` - Full documentation
- `logs/` - Error logs and processing details
- `.env.example` - Configuration template

Happy tagging!
