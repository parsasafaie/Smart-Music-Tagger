"""Background runner that drives ``TaggerService`` from GUI form input.

This is the GUI's counterpart to ``main._run_cli``: it builds a
:class:`~core.service.TaggerService` from user-provided configuration and runs
the pipeline in a background thread, bridging the service's ``on_progress``
callback into a :class:`~gui.progress.Job` for live SSE streaming.

The service — and therefore this runner — never reads ``.env`` or any global
state; all configuration comes in as constructor parameters.
"""

from __future__ import annotations

import threading
import traceback
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from core import TaggerService
from logs import Logger

from .progress import Job, JobStore


class JobManager:
    """Creates jobs and runs ``TaggerService`` in background threads."""

    def __init__(self, job_store: Optional[JobStore] = None) -> None:
        self.store = job_store or JobStore()

    def start_job(
        self,
        api_key: str,
        api_url: str,
        model: str,
        music_directory: str,
        request_delay_seconds: float,
    ) -> Job:
        """Validate inputs, create a Job, and launch the processing thread.

        Raises:
            ValueError: If the music directory does not exist.
        """
        music_dir = Path(music_directory)
        if not music_dir.exists() or not music_dir.is_dir():
            raise ValueError(f"Music directory does not exist: {music_directory}")

        job = Job(
            job_id=uuid.uuid4().hex[:12],
            music_directory=str(music_dir),
            model=model,
            status="running",
        )
        self.store.add(job)

        thread = threading.Thread(
            target=self._run,
            args=(
                job,
                api_key,
                api_url,
                model,
                str(music_dir),
                request_delay_seconds,
            ),
            daemon=True,
        )
        thread.start()
        return job

    def _run(
        self,
        job: Job,
        api_key: str,
        api_url: str,
        model: str,
        music_directory: str,
        request_delay_seconds: float,
    ) -> None:
        """Worker: instantiate the service and run the full pipeline."""
        try:
            logger = Logger()
            service = TaggerService(
                api_key=api_key,
                api_url=api_url,
                model=model,
                request_delay_seconds=request_delay_seconds,
                music_directory=music_directory,
                logger=logger,
            )

            # Pre-scan for immediate "found N files" feedback before the
            # (rate-limited) processing loop starts producing progress events.
            _, file_count = service.scan()
            job.file_count = file_count
            job.add_event(
                {
                    "type": "started",
                    "music_directory": music_directory,
                    "model": model,
                    "file_count": file_count,
                }
            )

            def on_progress(
                index: int,
                total: int,
                result: Dict[str, Any],
                new_filename: str,
            ) -> None:
                metadata = result.get("metadata")
                job.add_event(
                    {
                        "type": "progress",
                        "index": index,
                        "total": total,
                        "filename": result.get("filename", ""),
                        "new_filename": new_filename,
                        "success": bool(result.get("success")),
                        "metadata": metadata.to_dict()
                        if metadata is not None
                        else None,
                        "errors": result.get("errors", []),
                    }
                )

            summary = service.process_all(on_progress=on_progress)
            if summary.get("log_file"):
                summary["log_file"] = str(summary["log_file"])
            job.finish(summary=summary)
        except Exception as exc:  # noqa: BLE001 — surface any failure to the UI
            job.finish(
                error=f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
            )
