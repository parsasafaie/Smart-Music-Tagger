#!/usr/bin/env python3
"""Smart Music Tagger - GUI entry point.

Launches the Flask web GUI. The CLI (``cli_main.py``) is unaffected and remains
the default for non-interactive / automated use.

Usage:
    python gui_main.py [--host HOST] [--port PORT]

By default the server binds to 127.0.0.1 so it is only reachable from your
machine. Pass ``--host 0.0.0.0`` to expose it on your LAN (do this only on a
trusted network).
"""

import argparse
import os
import sys

# Windows UTF-8 hint (mirrors cli_main.py); Flask handles request encoding,
# but this keeps console output predictable for non-ASCII filenames in logs.
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from gui import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="Smart Music Tagger — Flask GUI")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=5000, help="Bind port (default: 5000)"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable Flask debug/reload mode"
    )
    args = parser.parse_args()

    app = create_app()
    print("=" * 52)
    print("  SMART MUSIC TAGGER — Flask GUI")
    print("=" * 52)
    print(f"  Open in your browser: http://{args.host}:{args.port}")
    print("  Press CTRL+C to stop.")
    print("=" * 52)

    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)


if __name__ == "__main__":
    main()
