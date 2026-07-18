"""Thread-safe job registry and SSE event streaming for the Flask GUI.

The GUI runs ``TaggerService.process_all`` in a background thread. That thread
reports progress via the service's ``on_progress`` callback, which appends
events to a :class:`Job`. Browser clients subscribe through Server-Sent Events
(SSE) using :func:`event_stream`, which replays buffered events then tails the
job live until it finishes.

Multiple browser tabs can subscribe to the same job — events are buffered on
the Job and each SSE stream tracks its own cursor, so a late subscriber still
sees the full history.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# Polling interval (seconds) used by the SSE tail loop when waiting for new
# events. Small enough to feel live, large enough to avoid busy-spinning.
_SSE_POLL_INTERVAL = 0.2


@dataclass
class Job:
    """A single tagging run: its status, buffered events, and final result."""

    job_id: str
    music_directory: str = ""
    model: str = ""
    # queued | running | done | failed
    status: str = "queued"
    file_count: int = 0
    events: List[Dict[str, Any]] = field(default_factory=list)
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    final: bool = False
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def add_event(self, event: Dict[str, Any]) -> None:
        """Append a progress event (thread-safe)."""
        with self._lock:
            self.events.append(event)

    def finish(
        self,
        summary: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """Mark the job as finished (thread-safe)."""
        with self._lock:
            if error is not None:
                self.status = "failed"
                self.error = error
            else:
                self.status = "done"
            self.summary = summary
            self.final = True

    def snapshot(self, since: int) -> Tuple[List[Dict[str, Any]], bool, str]:
        """Return events from index ``since`` plus the final/status flags."""
        with self._lock:
            new_events = self.events[since:]
            return list(new_events), self.final, self.status


class JobStore:
    """In-memory registry of jobs keyed by job_id."""

    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()

    def add(self, job: Job) -> None:
        with self._lock:
            self._jobs[job.job_id] = job

    def get(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def __contains__(self, job_id: str) -> bool:  # pragma: no cover - trivial
        with self._lock:
            return job_id in self._jobs


def format_sse(event_type: str, data: Any) -> str:
    """Format a single SSE message block."""
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event_type}\ndata: {payload}\n\n"


def event_stream(job: Job):
    """Generator yielding SSE messages, tailing the job until it finalizes.

    Replays any events already buffered, then tails new events until the job
    is marked final, at which point a terminal ``done``/``failed`` event is
    yielded and the stream closes.
    """
    cursor = 0
    while True:
        events, final, status = job.snapshot(cursor)
        cursor += len(events)
        for event in events:
            yield format_sse(event.get("type", "message"), event)

        if final:
            yield format_sse(
                status,
                {"status": status, "summary": job.summary, "error": job.error},
            )
            return

        time.sleep(_SSE_POLL_INTERVAL)
