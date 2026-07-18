# 🎵 Smart Music Tagger

### AI-powered music metadata cleaning & file renaming.

[English](README.md) | [فارسی](README.fa.md)

---

Smart Music Tagger analyzes your music filenames with AI, extracts accurate
metadata, writes clean tags into your files, and renames them to a consistent
format — automatically, across whole folders at a time.

It ships with **two interchangeable front-ends** that share one core engine:

- 💻 **CLI** — a terminal interface driven by a `.env` file
- 🌐 **Web GUI** — a Flask app with live progress streaming

Both produce identical results. Use whichever fits the task.



## ✨ Features

- **AI metadata extraction** via the Groq API (with web-search verification)
- **Clean tags** — clears existing junk, writes only verified fields
- **Auto-renames** files to `Artist - Song.ext`
- **Two front-ends** — CLI for automation, Web GUI for interactive runs
- **Live progress** — the GUI streams per-file progress over Server-Sent Events
- **Detailed logging** — every run writes a human-readable log file
- **Modular architecture** — core logic is fully decoupled from the UI
- Supports **MP3, FLAC, WAV, M4A, OGG**


## 📦 Installation

### Prerequisites

- **Python 3.8+**
- **pip**
- A **Groq API key** — create one (free) at <https://console.groq.com/keys>

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/parsasafaie/smart-music-tagger.git
   cd smart-music-tagger
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create your configuration file**
   ```bash
   cp .env.example .env
   ```

4. **Edit `.env`** with your values (see [Configuration](#-configuration)):
   ```env
   GROQ_API_KEY=your_groq_api_key
   GROQ_API_URL=https://api.groq.com/openai/v1
   GROQ_MODEL=groq/compound-mini
   GROQ_REQUEST_DELAY_SECONDS=3
   MUSIC_DIRECTORY=C:/Users/YourName/Music
   ```

> ⚠️ **Keep `.env` private** — it contains your API key. It is already in `.gitignore`.


## 🚀 Usage

Pick a front-end. Both run the same pipeline and produce the same results.

| Mode | Command | Best for |
|------|---------|----------|
| 💻 **CLI** | `python cli_main.py` | Automation, scripts, servers, headless machines |
| 🌐 **Web GUI** | `python gui_main.py` | Interactive runs, visual progress, one-off batches |

### The pipeline (identical in both modes)

For every audio file in your music directory:

1. 🎯 **Analyze** the filename with AI → extract metadata
2. 🧹 **Clear** all existing tags from the file
3. ✍️ **Write** clean, verified metadata (title, artist, album, genre, year…)
4. 📝 **Rename** the file to `Artist - Song.ext`
5. 📒 **Log** the result

### 💻 CLI mode

Reads configuration from `.env` and runs the whole pipeline in the terminal:

```bash
python cli_main.py
```

Example output:

```
╔════════════════════════════════════════╗
║     SMART MUSIC TAGGER                 ║
║     AI-Powered Metadata Management     ║
╚════════════════════════════════════════╝

ℹ Info: Scanning directory: C:/Users/You/Music
  Files to Process: 3

[1/3] Processing:
  eminem_lose_yourself_320kbps.mp3
         ↓
  Eminem - Lose Yourself.mp3

  ✓ Artist: Eminem
  ✓ Album: 8 Mile
  ✓ Genre: Hip Hop
  ✓ Release Year: 2002

Processing Complete:
  Total Files:    3
  Successful:     3
  Failed:         0
  Success Rate:   100.0%
```

### 🌐 Web GUI mode (Flask)

A browser interface that takes configuration from a form and shows progress live.

```bash
python gui_main.py
```

Then open **<http://127.0.0.1:5000>** in your browser, fill in the form, and click **Start Tagging**.

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `127.0.0.1` | Bind address (use `0.0.0.0` only on a trusted LAN) |
| `--port` | `5000` | Bind port |
| `--debug` | off | Enable Flask debug/reload mode |

> 🔒 **Security:** the server binds to `127.0.0.1` (localhost only) by default.
> Your API key is sent only to start a job and is **never** stored, logged, or
> echoed back in any response. If a `.env` file exists, its non-secret fields
> are prefilled in the form as a convenience.

---

## ⚙️ Configuration

All settings live in a `.env` file (used by the CLI; the GUI takes the same
values from its form).

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `GROQ_API_KEY` | ✅ | — | Your Groq API key |
| `GROQ_API_URL` | ✅ | — | Groq API endpoint (`https://api.groq.com/openai/v1`) |
| `GROQ_MODEL` | ✅ | — | Model name (`groq/compound-mini`) |
| `GROQ_REQUEST_DELAY_SECONDS` | ❌ | `3` | Minimum delay between API requests |
| `MUSIC_DIRECTORY` | ✅ | — | Path to your music folder |

---

## 🎧 Supported Formats

| Format | Extension |
|--------|-----------|
| MP3 | `.mp3` |
| FLAC | `.flac` |
| WAV | `.wav` |
| M4A | `.m4a` |
| OGG | `.ogg` |

## 🏷️ Metadata Written

For each file, the AI extracts and writes:

- **Song name** (title)
- **Artist(s)** — supports multiple artists
- **Album**
- **Genre**
- **Release year**
- **Album artist** & **track number** (when available)

The AI cleans filenames by removing bitrate tags (`320kbps`), source/site
names, and labels like "Official Video" or "Lyrics" — then verifies the
metadata via web search only when needed, never guessing unknown fields.

---

## 🏗️ Architecture

Smart Music Tagger uses a **modular, layered design**. All business logic
lives in a single reusable service (`TaggerService`), which both front-ends
drive — so the CLI and GUI never duplicate logic.

```
       cli_main.py                gui_main.py
       (reads .env)               (web form)
            │                         │
            └────────────┬────────────┘
                         ▼
               TaggerService  ← core/service.py
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    FileScanner     FileProcessor    FileRenamer
                         │
                GroqClient (AI) + MetadataWriter
                         │
                     Logger → log file
```

**Key principle:** the core knows nothing about the CLI or GUI. Adding the
web GUI required **zero changes** to `cli/` or `core/` — it simply wires form
input into the same service and streams progress back via a callback.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full module breakdown.

### Project structure

```
smart-music-tagger/
├── cli_main.py             # CLI entry point
├── gui_main.py             # GUI entry point (Flask)
├── config/
│   └── config_loader.py    # .env loader (CLI)
├── core/                   # Shared business logic
│   ├── service.py          # TaggerService — orchestration
│   ├── scanner.py          # File scanning
│   ├── processor.py        # AI analysis + tag writing
│   └── renamer.py          # File renaming
├── ai/                     # Groq client + data models
├── metadata/               # Tag read/write (mutagen)
├── cli/                    # Rich terminal interface
├── gui/                    # Flask web app (SSE progress)
│   ├── app.py              # Flask app factory + routes
│   ├── runner.py           # Background job runner
│   ├── progress.py         # Thread-safe SSE event store
│   ├── templates/
│   └── static/
├── logs/                   # Generated log files
└── requirements.txt
```

---

## 📒 Logging

Every run writes a log file to `logs/music_tagger_YYYYMMDD_HHMMSS.log`,
recording:

- Original → new filename
- Extracted metadata
- Success/failure status
- Any errors encountered
- A final processing summary

---

## 🛠️ Troubleshooting

| Problem | Likely cause & fix |
|---------|--------------------|
| **"Configuration file not found"** | Create `.env`: `cp .env.example .env` |
| **"Missing required configuration"** | Fill in all required keys (see [Configuration](#-configuration)) |
| **"Music directory does not exist"** | Fix the `MUSIC_DIRECTORY` path |
| **API error `401 Unauthorized`** | Wrong or invalid `GROQ_API_KEY` |
| **"No audio files found"** | Directory has no MP3/FLAC/WAV/M4A/OGG files |
| **Rename fails** | Check write permissions / duplicate filenames |
| **GUI port already in use** | Run with `--port 5001` |

---

## 📄 License

Released under the **MIT License** — see [`LICENSE`](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please follow the existing modular architecture:
keep business logic in `core/`, and UI concerns in `cli/` or `gui/`.
