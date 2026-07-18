# Architecture Documentation

## Overview

Smart Music Tagger follows a **modular, layered architecture** designed to keep
business logic independent from the user interface. Both the CLI and the Web
GUI use the same processing pipeline, making the application easy to maintain,
test, and extend.

## Architecture

```text
┌──────────────────────────────┐
│        CLI / Web GUI         │
└──────────────┬───────────────┘
               │
     cli_main.py / gui_main.py
               │
               ▼
        TaggerService
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
FileScanner FileProcessor FileRenamer
               │
      GroqClient + MetadataWriter
               │
             Logger
```

---

## Components

### Entry Points

**Files**

- `cli_main.py`
- `gui_main.py`

The application's entry points. Their responsibilities are limited to:

- Loading configuration
- Creating the `TaggerService`
- Starting the processing pipeline
- Presenting results to the user

Neither entry point contains business logic.

---

### config/

Loads and validates configuration from the `.env` file for the CLI. The Web GUI
receives the same values from its configuration form.

---

### core/

Contains the application's core business logic.

#### TaggerService

The central orchestration layer shared by every front-end.

Pipeline:

```text
Scan files
      │
      ▼
Analyze filename
      │
      ▼
Clear metadata
      │
      ▼
Write metadata
      │
      ▼
Rename file
      │
      ▼
Log result
```

#### FileScanner

Scans a directory for supported audio files.

Supported formats:

- MP3
- FLAC
- WAV
- M4A
- OGG

#### FileProcessor

Processes each file by:

1. Sending the filename to the AI.
2. Clearing existing metadata.
3. Writing verified metadata.

#### FileRenamer

Renames processed files using the standard format:

```text
Artist - Song.ext
```

---

### ai/

Contains the Groq API client and shared metadata models.

Responsibilities:

- AI communication
- Response validation
- Metadata extraction

The AI returns structured metadata as JSON and only verifies information through
web search when necessary.

---

### metadata/

Handles all metadata operations using **Mutagen**.

Responsibilities:

- Read existing tags
- Remove old metadata
- Write clean metadata

---

### cli/

Terminal interface built with **Rich**.

Responsible only for displaying progress and results.

---

### gui/

Flask-based web interface.

Responsibilities:

- Collect configuration from the user
- Start processing jobs
- Stream progress updates
- Display results in the browser

---

### logs/

Creates human-readable log files for every execution.

---

## Data Flow

```text
CLI (.env)            Web GUI (Form)
      │                     │
      └──────────┬──────────┘
                 ▼
          TaggerService
                 │
          FileScanner
                 │
          FileProcessor
                 │
        GroqClient (AI)
                 │
        MetadataWriter
                 │
          FileRenamer
                 │
             Logger
                 │
      CLI Output / Web GUI
```

---

## Module Relationships

```text
cli_main.py
gui_main.py
        │
        ▼
 TaggerService
        │
 ┌──────┼───────────────┐
 ▼      ▼               ▼
core/  ai/         metadata/
        │
        ▼
      logs/
```

---

## Key Design Decisions

- A single processing engine shared by both front-ends.
- Complete separation between UI and business logic.
- Modular components with clear responsibilities.
- Easy integration of future interfaces without changing the core.
- Centralized logging for every processing run.

---

## Additional Documentation

For implementation details, see the source code inside:

- `core/`
- `ai/`
- `metadata/`
- `cli/`
- `gui/`