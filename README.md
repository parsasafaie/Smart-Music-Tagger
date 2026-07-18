# Smart Music Tagger

### AI-powered music metadata cleaning & file renaming.

[English](README.md) | [فارسی](README.fa.md)

---

Smart Music Tagger analyzes music filenames with AI, extracts accurate metadata,
writes clean tags into audio files, and renames them to a consistent format.

It provides two interchangeable front-ends that share the same processing engine:

- **CLI**
- **Web GUI**

---

## Features

- AI-powered metadata extraction via the Groq API
- Removes existing metadata before writing clean tags
- Renames files to `Artist - Song.ext`
- Supports MP3, FLAC, WAV, M4A and OGG
- CLI and Web GUI powered by the same core engine
- Human-readable log files
- Modular architecture

<p align="center">
  <img src="docs/images/cli-interface.png" alt="CLI Interface" width="400" height="700">
  <img src="docs/images/web-interface.png" alt="Web GUI" width="400" height="700">
</p>

---

## Installation

### Prerequisites

- Python 3.8+
- pip
- A Groq API key

1. Clone the repository

```bash
git clone https://github.com/parsasafaie/smart-music-tagger.git
cd smart-music-tagger
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Create the configuration file

```bash
cp .env.example .env
```

4. Edit `.env`

```env
GROQ_API_KEY=your_groq_api_key
GROQ_API_URL=https://api.groq.com/openai/v1
GROQ_MODEL=groq/compound-mini
GROQ_REQUEST_DELAY_SECONDS=5
MUSIC_DIRECTORY=C:/Users/YourName/Music
```

> Keep your `.env` file private. It contains your API key.

---

## Configuration

The CLI reads these values from `.env`. The Web GUI accepts the same settings
through its graphical form.

| Variable | Required | Description |
|----------|:--------:|-------------|
| `GROQ_API_KEY` | Yes | Your Groq API key |
| `GROQ_API_URL` | Yes | Groq API endpoint |
| `GROQ_MODEL` | Yes | Model name |
| `GROQ_REQUEST_DELAY_SECONDS` | No | Delay between API requests |
| `MUSIC_DIRECTORY` | Yes | Path to your music folder |

---

## Usage

Both interfaces use the same processing pipeline.

### CLI

Reads configuration from `.env`.

```bash
python cli_main.py
```

### Web GUI

Starts a local Flask application.

```bash
python gui_main.py
```

Open:

```
http://127.0.0.1:5000
```

Fill in the form and click **Start Tagging**.

Available options:

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `127.0.0.1` | Bind address |
| `--port` | `5000` | Bind port |
| `--debug` | Off | Enable Flask debug mode |

> By default, the Web GUI is accessible only from `127.0.0.1`. API keys are never stored or returned.

---

## Metadata Written

For each file, Smart Music Tagger writes:

- Song title
- Artist(s)
- Album
- Genre
- Release year
- Album artist
- Track number (when available)

Existing metadata is cleared before writing verified information. Unknown fields
are never guessed.

---

## Architecture

Smart Music Tagger follows a modular layered architecture. Both the CLI and the
Web GUI use the same `TaggerService`, keeping the user interfaces independent
from the core processing logic.

```text
       cli_main.py                gui_main.py
            │                         │
            └────────────┬────────────┘
                         ▼
                  TaggerService
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    FileScanner     FileProcessor    FileRenamer
                         │
                GroqClient + MetadataWriter
                         │
                       Logger
```

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for more details.

---

## License

Released under the **MIT License**. See [`LICENSE`](LICENSE).

---

## Contributing

Contributions are welcome. Please keep business logic inside `core/` and
UI-related code inside `cli/` or `gui/`.