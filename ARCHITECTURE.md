# Architecture Documentation

## Overview

Smart Music Tagger is built with a **modular, layered architecture** designed for:
- **Maintainability** - Clear separation of concerns
- **Testability** - Independent module testing
- **Extensibility** - Easy to add features without core changes
- **GUI-readiness** - Core logic independent from CLI
- **Scalability** - Support for batch operations and future APIs

## Architecture Layers

```
┌─────────────────────────────────────┐
│      User Interface Layer           │
│      (CLI Interface)                │
│      cli/interface.py               │
└──────────────┬──────────────────────┘
               │
┌──────────────┴──────────────────────┐
│    Application Logic Layer          │
│    (Orchestration & Control)        │
│    main.py                          │
└──────────────┬──────────────────────┘
               │
    ┌──────────┼──────────┬────────────┐
    ↓          ↓          ↓            ↓
┌──────┐  ┌─────────┐ ┌──────────┐ ┌─────────┐
│ Core │  │   AI    │ │ Metadata │ │ Config  │
│ Ops  │  │ Client  │ │  Tools   │ │ Manager │
└──────┘  └─────────┘ └──────────┘ └─────────┘
    │          │          │            │
┌───┴──┐   ┌───┴────┐  ┌─┴────┐   ┌──┴─────┐
│ core/│   │ ai/    │  │meta/ │   │config/  │
│      │   │        │  │      │   │         │
└──────┘   └────────┘  └──────┘   └─────────┘
    │
┌───┴──────────────────────────┐
│  Support Layers              │
│  utils/ - logging/           │
│  (Utilities & Logging)       │
└──────────────────────────────┘
```

## Module Breakdown

### 1. **main.py** - Entry Point
**Purpose**: Application orchestration

**Responsibilities**:
- Load configuration
- Initialize all components
- Coordinate processing workflow
- Display user feedback
- Handle errors gracefully

**Dependencies**: All other modules

```python
# Flow:
config → scanner → processor → renamer → logger → CLI
```

### 2. **config/** - Configuration Management
**Location**: `config/config_loader.py`

**Purpose**: Load and validate application settings from `.env` file

**Key Class**:
```python
ConfigLoader
├── __init__(env_file=".env")
├── validate()  # Check required fields
├── get(key, default)  # Get config value
└── get_all()  # Get all config
```

### 3. **core/** - Core Processing Logic

#### 3.0 **TaggerService** (`core/service.py`)
**Purpose**: Reusable orchestration layer — the single entry point shared by both the CLI and any future GUI.

All configuration is passed as constructor parameters (api_key, api_url, model, delay, music_directory), so the service never reads `.env` or any global state. Progress is reported through an optional ``on_progress(index, total, result, new_filename)`` callback.

```python
TaggerService (core/service.py)
├── __init__(api_key, api_url, model, request_delay_seconds, music_directory, logger=None)
├── scan()                # Returns (file_list, count)
├── process_all(on_progress=None)  # Runs the full pipeline, returns summary
└── _log(...)             # Writes to Logger if one is configured
```

**Pipeline**:
```
scan() → for each file: analyze → clear metadata → write metadata → rename → log → on_progress callback
```

This is the class a future Flask app will instantiate with form-provided config.

#### 3.1 **FileScanner** (`core/scanner.py`)
**Purpose**: Find audio files in directories

**Supports**: MP3, FLAC, WAV, M4A, OGG (non-recursive)

#### 3.2 **FileProcessor** (`core/processor.py`)
**Purpose**: Per-file AI analysis, metadata clearing, and metadata writing

**Workflow**:
```
File → AI Analysis → Clear All Metadata → Write Clean Metadata → Result
```

**Returns**:
```python
{
    'filepath': str,
    'filename': str,
    'success': bool,
    'metadata': MusicMetadata,
    'errors': [str]
}
```

#### 3.3 **FileRenamer** (`core/renamer.py`)
**Purpose**: Rename files to standard format (`Artist - Song.ext`)

### 4. **ai/** - AI Integration

**Purpose**: Groq API communication

**Key Classes**:
```python
MusicMetadata (ai/models.py)
├── song_name: str
├── artists: [str]
├── album: str
├── genre: str
├── release_year: str
├── album_artist: str (optional)
├── track_number: str (optional)
└── additional_metadata: dict

GroqClient (ai/groq_client.py)
├── __init__(api_key, api_url, model="groq/compound-mini", request_delay_seconds)
├── analyze_filename(filename)  # Main method
├── _call_api(prompt)  # API call
└── _parse_response(text)  # JSON parsing
```

**Prompt Design**:
- System: Clean the filename, verify metadata (web search only when needed), never guess, return JSON only
- User: The filename only (no schema template; the system prompt names the required fields)
- Model: `groq/compound-mini` (lightweight, with built-in web search for verification)

### 5. **metadata/** - Metadata Operations

#### 5.1 **MetadataReader** (`metadata/reader.py`)
**Purpose**: Read existing metadata from files

#### 5.2 **MetadataWriter** (`metadata/writer.py`)
**Purpose**: Write metadata to files (ID3, Vorbis, M4A tags)

### 6. **cli/** - User Interface
**Location**: `cli/interface.py`

**Purpose**: Beautiful terminal output using Rich library

### 7. **logs/** - Logging System
**Location**: `logs/logger.py`

**Purpose**: Human-readable log files in `logs/music_tagger_YYYYMMDD_HHMMSS.log`

### 8. **utils/** - Utility Functions
**Location**: `utils/helpers.py`

**Purpose**: Filename sanitization, format checking, artist formatting

## Data Flow

```
CLI mode:                   GUI mode (future):
  python main.py              Flask route
      ↓                           ↓
  Load .env (config/)         Form input (api_key, dir, delay)
      ↓                           ↓
      └──────────┬────────────────┘
                 ↓
         TaggerService (core/service.py)
         Config passed as constructor params
                 ↓
         scan() → process_all(on_progress=...)
                 ↓
    ┌────────────┼──────────────────┐
    ↓            ↓                  ↓
 FileScanner   FileProcessor    FileRenamer
    ↓            ↓                  ↓
         GroqClient (ai/)
         MetadataWriter (metadata/)
         Logger (logs/)
                 ↓
         on_progress callback
          ├─ CLI: print to terminal
          └─ GUI: update view / SSE stream
                 ↓
         Summary dict returned
```

## Dependency Management

### External Dependencies
```
requests     → ai/groq_client.py (API requests)
mutagen      → metadata/reader.py, metadata/writer.py
python-dotenv → config/config_loader.py
rich         → cli/interface.py
```

### Internal Dependencies
```
main.py → config/, core/TaggerService, cli/, logs/

core/service.py → core/scanner, core/processor, core/renamer, ai/, logs/
  (no CLI, no config dependency — fully GUI-agnostic)
core/processor.py → ai/, metadata/ (no CLI dependency)
ai/groq_client.py → standalone (requests only)
cli/interface.py  → standalone (no core logic dependency)
```

## Extensibility Points

### Adding New Features

#### 1. **New Audio Format**
Extend `metadata/writer.py` and `utils/helpers.py`

#### 2. **Alternative AI Provider**
Add a new client in `ai/` implementing the same `analyze_filename()` interface

#### 3. **GUI Implementation**
Create `gui/interface.py` using the same core modules

#### 4. **REST API**
Create `api/routes.py` using the same core modules

## Design Principles

1. **Separation of Concerns** - Each module has a single responsibility
2. **Dependency Injection** - Components receive dependencies as parameters
3. **Fail-Fast Validation** - Check preconditions early
4. **Graceful Degradation** - Continue processing if individual files fail

## Summary

Smart Music Tagger's architecture provides:

- Clean separation between modules
- Easy testing and extension
- GUI-ready core logic
- Production-quality error handling and logging
