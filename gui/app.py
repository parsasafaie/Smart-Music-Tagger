"""Flask application factory for the Smart Music Tagger GUI.

The GUI is a thin layer over the shared ``TaggerService``: it collects
configuration from a web form, hands it to the service via
:class:`~gui.runner.JobManager`, and streams progress back to the browser via
Server-Sent Events. No CLI or core module is modified.

Security notes:
    - The app binds to ``127.0.0.1`` by default (see ``gui_main.py``) so it is
      only reachable from the local machine.
    - The API key is never persisted or echoed back in any response, template,
      or SSE event. It lives only in the in-memory job for the duration of the
      run.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Union

from flask import Flask, Response, jsonify, render_template, request

from config import ConfigLoader

from .progress import JobStore, event_stream
from .runner import JobManager

# Keys required in the run form. Used for fail-fast validation.
_REQUIRED_FIELDS = (
    ("groq_api_key", "API Key"),
    ("groq_api_url", "API URL"),
    ("groq_model", "Model"),
    ("music_directory", "Music Directory"),
)

_DEFAULT_PREFILL: Dict[str, str] = {
    "groq_api_url": "https://api.groq.com/openai/v1",
    "groq_model": "groq/compound-mini",
    "groq_request_delay_seconds": "5",
    "music_directory": "",
}


def _prefill_from_env() -> Dict[str, str]:
    """Best-effort form prefill from ``.env`` (never raises).

    The API key is intentionally NOT prefilled — it is never written into the
    served HTML.
    """
    try:
        config = ConfigLoader()
        return {
            "groq_api_url": config.get("groq_api_url")
            or _DEFAULT_PREFILL["groq_api_url"],
            "groq_model": config.get("groq_model")
            or _DEFAULT_PREFILL["groq_model"],
            "groq_request_delay_seconds": config.get(
                "groq_request_delay_seconds", "5"
            ),
            "music_directory": config.get("music_directory", ""),
        }
    except Exception:
        return dict(_DEFAULT_PREFILL)


def create_app(job_manager: Optional[JobManager] = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get(
        "FLASK_SECRET_KEY", "smart-music-tagger-dev"
    )
    manager = job_manager or JobManager()
    app.config["JOB_MANAGER"] = manager

    @app.route("/")
    def index() -> str:
        return render_template("index.html", prefill=_prefill_from_env())

    @app.route("/api/run", methods=["POST"])
    def run() -> Union[tuple[Any, int], Any]:
        data = request.get_json(silent=True) or {}
        values = {
            key: (data.get(key) or "").strip() for key, _ in _REQUIRED_FIELDS
        }
        delay_raw = (data.get("groq_request_delay_seconds") or "5").strip()

        missing = [
            label
            for key, label in _REQUIRED_FIELDS
            if not values[key]
        ]
        if missing:
            return (
                jsonify({"error": "Missing required fields: " + ", ".join(missing)}),
                400,
            )

        try:
            delay = float(delay_raw)
            if delay < 0:
                raise ValueError
        except ValueError:
            return (
                jsonify({"error": "Request delay must be a non-negative number."}),
                400,
            )

        try:
            job = manager.start_job(
                api_key=values["groq_api_key"],
                api_url=values["groq_api_url"],
                model=values["groq_model"],
                music_directory=values["music_directory"],
                request_delay_seconds=delay,
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify({"job_id": job.job_id})

    @app.route("/api/stream/<job_id>")
    def stream(job_id: str) -> Union[tuple[Any, int], Any]:
        job = manager.store.get(job_id)
        if job is None:
            return jsonify({"error": "Unknown job id."}), 404
        return Response(
            event_stream(job),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    @app.route("/api/health")
    def health() -> Any:
        return jsonify({"status": "ok"})

    return app
